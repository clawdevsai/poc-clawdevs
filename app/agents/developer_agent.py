#!/usr/bin/env python3
"""Implementacao do papel Developer sobre o runtime compartilhado."""
from __future__ import annotations

import os

from app.agents.base import AgentSettings, BaseRoleAgent
from app.core.orchestration import emit_event
from app.runtime import (
    AgentResult,
    ExecutionPolicy,
    PreparedRun,
    RunContext,
    increment_attempt,
    should_stop_task,
)
from app.shared.issue_state import STATE_IN_PROGRESS, set_issue_state

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")


class DeveloperAgent(BaseRoleAgent):
    def __init__(self) -> None:
        self.settings = AgentSettings(
            role_name="Developer",
            stream_name=os.getenv("DEVELOPER_STREAM", "task:backlog"),
            consumer_group=os.getenv("DEVELOPER_GROUP", "clawdevs"),
            consumer_name=os.getenv("POD_NAME", os.getenv("HOSTNAME", "developer-1")),
            session_key=os.getenv("OPENCLAW_DEVELOPER_SESSION_KEY", "agent:developer:main"),
            policy=ExecutionPolicy.from_env("DEVELOPER", default_block_ms=5000, default_timeout_sec=0),
        )
        self.finops_cost_estimate = float(os.getenv("FINOPS_COST_ESTIMATE", "0.01"))
        self.dev_lock_ttl = int(os.getenv("DEV_LOCK_TTL_SEC", "3600"))

    def _dev_lock_key(self, issue_id: str) -> str:
        return f"{KEY_PREFIX}:issue:{issue_id}:dev_lock"

    def _active_issue_key(self, developer_id: str) -> str:
        return f"{KEY_PREFIX}:developer:{developer_id}:active_issue"

    def _active_developer_key(self, issue_id: str) -> str:
        return f"{KEY_PREFIX}:issue:{issue_id}:active_developer"

    def _pr_merged_key(self, issue_id: str) -> str:
        return f"{KEY_PREFIX}:issue:{issue_id}:pr_merged"

    def _developer_id(self) -> str:
        return os.getenv("POD_NAME", os.getenv("HOSTNAME", "developer"))

    def acquire_story_lock(self, redis_client, issue_id: str) -> bool:
        if not issue_id:
            return True
        agent = self._developer_id()
        return bool(redis_client.set(self._dev_lock_key(issue_id), agent, nx=True, ex=self.dev_lock_ttl))

    def _is_issue_merged(self, redis_client, issue_id: str) -> bool:
        raw = redis_client.get(self._pr_merged_key(issue_id))
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        return str(raw or "").strip() in {"1", "true", "True", "merged"}

    def _active_issue(self, redis_client, developer_id: str) -> str:
        raw = redis_client.get(self._active_issue_key(developer_id))
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        return str(raw or "").strip()

    def get_issue_spec(self, redis_client, issue_id: str) -> str:
        raw = redis_client.get(f"{KEY_PREFIX}:issue:{issue_id}")
        if raw is None:
            return ""
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
        return str(raw)

    def prepare(self, redis_client, ctx: RunContext) -> PreparedRun:
        issue_id = ctx.issue_id or ""
        developer_id = self._developer_id()
        current_active = self._active_issue(redis_client, developer_id)
        if current_active and current_active != issue_id and not self._is_issue_merged(redis_client, current_active):
            redis_client.xadd(ctx.stream_name, ctx.envelope.next_attempt_payload())
            return PreparedRun(
                should_send=False,
                ack_on_exit=True,
                result=AgentResult(
                    status="blocked",
                    status_code="blocked_waiting_merge",
                    event_name="developer.blocked_waiting_merge",
                    summary=(
                        f"[{self.role_name}] aguardando merge da issue ativa={current_active}; "
                        f"nova issue={issue_id} devolvida para fila."
                    ),
                ),
            )
        if current_active and current_active != issue_id and self._is_issue_merged(redis_client, current_active):
            redis_client.delete(self._active_issue_key(developer_id))

        if not self.acquire_story_lock(redis_client, issue_id):
            redis_client.xadd(ctx.stream_name, ctx.envelope.next_attempt_payload())
            return PreparedRun(
                should_send=False,
                ack_on_exit=True,
                result=AgentResult(
                    status="requeued",
                    status_code="requeued_lock_busy",
                    event_name="developer.requeued_lock_busy",
                    summary=f"[{self.role_name}] Story lock ja ocupado para issue={issue_id}; devolvendo a fila.",
                ),
            )
        if issue_id:
            set_issue_state(redis_client, issue_id, STATE_IN_PROGRESS)
            redis_client.set(self._active_issue_key(developer_id), issue_id, ex=self.dev_lock_ttl)
            redis_client.set(self._active_developer_key(issue_id), developer_id, ex=self.dev_lock_ttl)
            redis_client.set(self._pr_merged_key(issue_id), "0")
            attempt = increment_attempt(redis_client, issue_id)
            stop, reason = should_stop_task(issue_id, attempt, self.finops_cost_estimate)
            if stop:
                set_issue_state(redis_client, issue_id, "Backlog")
                redis_client.delete(self._dev_lock_key(issue_id))
                redis_client.delete(self._active_issue_key(developer_id))
                redis_client.delete(self._active_developer_key(issue_id))
                emit_event(
                    redis_client,
                    "task_returned_to_po",
                    issue_id=issue_id,
                    reason=reason or "finops_limit",
                )
                return PreparedRun(
                    should_send=False,
                    ack_on_exit=True,
                    result=AgentResult(
                        status="halted",
                        status_code="halted_finops",
                        event_name="developer.halted_finops",
                        summary=f"[{self.role_name}] FinOps: interromper tarefa issue={issue_id} - {reason}",
                    ),
                )
        return PreparedRun()

    def build_instruction(self, redis_client, ctx: RunContext) -> str:
        issue_id = ctx.issue_id or ""
        spec = self.get_issue_spec(redis_client, issue_id) if issue_id else ""
        branch = str(ctx.event.get("branch") or "")
        priority = str(ctx.event.get("priority") or "1")
        return f"""Tarefa do backlog (task:backlog). Implemente conforme especificacao; ao concluir, use a ferramenta/adapter para publicar em code:ready (issue_id, branch) e liberar o dev_lock.

issue_id: {issue_id}
branch: {branch}
priority: {priority}

Especificacao (Redis project:v1:issue:{issue_id}):
{spec[:8000] or "(vazia)"}
"""

    def on_success(self, redis_client, ctx: RunContext, send_output: dict | str) -> AgentResult:
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="developer.forwarded",
            summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id} (enviado ao agente Developer)",
            metadata={"run_id": ctx.run_id},
        )

    def on_error(self, redis_client, ctx: RunContext | None, error: Exception) -> None:
        if ctx and ctx.issue_id:
            redis_client.delete(self._dev_lock_key(ctx.issue_id))
        super().on_error(redis_client, ctx, error)
