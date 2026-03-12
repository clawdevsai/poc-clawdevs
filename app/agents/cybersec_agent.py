#!/usr/bin/env python3
"""Implementacao do papel CyberSec sobre o runtime compartilhado."""
from __future__ import annotations

import os

from app.agents.base import AgentSettings, BaseRoleAgent
from app.core.review_consensus import finalize_round_if_ready, record_review_decision
from app.runtime import AgentResult, ExecutionPolicy, RunContext


class CyberSecAgent(BaseRoleAgent):
    def __init__(self) -> None:
        self.settings = AgentSettings(
            role_name="CyberSec",
            stream_name=os.getenv("CYBERSEC_REVIEW_STREAM", os.getenv("STREAM_PR_REVIEW", "pr:review")),
            consumer_group=os.getenv("CYBERSEC_GROUP", "clawdevs-cybersec"),
            consumer_name=os.getenv("POD_NAME", os.getenv("HOSTNAME", "cybersec-1")),
            session_key=os.getenv("OPENCLAW_CYBERSEC_SESSION_KEY", "agent:cybersec:main"),
            policy=ExecutionPolicy.from_env("CYBERSEC", default_block_ms=5000, default_timeout_sec=30),
        )

    def build_instruction(self, redis_client, ctx: RunContext) -> str:
        issue_id = str(ctx.event.get("issue_id") or "").strip()
        branch = str(ctx.event.get("branch") or "").strip()
        repo = str(ctx.event.get("repo") or os.getenv("GITHUB_REPO", "")).strip()
        pr = str(ctx.event.get("pr") or "").strip()
        review_round = str(ctx.event.get("round") or "").strip()
        return f"""Evento de PR review. Acao CyberSec: revisar seguranca da mudanca (segredos, auth, validacao de entrada, superficie de ataque).

Se houver vulnerabilidade relevante, bloquear com justificativa objetiva e acao corretiva.

issue_id: {issue_id}
branch: {branch}
repo: {repo}
pr: {pr}
round: {review_round}
"""

    def on_success(self, redis_client, ctx: RunContext, send_output: dict | str) -> AgentResult:
        issue_id = str(ctx.event.get("issue_id") or "").strip()
        review_round = str(ctx.event.get("round") or "").strip()
        branch = str(ctx.event.get("branch") or "").strip()
        repo = str(ctx.event.get("repo") or "").strip()
        pr = str(ctx.event.get("pr") or "").strip()
        if issue_id and review_round:
            record_review_decision(
                redis_client,
                issue_id=issue_id,
                review_round=review_round,
                role=self.role_name,
                send_output=send_output,
                repo=repo,
                pr=pr,
            )
            finalize_round_if_ready(
                redis_client,
                issue_id=issue_id,
                review_round=review_round,
                branch=branch,
                repo=repo,
                pr=pr,
            )
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="cybersec.forwarded",
            summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id} (enviado ao agente CyberSec)",
            metadata={"run_id": ctx.run_id},
        )
