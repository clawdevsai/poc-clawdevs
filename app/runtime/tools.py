#!/usr/bin/env python3
"""Bootstrap do conjunto minimo de ferramentas do runtime."""
from __future__ import annotations

from app.runtime.logging import log_event
from app.runtime.model_provider import load_runtime_stack_config, validate_runtime_stack
from app.runtime.tool_registry import ToolRegistry
from app.runtime.openclaw_client import TOOL_OPENCLAW_SESSIONS_SEND, send_to_session


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
    registry.register(TOOL_OPENCLAW_SESSIONS_SEND, send_to_session)
    return registry
