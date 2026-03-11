#!/usr/bin/env python3
"""Bootstrap do conjunto minimo de ferramentas do runtime."""
from __future__ import annotations

from app.runtime.tool_registry import ToolRegistry
from app.runtime.openclaw_client import TOOL_OPENCLAW_SESSIONS_SEND, send_to_session


def build_runtime_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(TOOL_OPENCLAW_SESSIONS_SEND, send_to_session)
    return registry
