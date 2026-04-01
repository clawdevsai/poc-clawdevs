"""
OpenClaw Hooks Package
=====================

Lifecycle event handlers for OpenClaw agent execution.

Hooks are extension points where plugins/middleware can intercept
and modify agent behavior at specific lifecycle stages.

Available Hooks:
- message.received: User sends message
- session.loaded: Session retrieved from storage
- context.loaded: Context window assembled
- prompt.built: System prompt assembled
- before.model: Ready to call LLM
- model.response: LLM returned response
- tools.available: Tool list assembled
- tool.selected: Agent chose tool to invoke
- tool.executed: Tool returned result ← CONTEXT MODE COMPRESSION
- response.ready: Final response assembled
- response.sent: Response delivered to user
- session.saved: Session persisted
- error.occurred: Exception during execution

See HOOKS_SPECIFICATION.md for full documentation.
"""

from .tool_executed import handle as tool_executed_handler
from .tool_executed import get_compression_metrics

__all__ = [
    "tool_executed_handler",
    "get_compression_metrics",
]
