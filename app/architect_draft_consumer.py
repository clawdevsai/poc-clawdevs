#!/usr/bin/env python3
"""
Architect draft trigger: consome draft.2.issue (rascunho do PO), envia ao agente Arquiteto no OpenClaw.
O Arquiteto (no Gateway) valida/refina; rejeita → draft_rejected + estado Refinamento;
aprova → Ready + task:backlog. Sem LLM neste script (openclaw-first).
Ref: docs/38-redis-streams-estado-global.md, docs/agents-devs/state-machine-issues.md,
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
    from openclaw_gateway_call import send_to_session
except ImportError:
    def send_to_session(session_key, message, timeout_sec=0):
        return False, "openclaw_gateway_call não disponível"

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
STREAM_DRAFT = os.getenv("STREAM_DRAFT_ISSUE", "draft.2.issue")
GROUP = os.getenv("ARCHITECT_DRAFT_GROUP", "clawdevs")
CONSUMER = os.getenv("POD_NAME", os.getenv("HOSTNAME", "architect-draft-1"))
BLOCK_MS = int(os.getenv("ARCHITECT_DRAFT_BLOCK_MS", "5000"))
ARCHITECT_SESSION_KEY = os.getenv("OPENCLAW_ARCHITECT_SESSION_KEY", "agent:architect:main")


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


def process_draft(r, msg_id: str, payload: dict) -> None:
    issue_id = (payload.get("issue_id") or payload.get("issue") or "").strip()
    title = (payload.get("title") or "").strip()
    summary = (payload.get("summary") or "").strip()
    if not issue_id:
        r.xack(STREAM_DRAFT, GROUP, msg_id)
        return
    spec = get_issue_spec(r, issue_id)
    message = f"""Rascunho de issue para revisão (draft.2.issue). Avalie viabilidade técnica; se aprovado, publique em task:backlog e sete estado Ready; se rejeitado, publique em draft_rejected e sete estado Refinamento.

issue_id: {issue_id}
title: {title}
summary: {summary}

Especificação (Redis project:v1:issue:{issue_id}):
{spec[:6000] or '(vazia)'}
"""
    ok, out = send_to_session(ARCHITECT_SESSION_KEY, message, timeout_sec=0)
    if not ok:
        print(f"[Architect-draft] Falha ao enviar ao Gateway: {out}", file=sys.stderr)
        return
    r.xack(STREAM_DRAFT, GROUP, msg_id)
    print(f"[Architect-draft] XACK {STREAM_DRAFT} {msg_id} (enviado ao agente Arquiteto)")


def main() -> None:
    r = get_redis()
    print(f"[Architect-draft] Consumindo stream={STREAM_DRAFT} group={GROUP} consumer={CONSUMER} (openclaw-first)")

    while True:
        try:
            reply = r.xreadgroup(GROUP, CONSUMER, {STREAM_DRAFT: ">"}, block=BLOCK_MS, count=1)
        except Exception as e:
            print(f"[Architect-draft] Erro: {e}", file=sys.stderr)
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
                    process_draft(r, msg_id, payload)
                except Exception as e:
                    print(f"[Architect-draft] Erro {msg_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
