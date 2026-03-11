#!/usr/bin/env python3
"""Implementacao do papel DevOps sobre o runtime compartilhado."""
from __future__ import annotations

import os

from app.agents.base import AgentSettings, BaseRoleAgent
from app.runtime import AgentResult, ExecutionPolicy, RunContext


class DevOpsAgent(BaseRoleAgent):
    def __init__(self) -> None:
        self.settings = AgentSettings(
            role_name="DevOps",
            stream_name=os.getenv("STREAM_EVENT_DEVOPS", "event:devops"),
            consumer_group=os.getenv("DEVOPS_GROUP", "clawdevs"),
            consumer_name=os.getenv("POD_NAME", os.getenv("HOSTNAME", "devops-1")),
            session_key=os.getenv("OPENCLAW_DEVOPS_SESSION_KEY", "agent:devops:main"),
            policy=ExecutionPolicy.from_env("DEVOPS", default_block_ms=5000, default_timeout_sec=0),
        )

    def build_instruction(self, redis_client, ctx: RunContext) -> str:
        issue_id = str(ctx.event.get("issue_id") or "").strip()
        repo = str(ctx.event.get("repo") or os.getenv("GITHUB_REPO", "")).strip()
        branch = str(ctx.event.get("branch") or "").strip()
        pr = str(ctx.event.get("pr") or "").strip()
        return f"""Evento pos-merge (event:devops). Acao: setar estado Deployed para a issue, disparar pipeline CI/CD se aplicavel, e emitir feature_complete em orchestrator:events (para o Slack/Diretor).

issue_id: {issue_id}
repo: {repo}
branch: {branch}
pr: {pr}
"""

    def on_success(self, redis_client, ctx: RunContext, send_output: dict | str) -> AgentResult:
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="devops.forwarded",
            summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id} (enviado ao agente DevOps)",
            metadata={"run_id": ctx.run_id},
        )
