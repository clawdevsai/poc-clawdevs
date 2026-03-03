#!/usr/bin/env python3
"""
DevOps trigger: consome event:devops (após merge), envia ao agente DevOps no OpenClaw.
O agente DevOps (no Gateway) atualiza estado Deployed, dispara pipeline se necessário,
e emite feature_complete em orchestrator:events via ferramentas. Sem LLM neste script (openclaw-first).
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
    from openclaw_gateway_call import send_to_session
except ImportError:
    def send_to_session(session_key, message, timeout_sec=0):
        return False, "openclaw_gateway_call não disponível"

STREAM_DEVOPS = os.getenv("STREAM_EVENT_DEVOPS", "event:devops")
GROUP = os.getenv("DEVOPS_GROUP", "clawdevs")
CONSUMER = os.getenv("POD_NAME", os.getenv("HOSTNAME", "devops-1"))
BLOCK_MS = int(os.getenv("DEVOPS_BLOCK_MS", "5000"))
DEVOPS_SESSION_KEY = os.getenv("OPENCLAW_DEVOPS_SESSION_KEY", "agent:devops:main")


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


def process_event(r, msg_id: str, payload: dict) -> None:
    issue_id = (payload.get("issue_id") or "").strip()
    repo = (payload.get("repo") or os.getenv("GITHUB_REPO", "")).strip()
    branch = (payload.get("branch") or "").strip()
    pr = (payload.get("pr") or "").strip()
    message = f"""Evento pós-merge (event:devops). Ação: setar estado Deployed para a issue, disparar pipeline CI/CD se aplicável, e emitir feature_complete em orchestrator:events (para o Slack/Diretor).

issue_id: {issue_id}
repo: {repo}
branch: {branch}
pr: {pr}
"""
    ok, out = send_to_session(DEVOPS_SESSION_KEY, message, timeout_sec=0)
    if not ok:
        print(f"[DevOps] Falha ao enviar ao Gateway: {out}", file=sys.stderr)
        return
    r.xack(STREAM_DEVOPS, GROUP, msg_id)
    print(f"[DevOps] XACK {STREAM_DEVOPS} {msg_id} (enviado ao agente DevOps)")


def main() -> None:
    r = get_redis()
    print(f"[DevOps] Consumindo stream={STREAM_DEVOPS} group={GROUP} consumer={CONSUMER} (openclaw-first)")

    while True:
        try:
            reply = r.xreadgroup(GROUP, CONSUMER, {STREAM_DEVOPS: ">"}, block=BLOCK_MS, count=1)
        except Exception as e:
            print(f"[DevOps] Erro: {e}", file=sys.stderr)
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
                    process_event(r, msg_id, payload)
                except Exception as e:
                    print(f"[DevOps] Erro {msg_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
