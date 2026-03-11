#!/usr/bin/env python3
"""
QA trigger: consome code:ready, envia ao agente QA no OpenClaw.
QA aprova/bloqueia e, quando aprovado, encaminha para event:devops.
"""
from app.bootstrap import bootstrap_paths

bootstrap_paths()

from app.agents.qa_agent import QAAgent
from app.runtime import build_runtime_session_sender, build_runtime_tool_registry, run_stream_worker
from app.shared.redis_client import get_redis


def main() -> None:
    redis_client = get_redis()
    registry = build_runtime_tool_registry()
    agent = QAAgent()
    sender = build_runtime_session_sender(registry, role_name=agent.role_name, session_key=agent.session_key)
    run_stream_worker(redis_client, agent, sender)


if __name__ == "__main__":
    main()
