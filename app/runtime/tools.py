#!/usr/bin/env python3
"""Bootstrap do conjunto minimo de ferramentas do runtime."""
from __future__ import annotations

import os
from typing import Any

from app.runtime.logging import log_event
from app.runtime.model_provider import load_runtime_stack_config, validate_runtime_stack
from app.runtime.openclaw_session import resolve_openclaw_session_config_for_role
from app.runtime.tool_registry import ToolRegistry
from app.runtime.openclaw_client import TOOL_OPENCLAW_SESSIONS_SEND, send_to_session
from app.shared.issue_state import (
    STATE_DEPLOYED,
    STATE_IN_REVIEW,
    STATE_READY,
    STATE_REFINAMENTO,
    set_issue_state,
)

TOOL_PUBLISH_BACKLOG = "redis.publish_backlog"
TOOL_PUBLISH_DRAFT_REJECTED = "redis.publish_draft_rejected"
TOOL_PUBLISH_CODE_READY = "redis.publish_code_ready"
TOOL_PUBLISH_DEPLOY_EVENT = "redis.publish_deploy_event"
TOOL_PUBLISH_PR_REVIEW = "redis.publish_pr_review"

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
STREAM_PR_REVIEW = os.environ.get("STREAM_PR_REVIEW", "pr:review")
MAX_PR_REVIEW_ROUNDS = int(os.environ.get("MAX_PR_REVIEW_ROUNDS", "5"))


def _pr_review_round_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:pr_review_round"


def _pr_merged_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:pr_merged"


def _issue_active_developer_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}:active_developer"


def _developer_active_issue_key(developer_id: str) -> str:
    return f"{KEY_PREFIX}:developer:{developer_id}:active_issue"


def publish_backlog(
    *,
    redis_client: Any,
    issue_id: str,
    title: str = "",
    summary: str = "",
    priority: str = "1",
) -> tuple[bool, dict[str, str]]:
    set_issue_state(redis_client, issue_id, STATE_READY)
    payload = {
        "issue_id": issue_id,
        "title": title,
        "summary": summary,
        "priority": priority,
    }
    redis_client.xadd("task:backlog", payload)
    return True, {"stream": "task:backlog", "issue_id": issue_id, "state": STATE_READY}


def publish_draft_rejected(
    *,
    redis_client: Any,
    issue_id: str,
    reason: str,
    title: str = "",
) -> tuple[bool, dict[str, str]]:
    set_issue_state(redis_client, issue_id, STATE_REFINAMENTO)
    payload = {
        "issue_id": issue_id,
        "reason": reason,
        "title": title,
    }
    redis_client.xadd("draft_rejected", payload)
    return True, {"stream": "draft_rejected", "issue_id": issue_id, "state": STATE_REFINAMENTO}


def publish_code_ready(
    *,
    redis_client: Any,
    issue_id: str,
    branch: str,
    repo: str = "",
    pr: str = "",
) -> tuple[bool, dict[str, str]]:
    from app.core.orchestration import emit_event

    round_key = _pr_review_round_key(issue_id)
    review_round = int(redis_client.incr(round_key))
    if review_round > MAX_PR_REVIEW_ROUNDS:
        emit_event(
            redis_client,
            "architect_final_decision_required",
            issue_id=issue_id,
            pr=pr,
            branch=branch,
            repo=repo,
            round=review_round,
            max_rounds=MAX_PR_REVIEW_ROUNDS,
            reason="max_pr_review_rounds_reached",
            status_code="architect_final_decision_required",
            event_name="orchestration.architect_final_decision_required",
        )
        return (
            True,
            {
                "stream": STREAM_PR_REVIEW,
                "issue_id": issue_id,
                "branch": branch,
                "status": "escalated",
                "round": str(review_round),
            },
        )

    set_issue_state(redis_client, issue_id, STATE_IN_REVIEW)
    redis_client.set(_pr_merged_key(issue_id), "0")
    payload = {
        "issue_id": issue_id,
        "branch": branch,
        "repo": repo,
        "pr": pr,
        "round": str(review_round),
    }
    redis_client.xadd("code:ready", payload)
    redis_client.xadd(STREAM_PR_REVIEW, payload)
    return (
        True,
        {
            "stream": STREAM_PR_REVIEW,
            "issue_id": issue_id,
            "branch": branch,
            "state": STATE_IN_REVIEW,
            "round": str(review_round),
        },
    )


def publish_deploy_event(
    *,
    redis_client: Any,
    issue_id: str,
    branch: str,
    repo: str = "",
    pr: str = "",
) -> tuple[bool, dict[str, str]]:
    from app.core.orchestration import emit_event

    set_issue_state(redis_client, issue_id, STATE_DEPLOYED)
    redis_client.set(_pr_merged_key(issue_id), "1")
    redis_client.delete(_pr_review_round_key(issue_id))
    active_developer = redis_client.get(_issue_active_developer_key(issue_id))
    if isinstance(active_developer, bytes):
        active_developer = active_developer.decode("utf-8", errors="replace")
    active_developer = str(active_developer or "").strip()
    if active_developer:
        redis_client.delete(_developer_active_issue_key(active_developer))
    redis_client.delete(_issue_active_developer_key(issue_id))
    payload = {
        "issue_id": issue_id,
        "branch": branch,
        "repo": repo,
        "pr": pr,
    }
    redis_client.xadd("event:devops", payload)
    emit_event(redis_client, "feature_complete", issue_id=issue_id, branch=branch, repo=repo, pr=pr)
    return True, {"stream": "event:devops", "issue_id": issue_id, "state": STATE_DEPLOYED}


def build_runtime_tool_registry() -> ToolRegistry:
    stack = load_runtime_stack_config()
    errors = validate_runtime_stack(stack)
    if errors:
        raise RuntimeError("; ".join(errors))

    log_event(
        "runtime.stack_configured",
        stack=stack.stack_label,
        model_provider=stack.model_provider,
        model_mode=stack.model_mode,
        ollama_base_url=stack.ollama_base_url,
        ollama_model=stack.ollama_model,
    )
    registry = ToolRegistry()
    registry.register(
        TOOL_OPENCLAW_SESSIONS_SEND,
        send_to_session,
        allowed_roles=(
            "PO",
            "Architect-draft",
            "Architect-review",
            "Developer",
            "QA",
            "DBA",
            "CyberSec",
            "DevOps",
        ),
    )
    registry.register(
        TOOL_PUBLISH_BACKLOG,
        publish_backlog,
        allowed_roles=("PO", "Architect-draft"),
    )
    registry.register(
        TOOL_PUBLISH_DRAFT_REJECTED,
        publish_draft_rejected,
        allowed_roles=("Architect-draft",),
    )
    registry.register(
        TOOL_PUBLISH_CODE_READY,
        publish_code_ready,
        allowed_roles=("Developer",),
    )
    registry.register(
        TOOL_PUBLISH_PR_REVIEW,
        publish_code_ready,
        allowed_roles=("Developer",),
    )
    registry.register(
        TOOL_PUBLISH_DEPLOY_EVENT,
        publish_deploy_event,
        allowed_roles=("QA", "DBA", "CyberSec", "Architect-review", "DevOps"),
    )
    registry.default_session_config = stack  # type: ignore[attr-defined]
    log_event(
        "runtime.tools_registered",
        tools=[
            TOOL_OPENCLAW_SESSIONS_SEND,
            TOOL_PUBLISH_BACKLOG,
            TOOL_PUBLISH_DRAFT_REJECTED,
            TOOL_PUBLISH_CODE_READY,
            TOOL_PUBLISH_PR_REVIEW,
            TOOL_PUBLISH_DEPLOY_EVENT,
        ],
    )
    return registry


def build_runtime_session_sender(registry: ToolRegistry, *, role_name: str, session_key: str):
    stack = getattr(registry, "default_session_config", None)
    session_config = None
    if stack is not None:
        session_config = resolve_openclaw_session_config_for_role(
            session_key=session_key,
            stack=stack,
            role_name=role_name,
        )
    from app.runtime.tool_registry import build_session_sender

    return build_session_sender(registry, role_name=role_name, session_config=session_config)
