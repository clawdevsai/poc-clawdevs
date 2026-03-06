#!/usr/bin/env python3
"""
032: Fallback Architect no 2º strike (openclaw-first).
Envia ao agente Architect no OpenClaw prompt de compromisso: gerar código/patch que tornaria o PR aprovável.
O Architect (no Gateway) grava resultado em Redis (project:v1:issue:{id}:architect_fallback_patch) via ferramentas.
Ref: docs/issues/032-five-strikes-fallback-arbitragem.md, .cursor/rules/openclaw-first.mdc
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from orchestration import get_redis, architect_fallback_patch_key

try:
    from slack_notify import send_slack
except ImportError:
    def send_slack(*a, **k):
        pass

try:
    from openclaw_gateway_call import send_to_session
except ImportError:
    def send_to_session(session_key, message, timeout_sec=0):
        return False, "openclaw_gateway_call não disponível"

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
ARCHITECT_SESSION_KEY = os.getenv("OPENCLAW_ARCHITECT_SESSION_KEY", "agent:architect:main")


def _get_issue_context(r, issue_id: str, max_chars: int = 6000) -> str:
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


def run_fallback(r, issue_id: str, rejection_reason: str = "", branch: str = "", title: str = "") -> str | None:
    """
    Envia ao Architect (OpenClaw) prompt de compromisso. O agente gera patch e grava em Redis
    em architect_fallback_patch_key(issue_id). Retorna None (resultado fica no Redis).
    """
    issue_ctx = _get_issue_context(r, issue_id)
    reason = (rejection_reason or "Rejeição pelo Architect (razão não informada).").strip()[:500]
    key = architect_fallback_patch_key(issue_id)

    message = f"""Fallback Architect (2º strike). Esta tarefa recebeu 2 rejeições no code review.
Gere o código ou patch (unified diff) MÍNIMO que tornaria este PR aprovável. Respeite SOLID, testes e ADRs.
Grave o resultado em Redis na chave: {key} (TTL 7 dias). Output apenas código/diff.

Issue id: {issue_id}. Branch: {branch or '(não informada)'}. Título: {title or '(vazio)'}.
Motivo da última rejeição: {reason}

Contexto da issue:
{issue_ctx or '(nenhum contexto no Redis)'}
"""
    ok, out = send_to_session(ARCHITECT_SESSION_KEY, message, timeout_sec=0)
    if not ok:
        print(f"[architect_fallback] Falha ao enviar ao Gateway: {out}", file=sys.stderr)
        return None
    try:
        send_slack(
            f"*ClawDevs — Fallback Architect (2º strike)*\nIssue `{issue_id}`: enviado ao agente Architect. Ver Redis key `{key}`.",
            env_prefix="ORCHESTRATOR_",
        )
    except Exception:
        pass
    return None


def main():
    if len(sys.argv) < 2:
        print("Uso: architect_fallback.py <issue_id> [rejection_reason]", file=sys.stderr)
        sys.exit(1)
    issue_id = sys.argv[1].strip()
    reason = " ".join(sys.argv[2:]).strip() if len(sys.argv) > 2 else ""
    r = get_redis()
    run_fallback(r, issue_id, rejection_reason=reason)
    sys.exit(0)


if __name__ == "__main__":
    main()
