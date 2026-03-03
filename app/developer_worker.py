#!/usr/bin/env python3
"""

Developer trigger: consome task:backlog, envia tarefa ao agente Developer no OpenClaw.
Adquire lock por story, seta estado InProgress; o Developer (no Gateway) implementa e,
ao concluir, usa ferramenta/adapter para publicar code:ready e liberar o lock. Sem LLM neste script (openclaw-first).
Ref: docs/issues/013-pods-tecnicos-developer-opencode.md, docs/agents-devs/state-machine-issues.md,
     .cursor/rules/openclaw-first.mdc
"""
import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from gpu_lock import get_redis

try:
    from issue_state import set_issue_state, STATE_IN_PROGRESS
except ImportError:
    KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
    STATE_IN_PROGRESS = "InProgress"

    def set_issue_state(r, issue_id: str, state: str, ttl_sec=None) -> bool:
        r.set(f"{KEY_PREFIX}:issue:{issue_id}:state", state)
        return True

try:
    from finops_attempt_cost import should_stop_task, get_attempt_count, increment_attempt
except ImportError:
    def should_stop_task(issue_id, attempt, cost_estimate):
        return False, ""
    def get_attempt_count(r, issue_id):
        return 0
    def increment_attempt(r, issue_id):
        return 1

try:
    from openclaw_gateway_call import send_to_session
except ImportError:
    def send_to_session(session_key, message, timeout_sec=0):
        return False, "openclaw_gateway_call não disponível"

STREAM = os.getenv("DEVELOPER_STREAM", "task:backlog")
GROUP = os.getenv("DEVELOPER_GROUP", "clawdevs")
CONSUMER = os.getenv("POD_NAME", os.getenv("HOSTNAME", "developer-1"))
BLOCK_MS = int(os.getenv("DEVELOPER_BLOCK_MS", "5000"))
FINOPS_COST_ESTIMATE = float(os.getenv("FINOPS_COST_ESTIMATE", "0.01"))
KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
DEV_LOCK_TTL = int(os.getenv("DEV_LOCK_TTL_SEC", "3600"))
DEVELOPER_SESSION_KEY = os.getenv("OPENCLAW_DEVELOPER_SESSION_KEY", "agent:developer:main")


def _dev_lock_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:dev_lock"


def acquire_story_lock(r, issue_id: str) -> bool:
    if not issue_id:
        return True
    key = _dev_lock_key(issue_id)
    agent = os.getenv("POD_NAME", os.getenv("HOSTNAME", "developer"))
    return bool(r.set(key, agent, nx=True, ex=DEV_LOCK_TTL))


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


def get_issue_spec(r, issue_id: str) -> str:
    key = f"{KEY_PREFIX}:issue:{issue_id}"
    raw = r.get(key)
    if raw is None:
        return ""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    return raw


def process_task(r, stream: str, msg_id: str, data) -> None:
    data = _payload_to_dict(data or {})
    issue_id = (data.get("issue_id") or data.get("issue") or data.get("task_id") or "").strip()
    if not acquire_story_lock(r, issue_id):
        print(f"[Developer] Story lock já ocupado para issue={issue_id}; devolvendo à fila.", file=sys.stderr)
        r.xadd(stream, data)
        r.xack(stream, GROUP, msg_id)
        return
    try:
        if issue_id:
            set_issue_state(r, issue_id, STATE_IN_PROGRESS)
        if issue_id:
            attempt = increment_attempt(r, issue_id)
            stop, reason = should_stop_task(issue_id, attempt, FINOPS_COST_ESTIMATE)
            if stop:
                print(f"[Developer] FinOps: interromper tarefa issue={issue_id} — {reason}", file=sys.stderr)
                if issue_id:
                    set_issue_state(r, issue_id, "Backlog")
                r.delete(_dev_lock_key(issue_id))
                r.xack(stream, GROUP, msg_id)
                try:
                    from orchestration_phase3 import emit_event
                    emit_event(r, "task_returned_to_po", issue_id=issue_id, reason=reason or "finops_limit")
                except Exception:
                    pass
                return
        spec = get_issue_spec(r, issue_id) if issue_id else ""
        message = f"""Tarefa do backlog (task:backlog). Implemente conforme especificação; ao concluir, use a ferramenta/adapter para publicar em code:ready (issue_id, branch) e liberar o dev_lock.

issue_id: {issue_id}
branch: {data.get("branch", "")}
priority: {data.get("priority", "1")}

Especificação (Redis project:v1:issue:{issue_id}):
{spec[:8000] or "(vazia)"}
"""
        ok, out = send_to_session(DEVELOPER_SESSION_KEY, message, timeout_sec=0)
        if not ok:
            print(f"[Developer] Falha ao enviar ao Gateway: {out}", file=sys.stderr)
            r.delete(_dev_lock_key(issue_id))
            return
        r.xack(stream, GROUP, msg_id)
        print(f"[Developer] XACK {stream} {msg_id} (enviado ao agente Developer)")
    except Exception:
        if issue_id:
            r.delete(_dev_lock_key(issue_id))
        raise


def main() -> None:
    r = get_redis()
    print(f"[Developer] Consumindo stream={STREAM} group={GROUP} consumer={CONSUMER} (openclaw-first)")

    while True:
        try:
            reply = r.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, block=BLOCK_MS, count=1)
        except Exception as e:
            print(f"[Developer] Erro XREADGROUP: {e}", file=sys.stderr)
            time.sleep(5)
            continue
        if not reply:
            continue
        for stream_name, messages in reply:
            stream_name = stream_name if isinstance(stream_name, str) else stream_name.decode()
            for msg_id, raw_data in messages:
                msg_id = msg_id if isinstance(msg_id, str) else msg_id.decode()
                try:
                    process_task(r, stream_name, msg_id, raw_data)
                except Exception as e:
                    print(f"[Developer] Erro ao processar {msg_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
