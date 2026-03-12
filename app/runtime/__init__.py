"""Superficie publica do runtime principal."""

from .agent_runtime import AgentResult, GatewayOutput, PreparedRun, RedisClient, StreamAgent
from .event_envelope import EventEnvelope, RESERVED_EVENT_FIELDS
from .finops import increment_attempt, should_stop_task
from .logging import log_error, log_event
from .model_provider import RuntimeStackConfig, load_runtime_stack_config, validate_runtime_stack
from .openclaw_assets import OpenClawRoleConfig, get_role_openclaw_config, render_openclaw_context, render_openclaw_message
from .openclaw_client import TOOL_OPENCLAW_SESSIONS_SEND, gateway_call, send_to_session
from .openclaw_session import OpenClawSessionConfig, resolve_openclaw_session_config, resolve_openclaw_session_config_for_role
from .openclaw_output import inspect_openclaw_output, normalize_openclaw_output
from .policies import ExecutionPolicy
from .run_context import RunContext, extract_issue_id
from .stream_worker import payload_to_dict, process_stream_message, run_stream_worker
from .tool_registry import ToolDefinition, ToolRegistry, build_session_sender
from .tools import (
    TOOL_PUBLISH_BACKLOG,
    TOOL_PUBLISH_CODE_READY,
    TOOL_PUBLISH_DEPLOY_EVENT,
    TOOL_PUBLISH_DRAFT_REJECTED,
    TOOL_PUBLISH_PR_REVIEW,
    build_runtime_tool_registry,
    build_runtime_session_sender,
    publish_backlog,
    publish_code_ready,
    publish_deploy_event,
    publish_draft_rejected,
)

__all__ = [
    "AgentResult",
    "GatewayOutput",
    "PreparedRun",
    "RedisClient",
    "StreamAgent",
    "EventEnvelope",
    "RESERVED_EVENT_FIELDS",
    "increment_attempt",
    "should_stop_task",
    "log_error",
    "log_event",
    "RuntimeStackConfig",
    "load_runtime_stack_config",
    "validate_runtime_stack",
    "OpenClawRoleConfig",
    "get_role_openclaw_config",
    "render_openclaw_context",
    "render_openclaw_message",
    "OpenClawSessionConfig",
    "resolve_openclaw_session_config",
    "resolve_openclaw_session_config_for_role",
    "normalize_openclaw_output",
    "inspect_openclaw_output",
    "TOOL_OPENCLAW_SESSIONS_SEND",
    "gateway_call",
    "send_to_session",
    "ExecutionPolicy",
    "RunContext",
    "extract_issue_id",
    "payload_to_dict",
    "process_stream_message",
    "run_stream_worker",
    "ToolDefinition",
    "ToolRegistry",
    "build_session_sender",
    "TOOL_PUBLISH_BACKLOG",
    "TOOL_PUBLISH_DRAFT_REJECTED",
    "TOOL_PUBLISH_CODE_READY",
    "TOOL_PUBLISH_PR_REVIEW",
    "TOOL_PUBLISH_DEPLOY_EVENT",
    "publish_backlog",
    "publish_draft_rejected",
    "publish_code_ready",
    "publish_deploy_event",
    "build_runtime_tool_registry",
    "build_runtime_session_sender",
]
