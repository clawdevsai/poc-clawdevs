#!/usr/bin/env python3
"""
Orquestrador autonomia — Autonomia nível 4: five strikes, orçamento de degradação, digest (referência).
Lê estado no Redis (contagens de 5º strike e aprovação por omissão cosmética), aplica regras
do doc 43 e 06-operacoes: ao atingir 10–15% das tarefas do sprint na rota de fuga, emite
evento de pré-freio (loop de consenso) ou pause. Gera digest e relatório de degradação (Fase 3).
Ref: docs/43-autonomia-nivel-4-matriz-escalonamento.md, docs/06-operacoes.md
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
# Chaves de estado (orquestrador)
KEY_FIVE_STRIKES = f"{KEY_PREFIX}:orchestrator:five_strikes_count"
KEY_OMISSION_COUNT = f"{KEY_PREFIX}:orchestrator:omission_cosmetic_count"
KEY_SPRINT_TASKS = f"{KEY_PREFIX}:orchestrator:sprint_task_count"
KEY_PAUSE_DEGRADATION = "orchestration:pause_degradation"
STREAM_DIGEST = os.environ.get("STREAM_DIGEST", "digest:daily")
DEGRADATION_THRESHOLD_PCT = float(os.environ.get("DEGRADATION_THRESHOLD_PCT", "12.0"))
INTERVAL_SEC = int(os.environ.get("ORCHESTRATOR_INTERVAL_SEC", "60"))
DEGRADATION_REPORT_DIR = os.environ.get("DEGRADATION_REPORT_DIR", "docs/agents-devs")


def get_redis():
    try:
        import redis
        return redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
    except ImportError:
        raise RuntimeError("Instale redis: pip install redis")


def get_int(r, key, default=0):
    val = r.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


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
    if pct >= DEGRADATION_THRESHOLD_PCT:
        r.set(KEY_PAUSE_DEGRADATION, "1", ex=86400)
        r.xadd(
            STREAM_DIGEST,
            {
                "type": "degradation_threshold",
                "pct": str(round(pct, 1)),
                "five_strikes": str(five),
                "omission_cosmetic": str(omission),
                "sprint_tasks": str(sprint_total),
            },
        )
        try:
            write_degradation_report(five, omission, sprint_total, pct)
        except Exception as e:
            print(f"[orchestrator] Falha ao escrever relatório de degradação: {e}", file=sys.stderr)
        print(f"[orchestrator] Orçamento degradação atingido: {pct:.1f}% — pause e digest emitido.")
    else:
        r.delete(KEY_PAUSE_DEGRADATION)


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
