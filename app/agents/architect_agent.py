#!/usr/bin/env python3
"""Implementacao do papel Architect Draft sobre o runtime compartilhado."""
from __future__ import annotations

import os

from app.agents.base import AgentSettings, BaseRoleAgent
from app.runtime import AgentResult, ExecutionPolicy, PreparedRun, RunContext

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")


class ArchitectDraftAgent(BaseRoleAgent):
    def __init__(self) -> None:
        self.settings = AgentSettings(
            role_name="Architect-draft",
            stream_name=os.getenv("STREAM_DRAFT_ISSUE", "draft.2.issue"),
            consumer_group=os.getenv("ARCHITECT_DRAFT_GROUP", "clawdevs"),
            consumer_name=os.getenv("POD_NAME", os.getenv("HOSTNAME", "architect-draft-1")),
            session_key=os.getenv("OPENCLAW_ARCHITECT_SESSION_KEY", "agent:architect:main"),
            policy=ExecutionPolicy.from_env("ARCHITECT_DRAFT", default_block_ms=5000, default_timeout_sec=0),
        )

    def prepare(self, redis_client, ctx: RunContext) -> PreparedRun:
        if not ctx.issue_id:
            return PreparedRun(
                should_send=False,
                ack_on_exit=True,
                result=AgentResult(
                    status="ignored",
                    status_code="ignored_missing_issue",
                    event_name="architect.ignored_missing_issue",
                    summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id} (issue ausente)",
                ),
            )
        return PreparedRun()

    def get_issue_spec(self, redis_client, issue_id: str) -> str:
        raw = redis_client.get(f"{KEY_PREFIX}:issue:{issue_id}")
        if raw is None:
            return ""
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
        return str(raw)

    def build_instruction(self, redis_client, ctx: RunContext) -> str:
        issue_id = ctx.issue_id or ""
        title = str(ctx.event.get("title") or "").strip()
        summary = str(ctx.event.get("summary") or "").strip()
        spec = self.get_issue_spec(redis_client, issue_id)
        return f"""Rascunho de issue para revisao (draft.2.issue). Avalie viabilidade tecnica; se aprovado, publique em task:backlog e sete estado Ready; se rejeitado, publique em draft_rejected e sete estado Refinamento.

issue_id: {issue_id}
title: {title}
summary: {summary}

Especificacao (Redis project:v1:issue:{issue_id}):
{spec[:6000] or '(vazia)'}
"""

    def on_success(self, redis_client, ctx: RunContext, send_output: dict | str) -> AgentResult:
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="architect.forwarded",
            summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id} (enviado ao agente Arquiteto)",
            metadata={"run_id": ctx.run_id},
        )
