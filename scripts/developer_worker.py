#!/usr/bin/env python3
"""
Worker do agente Developer (Fase 1 — 013).
Consome stream task:backlog (consumer group clawdevs, consumer name developer),
adquire GPU Lock, processa (stub ou chamada Ollama), libera lock e envia XACK.
truncamento-finops: antes de processar, verifica finops_attempt_cost; se deve interromper, não usa GPU e emite evento.
Ref: docs/issues/013-pods-tecnicos-developer-opencode.md, docs/issues/041-truncamento-contexto-finops.md
"""
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from gpu_lock import GPULock, get_redis

# truncamento-finops — FinOps: verificar se deve interromper tarefa (devolver ao PO)
try:
    from finops_attempt_cost import should_stop_task, get_attempt_count, increment_attempt
except ImportError:
    def should_stop_task(issue_id, attempt, cost_estimate):
        return False, ""
    def get_attempt_count(r, issue_id):
        return 0
    def increment_attempt(r, issue_id):
        return 1

STREAM = os.getenv("DEVELOPER_STREAM", "task:backlog")
GROUP = os.getenv("DEVELOPER_GROUP", "clawdevs")
CONSUMER = os.getenv("POD_NAME", os.getenv("HOSTNAME", "developer-1"))
BLOCK_MS = int(os.getenv("DEVELOPER_BLOCK_MS", "5000"))
FINOPS_COST_ESTIMATE = float(os.getenv("FINOPS_COST_ESTIMATE", "0.01"))


def process_task(r, stream: str, msg_id: str, data: dict) -> None:
    """Processa uma tarefa: verifica FinOps; adquire GPU Lock, executa (stub ou Ollama), libera."""
    issue_id = (data.get("issue_id") or data.get("issue") or data.get("task_id") or "").strip()
    if issue_id:
        attempt = increment_attempt(r, issue_id)
        stop, reason = should_stop_task(issue_id, attempt, FINOPS_COST_ESTIMATE)
        if stop:
            print(f"[Developer] FinOps: interromper tarefa issue={issue_id} — {reason}", file=sys.stderr)
            r.xack(stream, GROUP, msg_id)
            try:
                from orchestration_phase3 import emit_event
                emit_event(r, "task_returned_to_po", issue_id=issue_id, reason=reason or "finops_limit")
            except Exception:
                pass
            return
    print(f"[Developer] Processando {msg_id} stream={stream}")
    with GPULock():
        # Stub: em produção chamar OpenCode / Ollama para gerar código
        time.sleep(0.5)
        print(f"[Developer] Tarefa processada (stub). Liberando lock.")
    r.xack(stream, GROUP, msg_id)
    print(f"[Developer] XACK {stream} {GROUP} {msg_id}")


def main() -> None:
    r = get_redis()
    print(f"[Developer] Consumindo stream={STREAM} group={GROUP} consumer={CONSUMER}")

    while True:
        try:
            reply = r.xreadgroup(GROUP, CONSUMER, {STREAM: "0"}, block=BLOCK_MS, count=1)
        except Exception as e:
            print(f"[Developer] Erro XREADGROUP: {e}", file=sys.stderr)
            time.sleep(5)
            continue
        if not reply:
            continue
        for stream, messages in reply:
            stream = stream if isinstance(stream, str) else stream.decode()
            for msg_id, data in messages:
                msg_id = msg_id if isinstance(msg_id, str) else msg_id.decode()
                data = data or {}
                try:
                    process_task(r, stream, msg_id, data)
                except Exception as e:
                    print(f"[Developer] Erro ao processar {msg_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
