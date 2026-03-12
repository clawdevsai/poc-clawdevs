#!/usr/bin/env python3
"""Implementacao do papel Architect-review sobre o runtime compartilhado."""
from __future__ import annotations

import os

from app.agents.base import AgentSettings, BaseRoleAgent
from app.runtime import AgentResult, ExecutionPolicy, PreparedRun, RunContext


class ArchitectReviewAgent(BaseRoleAgent):
    def __init__(self) -> None:
        self.settings = AgentSettings(
            role_name="Architect-review",
            stream_name=os.getenv("ARCHITECT_REVIEW_STREAM", os.getenv("STREAM_ORCHESTRATOR_EVENTS", "orchestrator:events")),
            consumer_group=os.getenv("ARCHITECT_REVIEW_GROUP", "clawdevs-architect-review"),
            consumer_name=os.getenv("POD_NAME", os.getenv("HOSTNAME", "architect-review-1")),
            session_key=os.getenv("OPENCLAW_ARCHITECT_REVIEW_SESSION_KEY", "agent:architect_review:main"),
            policy=ExecutionPolicy.from_env("ARCHITECT_REVIEW", default_block_ms=5000, default_timeout_sec=0),
        )

    def prepare(self, redis_client, ctx: RunContext) -> PreparedRun:
        event_type = str(ctx.event.get("type") or "").strip()
        if event_type != "architect_final_decision_required":
            return PreparedRun(
                should_send=False,
                ack_on_exit=True,
                result=AgentResult(
                    status="ignored",
                    status_code="ignored_non_final_decision_event",
                    event_name="architect_review.ignored_non_final_decision_event",
                    summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id} (evento sem decisao final)",
                ),
            )
        return PreparedRun()

    def build_instruction(self, redis_client, ctx: RunContext) -> str:
        issue_id = str(ctx.event.get("issue_id") or "").strip()
        branch = str(ctx.event.get("branch") or "").strip()
        repo = str(ctx.event.get("repo") or os.getenv("GITHUB_REPO", "")).strip()
        pr = str(ctx.event.get("pr") or "").strip()
        review_round = str(ctx.event.get("round") or "").strip()
        max_rounds = str(ctx.event.get("max_rounds") or "").strip()
        reason = str(ctx.event.get("reason") or "").strip()
        return f"""Escalonamento de decisao final do Architect apos limite de rodadas.

Acao:
- decidir `approve_merge` ou `request_final_correction`
- quando aprovado, publicar em event:devops (issue_id/branch/repo/pr)
- quando bloqueado, registrar decisao objetiva para retorno ao Developer

issue_id: {issue_id}
branch: {branch}
repo: {repo}
pr: {pr}
round: {review_round}
max_rounds: {max_rounds}
reason: {reason}
"""

    def on_success(self, redis_client, ctx: RunContext, send_output: dict | str) -> AgentResult:
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="architect_review.forwarded",
            summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id} (enviado ao Architect-review)",
            metadata={"run_id": ctx.run_id},
        )

