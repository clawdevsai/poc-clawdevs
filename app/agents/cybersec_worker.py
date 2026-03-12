#!/usr/bin/env python3
"""
CyberSec trigger: consome pr:review e envia contexto ao agente CyberSec no OpenClaw.
"""
from app.bootstrap import bootstrap_paths

bootstrap_paths()

from app.agents.cybersec_agent import CyberSecAgent
from app.runtime import build_runtime_session_sender, build_runtime_tool_registry, run_stream_worker
from app.shared.redis_client import get_redis


def main() -> None:
    redis_client = get_redis()
    registry = build_runtime_tool_registry()
    agent = CyberSecAgent()
    sender = build_runtime_session_sender(registry, role_name=agent.role_name, session_key=agent.session_key)
    run_stream_worker(redis_client, agent, sender)


if __name__ == "__main__":
    main()

