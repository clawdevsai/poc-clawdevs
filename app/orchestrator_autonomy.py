#!/usr/bin/env python3
"""
Orquestrador autonomia — Autonomia nível 4: five strikes, orçamento de degradação,
loop de consenso (pré-freio), digest (Fase 3).
Ao atingir 10–15% na rota de fuga: primeiro emite evento de loop de consenso (QA+Architect);
só aciona freio de mão se o pilot falhar ou não houver resultado no timeout.
Ref: docs/06-operacoes.md, docs/issues/034.
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Importar chaves e helpers Fase 3 (strikes, consenso, digest)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration import (
    get_redis,
    get_int,
    KEY_FIVE_STRIKES,
    KEY_OMISSION_COUNT,
    KEY_SPRINT_TASKS,
    KEY_PAUSE_DEGRADATION,
    KEY_CONSENSUS_IN_PROGRESS,
    KEY_CONSENSUS_PILOT_RESULT,
    STREAM_DIGEST,
    emit_digest,
    emit_event,
)

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
DEGRADATION_THRESHOLD_PCT = float(os.environ.get("DEGRADATION_THRESHOLD_PCT", "12.0"))
CONSENSUS_LOOP_TIMEOUT_SEC = int(os.environ.get("CONSENSUS_LOOP_TIMEOUT_SEC", "3600"))  # 1h
INTERVAL_SEC = int(os.environ.get("ORCHESTRATOR_INTERVAL_SEC", "60"))
DEGRADATION_REPORT_DIR = os.environ.get("DEGRADATION_REPORT_DIR", "docs/agents-devs")


def write_degradation_report(five: int, omission: int, sprint_total: int, pct: float) -> None:
    """Gera relatório em Markdown para o Diretor (Fase 3 — 017)."""
    report_dir = Path(DEGRADATION_REPORT_DIR)
    report_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    report_path = report_dir / f"degradation-report-{date_str}.md"
    body = f"""# Relatório de degradação — {date_str}

**Esteira pausada por orçamento de degradação.** Retomada somente após revisão do Diretor e comando explícito: `./scripts/unblock-degradation.sh`.

## Sumário

- **Tarefas na rota de fuga (5º strike + aprovação por omissão cosmética):** {five + omission}
- **Total de tarefas do sprint:** {sprint_total}
- **Percentual na rota de fuga:** {pct:.1f}%
- **5º strike (abandono após impasse):** {five}
- **Aprovação por omissão cosmética:** {omission}

## Ação recomendada

1. Revisar **MEMORY.md** e este relatório.
2. Ajustar limiares ou critérios no arquivo de configuração (Gateway/agentes) se necessário.
3. Executar `./scripts/unblock-degradation.sh` para autorizar a retomada da esteira.

Ref: docs/06-operacoes.md (Workflow de recuperação pós-degradação).
"""
    report_path.write_text(body, encoding="utf-8")
    print(f"[orchestrator] Relatório de degradação escrito: {report_path}")


def run_once(r) -> None:
    five = get_int(r, KEY_FIVE_STRIKES)
    omission = get_int(r, KEY_OMISSION_COUNT)
    sprint_total = get_int(r, KEY_SPRINT_TASKS, default=1)
    route_fuge = five + omission
    if sprint_total <= 0:
        return
    pct = 100.0 * route_fuge / sprint_total

    if pct < DEGRADATION_THRESHOLD_PCT:
        r.delete(KEY_PAUSE_DEGRADATION)
        return

    # Limiar atingido — loop de consenso (034) antes do freio de mão
    consensus_in_progress = r.get(KEY_CONSENSUS_IN_PROGRESS)
    pilot_result = (r.get(KEY_CONSENSUS_PILOT_RESULT) or "").strip().lower()

    if pilot_result == "success":
        r.delete(KEY_CONSENSUS_IN_PROGRESS)
        r.delete(KEY_CONSENSUS_PILOT_RESULT)
        r.delete(KEY_PAUSE_DEGRADATION)
        emit_digest(r, "consensus_pilot_success", pct=str(round(pct, 1)))
        print("[orchestrator] Loop de consenso: pilot sucesso — esteira segue sem pausar.")
        return

    if pilot_result == "fail" or (consensus_in_progress and _consensus_timed_out(r)):
        r.delete(KEY_CONSENSUS_IN_PROGRESS)
        r.delete(KEY_CONSENSUS_PILOT_RESULT)
        r.set(KEY_PAUSE_DEGRADATION, "1", ex=86400)
        emit_digest(
            r,
            "degradation_threshold",
            pct=str(round(pct, 1)),
            five_strikes=str(five),
            omission_cosmetic=str(omission),
            sprint_tasks=str(sprint_total),
        )
        try:
            write_degradation_report(five, omission, sprint_total, pct)
        except Exception as e:
            print(f"[orchestrator] Falha ao escrever relatório de degradação: {e}", file=sys.stderr)
        # Alerta imediato via Slack (Fase 3)
        try:
            import subprocess
            msg = (
                f"*ClawDevs — Freio de mão acionado*\n"
                f"Orçamento de degradação atingido: {pct:.1f}% "
                f"(5º strike: {five}, omissão cosmética: {omission}, sprint: {sprint_total}). "
                f"Esteira pausada. Revisar relatório e executar unblock-degradation.sh para retomar."
            )
            env = dict(os.environ)
            env.setdefault("SLACK_ENV_PREFIX", "ORCHESTRATOR_")
            subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "slack_notify.py"), msg],
                env=env,
                timeout=10,
                capture_output=True,
            )
        except Exception as e:
            print(f"[orchestrator] Falha ao enviar alerta Slack: {e}", file=sys.stderr)
        print(f"[orchestrator] Orçamento degradação: loop falhou ou timeout — freio de mão acionado ({pct:.1f}%).")
        return

    if not consensus_in_progress:
        # Primeira vez no limiar: acionar loop de consenso (QA + Architect)
        r.set(KEY_CONSENSUS_IN_PROGRESS, "1", ex=CONSENSUS_LOOP_TIMEOUT_SEC)
        r.set(f"{KEY_CONSENSUS_IN_PROGRESS}:started_at", str(time.time()), ex=CONSENSUS_LOOP_TIMEOUT_SEC)
        emit_digest(
            r,
            "consensus_loop_requested",
            pct=str(round(pct, 1)),
            five_strikes=str(five),
            omission_cosmetic=str(omission),
            sprint_tasks=str(sprint_total),
        )
        emit_event(
            r,
            "consensus_loop_requested",
            pct=str(round(pct, 1)),
            five_strikes=str(five),
            omission_cosmetic=str(omission),
            sprint_tasks=str(sprint_total),
        )
        print(f"[orchestrator] Limiar {pct:.1f}% atingido — loop de consenso (pré-freio) acionado; aguardando pilot.")
    # Se já em consenso e sem resultado ainda, não pausar; aguardar próximo ciclo.
    return


def _consensus_timed_out(r) -> bool:
    started = r.get(f"{KEY_CONSENSUS_IN_PROGRESS}:started_at")
    if not started:
        return True
    try:
        return (time.time() - float(started)) >= CONSENSUS_LOOP_TIMEOUT_SEC
    except (ValueError, TypeError):
        return True


def main() -> None:
    r = get_redis()
    print(
        f"[orchestrator] Autonomia: threshold={DEGRADATION_THRESHOLD_PCT}% interval={INTERVAL_SEC}s"
    )
    while True:
        try:
            run_once(r)
        except Exception as e:
            print(f"[orchestrator] Erro: {e}", file=sys.stderr)
        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()
