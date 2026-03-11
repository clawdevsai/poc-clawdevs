#!/usr/bin/env python3
"""Bootstrap do conjunto minimo de ferramentas do runtime."""
from __future__ import annotations

from typing import Any

from app.runtime.logging import log_event
from app.runtime.model_provider import load_runtime_stack_config, validate_runtime_stack
from app.runtime.openclaw_session import resolve_openclaw_session_config_for_role
from app.runtime.tool_registry import ToolRegistry
from app.runtime.openclaw_client import TOOL_OPENCLAW_SESSIONS_SEND, send_to_session
from app.shared.issue_state import STATE_DEPLOYED, STATE_READY, STATE_REFINAMENTO, set_issue_state

TOOL_PUBLISH_BACKLOG = "redis.publish_backlog"
TOOL_PUBLISH_DRAFT_REJECTED = "redis.publish_draft_rejected"
TOOL_PUBLISH_CODE_READY = "redis.publish_code_ready"
TOOL_PUBLISH_DEPLOY_EVENT = "redis.publish_deploy_event"


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
) -> tuple[bool, dict[str, str]]:
    payload = {
        "issue_id": issue_id,
        "branch": branch,
        "repo": repo,
    }
    redis_client.xadd("code:ready", payload)
    return True, {"stream": "code:ready", "issue_id": issue_id, "branch": branch}


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
        allowed_roles=("PO", "Architect-draft", "Developer", "DevOps"),
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
        TOOL_PUBLISH_DEPLOY_EVENT,
        publish_deploy_event,
        allowed_roles=("DevOps",),
    )
    registry.default_session_config = stack  # type: ignore[attr-defined]
    log_event(
        "runtime.tools_registered",
        tools=[
            TOOL_OPENCLAW_SESSIONS_SEND,
            TOOL_PUBLISH_BACKLOG,
            TOOL_PUBLISH_DRAFT_REJECTED,
            TOOL_PUBLISH_CODE_READY,
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
