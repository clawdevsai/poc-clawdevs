#!/usr/bin/env python3
"""
Architect trigger: consome draft.2.issue, envia ao agente Architect no OpenClaw
e mantém o worker alinhado ao runtime central.
"""
from app.bootstrap import bootstrap_paths

bootstrap_paths()

from app.agents.architect_agent import ArchitectDraftAgent
from app.runtime import build_runtime_tool_registry, build_session_sender, run_stream_worker
from app.shared.redis_client import get_redis


def main() -> None:
    r = get_redis()
    registry = build_runtime_tool_registry()
    run_stream_worker(r, ArchitectDraftAgent(), build_session_sender(registry))


if __name__ == "__main__":
    main()
