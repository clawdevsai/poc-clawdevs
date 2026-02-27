#!/usr/bin/env python3
"""
Slot único "Revisão pós-Dev" (Fase 0 — 125).
Consome o stream code:ready (consumer group revisao-pos-dev), adquire GPU Lock uma vez,
executa Architect → QA → CyberSec → DBA em sequência, libera o lock e envia XACK.
Ref: docs/39-consumer-groups-pipeline-revisao.md, docs/estrategia-uso-hardware-gpu-cpu.md
"""
import os
import sys
import time

# Adicionar diretório do script para importar gpu_lock
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from gpu_lock import GPULock, get_redis

# Contingência cluster acéfalo (124): respeitar pausa
try:
    from acefalo_redis import is_consumption_paused
except ImportError:
    def is_consumption_paused(r=None):
        return False

STREAM_CODE_READY = os.getenv("STREAM_CODE_READY", "code:ready")
GROUP_REVISAO = os.getenv("CONSUMER_GROUP_REVISAO", "revisao-pos-dev")
CONSUMER_NAME = os.getenv("POD_NAME", os.getenv("HOSTNAME", "slot-1"))
BLOCK_MS = int(os.getenv("SLOT_BLOCK_MS", "5000"))


def run_etapa(nome: str) -> None:
    """Simula uma etapa (Architect, QA, CyberSec, DBA). Em produção: chamar Ollama."""
    print(f"  [{nome}] Etapa executada (stub).")
    time.sleep(0.5)


def processar_mensagem(r, stream: str, msg_id: str, data: dict) -> None:
    """Processa uma mensagem: adquire lock, executa 4 etapas, libera, ACK."""
    print(f"[Slot] Processando mensagem {msg_id} do stream {stream}")
    with GPULock():
        run_etapa("Architect")
        run_etapa("QA")
        run_etapa("CyberSec")
        run_etapa("DBA")
    r.xack(stream, GROUP_REVISAO, msg_id)
    print(f"[Slot] XACK {stream} {GROUP_REVISAO} {msg_id}")


def main() -> None:
    r = get_redis()
    print(f"[Slot] Consumindo stream={STREAM_CODE_READY} group={GROUP_REVISAO} consumer={CONSUMER_NAME}")

    while True:
        if is_consumption_paused(r=r):
            time.sleep(60)
            continue
        # XREADGROUP GROUP revisao-pos-dev slot-1 BLOCK 5000 STREAMS code:ready 0
        reply = r.xreadgroup(
            GROUP_REVISAO,
            CONSUMER_NAME,
            {STREAM_CODE_READY: "0"},
            block=BLOCK_MS,
            count=1,
        )
        if not reply:
            continue
        for stream, messages in reply:
            stream = stream if isinstance(stream, str) else stream.decode()
            for msg_id, data in messages:
                msg_id = msg_id if isinstance(msg_id, str) else msg_id.decode()
                data = data or {}
                try:
                    processar_mensagem(r, stream, msg_id, data)
                except Exception as e:
                    print(f"[Slot] Erro ao processar {msg_id}: {e}", file=sys.stderr)
                    # Não faz XACK; mensagem fica pendente para retry


if __name__ == "__main__":
    main()
