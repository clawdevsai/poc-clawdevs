#!/usr/bin/env python3
"""
Subfluxo do loop de consenso (Fase 3 — 034).
Quando KEY_CONSENSUS_IN_PROGRESS está setada: carrega o relatório de degradação,
chama QA+Architect para propor ajuste, executa tarefa piloto (uma de code:ready) e define resultado.
Pode ser executado por CronJob (ex.: a cada 2 min) ou uma vez.
Uso: consensus_loop_runner.py [--once]
Ref: docs/06-operacoes.md (Loop de consenso automatizado)
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration_phase3 import (
    get_redis,
    KEY_CONSENSUS_IN_PROGRESS,
    KEY_CONSENSUS_PROPOSAL,
    DEGRADATION_REPORT_DIR,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
OLLAMA_BASE_URL = (os.environ.get("OLLAMA_BASE_URL") or "").strip().rstrip("/")
ARCHITECT_MODEL = os.environ.get("ARCHITECT_MODEL", "glm-5:cloud")
CONSENSUS_LLM_TIMEOUT = int(os.environ.get("CONSENSUS_LLM_TIMEOUT_SEC", "90"))
STREAM_CODE_READY = os.environ.get("STREAM_CODE_READY", "code:ready")


def _latest_report_path() -> Path | None:
    report_dir = Path(os.environ.get("DEGRADATION_REPORT_DIR", DEGRADATION_REPORT_DIR))
    if not report_dir.exists():
        return None
    reports = sorted(report_dir.glob("degradation-report-*.md"), reverse=True)
    return reports[0] if reports else None


def _get_issue_context(r, issue_id: str, max_chars: int = 4000) -> str:
    if not issue_id:
        return ""
    key = f"{KEY_PREFIX}:issue:{issue_id}"
    try:
        raw = r.get(key)
        if raw is None:
            return ""
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        return (raw[:max_chars] + "…") if len(raw) > max_chars else raw
    except Exception:
        return ""


def _call_ollama(messages: list, timeout: int = CONSENSUS_LLM_TIMEOUT) -> str:
    if not OLLAMA_BASE_URL:
        return ""
    body = {"model": ARCHITECT_MODEL, "messages": messages, "stream": False}
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return ((data.get("message") or {}).get("content") or "").strip()
    except Exception:
        return ""


def _run_qa_architect_proposal(r, report_text: str) -> str:
    """QA + Architect propõem ajuste com base no relatório de degradação. Retorna proposta ou vazio."""
    if not report_text or not OLLAMA_BASE_URL:
        return ""
    system = """Você atua como QA e Architect em consenso. Recebeu um relatório de degradação da esteira (muitas tarefas na rota de fuga: 5º strike ou aprovação por omissão cosmética).
Proponha ajustes CONCRETOS e breves: (1) critérios de aceite do PO a relaxar temporariamente; (2) fitness do Architect a ajustar (ex.: priorizar aprovar se seguro).
Responda em um único parágrafo objetivo (máx. 300 palavras)."""
    user = f"Relatório de degradação:\n{report_text[:6000]}\n\nProposta de ajuste (PO + Architect):"
    content = _call_ollama([{"role": "system", "content": system}, {"role": "user", "content": user}])
    if content:
        try:
            r.set(KEY_CONSENSUS_PROPOSAL, content, ex=3600)
        except Exception:
            pass
    return content


def _pilot_architect_review(r, issue_id: str, payload: dict) -> bool:
    """Revisão Architect em modo PILOT (mais leniente). Retorna True se aprovado."""
    if not OLLAMA_BASE_URL:
        return False
    issue_ctx = _get_issue_context(r, issue_id)
    branch = payload.get("branch", "")
    title = payload.get("title", "")

    system = """Você é o Architect. MODO PILOT: a esteira está em loop de consenso pós-degradação.
Prefira APROVAR se o código for seguro e funcional, mesmo que não ideal (evite rejeição por detalhes).
Responda em uma linha: APPROVED ou REJECTED: razão."""

    user = f"Issue {issue_id}. Branch: {branch}. Título: {title}.\n\nContexto:\n{issue_ctx or '(nenhum)'}\n\nRevisão (modo pilot): aprove ou rejeite em uma linha."

    content = _call_ollama([{"role": "system", "content": system}, {"role": "user", "content": user}])
    content_upper = (content or "").upper()
    return "REJECTED" not in content_upper and "REJEITADO" not in content_upper and "APPROVED" in content_upper


def _run_pilot(r) -> str:
    """
    Pilot real: pega uma mensagem de code:ready (XRANGE peek), roda revisão Architect em modo pilot.
    Retorna "success" ou "fail".
    """
    if os.environ.get("CONSENSUS_PILOT_AUTO_SUCCESS", "").strip().lower() in ("1", "true", "yes"):
        return "success"
    if not OLLAMA_BASE_URL:
        return "fail"
    try:
        # Peek: mensagem mais antiga (não consome)
        entries = r.xrange(STREAM_CODE_READY, min="-", max="+", count=1)
        if not entries:
            return "fail"
        msg_id, raw = entries[0]
        payload = raw if isinstance(raw, dict) else dict(zip((raw or [])[::2], (raw or [])[1::2]))
        issue_id = (payload.get("issue_id") or payload.get("issue") or payload.get("task_id") or "").strip()
        if not issue_id:
            return "fail"
        approved = _pilot_architect_review(r, issue_id, payload)
        return "success" if approved else "fail"
    except Exception as e:
        print(f"[consensus_loop_runner] Pilot erro: {e}", file=sys.stderr)
        return "fail"


def run_once(r) -> bool:
    """Retorna True se executou o subfluxo (consensus estava ativo)."""
    if not r.get(KEY_CONSENSUS_IN_PROGRESS):
        return False
    report_path = _latest_report_path()
    report_text = ""
    if report_path:
        report_text = report_path.read_text(encoding="utf-8")
        proposal = _run_qa_architect_proposal(r, report_text)
        if proposal:
            print(f"[consensus_loop_runner] Proposta QA+Architect: {proposal[:200]}…")
    try:
        from slack_notify import send_slack
        send_slack(
            "*ClawDevs — Loop de consenso*\n"
            "Subfluxo em execução (relatório carregado, proposta QA+Architect gerada). Executando pilot."
        )
    except Exception:
        pass
    result = _run_pilot(r)
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
