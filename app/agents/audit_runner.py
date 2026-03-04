#!/usr/bin/env python3
"""
Audit trigger: consome audit:queue, envia a cada papel (QA, DBA, Security, UX) ao OpenClaw.
Cada agente (no Gateway) executa sua auditoria e pode criar Issue no GitHub; estado Monitoring/Done.
Sem LLM neste script (openclaw-first).
Ref: docs/38-redis-streams-estado-global.md, docs/agents-devs/state-machine-issues.md,
     .cursor/rules/openclaw-first.mdc
"""
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gpu_lock import get_redis

try:
    from issue_state import set_issue_state, STATE_MONITORING
except ImportError:
    def set_issue_state(r, issue_id: str, state: str, ttl_sec=None) -> bool:
        r.set(f"project:v1:issue:{issue_id}:state", state)
        return True
    STATE_MONITORING = "Monitoring"

try:
    from openclaw_gateway_call import send_to_session
except ImportError:
    def send_to_session(session_key, message, timeout_sec=0):
        return False, "openclaw_gateway_call não disponível"

STREAM_AUDIT = os.getenv("STREAM_AUDIT_QUEUE", "audit:queue")
GROUP = os.getenv("AUDIT_GROUP", "clawdevs")
CONSUMER = os.getenv("POD_NAME", os.getenv("HOSTNAME", "audit-runner-1"))
BLOCK_MS = int(os.getenv("AUDIT_BLOCK_MS", "5000"))
AUDIT_ROLES = ["qa", "dba", "security", "ux"]
GITHUB_REPO = os.getenv("GITHUB_REPO", os.getenv("GH_REPO", ""))


def _session_key(role: str) -> str:
    # security -> cybersec no OpenClaw
    if role == "security":
        return os.getenv("OPENCLAW_CYBERSEC_SESSION_KEY", "agent:cybersec:main")
    return os.getenv(f"OPENCLAW_{role.upper()}_SESSION_KEY", f"agent:{role}:main")


def _payload_to_dict(data) -> dict:
    if isinstance(data, dict):
        return {k: (v.decode() if isinstance(v, bytes) else v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        out = {}
        for i in range(0, len(data) - 1, 2):
            k, v = data[i], data[i + 1]
            if isinstance(k, bytes):
                k = k.decode()
            if isinstance(v, bytes):
                v = v.decode()
            out[k] = v
        return out
    return {}


def process_audit(r, msg_id: str, payload: dict) -> None:
    repo = (payload.get("repo") or GITHUB_REPO or "").strip()
    scope = (payload.get("scope") or "default").strip()
    issue_id = (payload.get("issue_id") or "").strip()
    message_base = f"""Auditoria periódica (audit:queue). Execute sua auditoria para o repo e escopo; se encontrar bug/melhoria, crie Issue no GitHub. Escopo: {scope}. Repo: {repo or '(não informado)'}. issue_id (se houver): {issue_id}.
"""
    for role in AUDIT_ROLES:
        session_key = _session_key(role)
        ok, _ = send_to_session(session_key, message_base + f"\nPapel: {role}.", timeout_sec=0)
        if not ok:
            print(f"  [Audit] Falha ao enviar para {role}: session={session_key}", file=sys.stderr)
    if issue_id:
        set_issue_state(r, issue_id, STATE_MONITORING)
    r.xack(STREAM_AUDIT, GROUP, msg_id)
    print(f"[Audit] XACK {msg_id} (enviado aos agentes QA, DBA, Security, UX)")


def main() -> None:
    r = get_redis()
    print(f"[Audit] Consumindo stream={STREAM_AUDIT} group={GROUP} consumer={CONSUMER} (openclaw-first)")

    while True:
        try:
            reply = r.xreadgroup(GROUP, CONSUMER, {STREAM_AUDIT: ">"}, block=BLOCK_MS, count=1)
        except Exception as e:
            print(f"[Audit] Erro: {e}", file=sys.stderr)
            time.sleep(5)
            continue
        if not reply:
            continue
        for stream, messages in reply:
            stream = stream.decode() if isinstance(stream, bytes) else stream
            for msg_id, data in messages:
                msg_id = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                payload = _payload_to_dict(data or {})
                try:
                    process_audit(r, msg_id, payload)
                except Exception as e:
                    print(f"[Audit] Erro {msg_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
