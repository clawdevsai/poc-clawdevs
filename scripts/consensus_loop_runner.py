#!/usr/bin/env python3
"""
Subfluxo do loop de consenso (Fase 3 — 034).
Quando KEY_CONSENSUS_IN_PROGRESS está setada: carrega o relatório de degradação,
opcionalmente notifica Slack, executa tarefa piloto e define resultado via set_consensus_pilot_result.
Pode ser executado por CronJob (ex.: a cada 2 min) ou uma vez.
Uso: consensus_loop_runner.py [--once]
Ref: docs/06-operacoes.md (Loop de consenso automatizado)
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration_phase3 import (
    get_redis,
    KEY_CONSENSUS_IN_PROGRESS,
    DEGRADATION_REPORT_DIR,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _latest_report_path() -> Path | None:
    report_dir = Path(os.environ.get("DEGRADATION_REPORT_DIR", DEGRADATION_REPORT_DIR))
    if not report_dir.exists():
        return None
    reports = sorted(report_dir.glob("degradation-report-*.md"), reverse=True)
    return reports[0] if reports else None


def _run_pilot() -> str:
    """
    Executa a tarefa piloto (uma tarefa determinística da fila).
    Por enquanto: stub que usa CONSENSUS_PILOT_AUTO_SUCCESS para success/fail.
    Futuro: rodar slot com uma tarefa de code:ready e inferir resultado.
    """
    if os.environ.get("CONSENSUS_PILOT_AUTO_SUCCESS", "").strip().lower() in ("1", "true", "yes"):
        return "success"
    return "fail"


def run_once(r) -> bool:
    """Retorna True se executou o subfluxo (consensus estava ativo)."""
    if not r.get(KEY_CONSENSUS_IN_PROGRESS):
        return False
    report_path = _latest_report_path()
    if report_path:
        # Carregar relatório (contexto para QA/Architect em versão futura)
        report_path.read_text(encoding="utf-8")
    # Notificar Slack (opcional)
    try:
        from slack_notify import send_slack
        send_slack(
            "*ClawDevs — Loop de consenso*\n"
            "Subfluxo em execução (relatório de degradação carregado). "
            "Aguardando resultado do pilot."
        )
    except Exception:
        pass
    result = _run_pilot()
    subprocess.run(
        [sys.executable, os.path.join(SCRIPT_DIR, "set_consensus_pilot_result.py"), result],
        env=os.environ,
        cwd=os.path.dirname(SCRIPT_DIR) or ".",
        timeout=30,
    )
    return True


def main():
    parser = argparse.ArgumentParser(description="Subfluxo loop de consenso (Fase 3)")
    parser.add_argument("--once", action="store_true", help="Executa uma vez e sai")
    args = parser.parse_args()
    r = get_redis()
    if args.once:
        run_once(r)
        return
    # Loop com intervalo (para uso como processo contínuo)
    import time
    interval = int(os.environ.get("CONSENSUS_LOOP_RUNNER_INTERVAL_SEC", "120"))
    while True:
        try:
            run_once(r)
        except Exception as e:
            print(f"[consensus_loop_runner] Erro: {e}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
