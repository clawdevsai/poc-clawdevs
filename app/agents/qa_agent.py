#!/usr/bin/env python3
"""Implementacao do papel QA sobre o runtime compartilhado."""
from __future__ import annotations

import os

from app.agents.base import AgentSettings, BaseRoleAgent
from app.runtime import AgentResult, ExecutionPolicy, RunContext


class QAAgent(BaseRoleAgent):
    def __init__(self) -> None:
        self.settings = AgentSettings(
            role_name="QA",
            stream_name=os.getenv("QA_STREAM", "code:ready"),
            consumer_group=os.getenv("QA_GROUP", "clawdevs"),
            consumer_name=os.getenv("POD_NAME", os.getenv("HOSTNAME", "qa-1")),
            session_key=os.getenv("OPENCLAW_QA_SESSION_KEY", "agent:qa:main"),
            policy=ExecutionPolicy.from_env("QA", default_block_ms=5000, default_timeout_sec=0),
        )

    def build_instruction(self, redis_client, ctx: RunContext) -> str:
        issue_id = str(ctx.event.get("issue_id") or "").strip()
        branch = str(ctx.event.get("branch") or "").strip()
        repo = str(ctx.event.get("repo") or os.getenv("GITHUB_REPO", "")).strip()
        return f"""Evento code:ready. Acao QA: revisar a mudanca, validar criterios de aceite e executar checks essenciais.

Se aprovado, publicar evento em event:devops com issue_id/branch/repo.
Se bloqueado, retornar decisao de bloqueio com razao objetiva.

issue_id: {issue_id}
branch: {branch}
repo: {repo}
"""

    def on_success(self, redis_client, ctx: RunContext, send_output: dict | str) -> AgentResult:
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="qa.forwarded",
            summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id} (enviado ao agente QA)",
            metadata={"run_id": ctx.run_id},
        )
