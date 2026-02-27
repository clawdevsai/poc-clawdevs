#!/usr/bin/env python3
"""
Slot por agente (Fase 1 — evolução 014). Um pod por role: Architect, QA, CyberSec, DBA.
Lê de STREAM_IN (consumer group por role), executa uma etapa, publica em STREAM_OUT, XACK.
Pipeline: code:ready → review_architect_done → review_qa_done → review_cybersec_done → review_done.
Ref: docs/41-fase1-agentes-soul-pods.md, docs/38-redis-streams-estado-global.md
"""
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gpu_lock import GPULock, get_redis

try:
    from acefalo_redis import is_consumption_paused
except ImportError:

    def is_consumption_paused(r=None):
        return False


AGENT_ROLE = os.getenv("AGENT_ROLE", "").strip()
STREAM_IN = os.getenv("STREAM_IN", "code:ready")
STREAM_OUT = os.getenv("STREAM_OUT", "review_architect_done")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "architect-slot")
CONSUMER_NAME = os.getenv("POD_NAME", os.getenv("HOSTNAME", "slot-1"))
BLOCK_MS = int(os.getenv("SLOT_BLOCK_MS", "5000"))

VALID_ROLES = ("Architect", "QA", "CyberSec", "DBA")


def run_etapa(nome: str) -> None:
    """Executa uma etapa (stub; em produção chamar Ollama)."""
    print(f"  [{nome}] Etapa executada (stub).")
    time.sleep(0.5)


def main() -> None:
    if AGENT_ROLE not in VALID_ROLES:
        print(f"AGENT_ROLE deve ser um de {VALID_ROLES}. Atual: {AGENT_ROLE!r}", file=sys.stderr)
        sys.exit(1)

    r = get_redis()
    print(
        f"[Slot {AGENT_ROLE}] stream_in={STREAM_IN} stream_out={STREAM_OUT} group={CONSUMER_GROUP} consumer={CONSUMER_NAME}"
    )

    while True:
        if is_consumption_paused(r=r):
            time.sleep(60)
            continue
        reply = r.xreadgroup(
            CONSUMER_GROUP,
            CONSUMER_NAME,
            {STREAM_IN: "0"},
            block=BLOCK_MS,
            count=1,
        )
        if not reply:
            continue
        for stream_key, messages in reply:
            stream_in_name = stream_key if isinstance(stream_key, str) else stream_key.decode()
            for msg_id, data in messages:
                msg_id = msg_id if isinstance(msg_id, str) else msg_id.decode()
                data = data or {}
                if isinstance(data, dict):
                    payload = {k: str(v) for k, v in data.items()}
                elif isinstance(data, (list, tuple)):
                    payload = {}
                    for i in range(0, len(data) - 1, 2):
                        payload[str(data[i])] = str(data[i + 1])
                else:
                    payload = {}
                payload["_from_role"] = AGENT_ROLE
                payload["_msg_in"] = msg_id
                try:
                    with GPULock():
                        run_etapa(AGENT_ROLE)
                    r.xadd(STREAM_OUT, payload)
                    r.xack(stream_in_name, CONSUMER_GROUP, msg_id)
                    print(f"[Slot {AGENT_ROLE}] Processado {msg_id} -> {STREAM_OUT}")
                except Exception as e:
                    print(f"[Slot {AGENT_ROLE}] Erro ao processar {msg_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
