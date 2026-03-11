"""Superficie publica do runtime principal."""

from .agent_runtime import AgentResult, GatewayOutput, PreparedRun, RedisClient, StreamAgent
from .event_envelope import EventEnvelope, RESERVED_EVENT_FIELDS
from .finops import increment_attempt, should_stop_task
from .logging import log_error, log_event
from .openclaw_client import TOOL_OPENCLAW_SESSIONS_SEND, gateway_call, send_to_session
from .policies import ExecutionPolicy
from .run_context import RunContext, extract_issue_id
from .stream_worker import payload_to_dict, process_stream_message, run_stream_worker
from .tool_registry import ToolDefinition, ToolRegistry, build_session_sender
from .tools import build_runtime_tool_registry

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
    "build_runtime_tool_registry",
]
