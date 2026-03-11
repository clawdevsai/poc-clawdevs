#!/usr/bin/env python3
"""Registry minimo de ferramentas do runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .agent_runtime import GatewayOutput

ToolHandler = Callable[..., tuple[bool, GatewayOutput]]


@dataclass(slots=True)
class ToolDefinition:
    name: str
    handler: ToolHandler

    def execute(self, **kwargs) -> tuple[bool, GatewayOutput]:
        return self.handler(**kwargs)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, name: str, handler: ToolHandler) -> None:
        self._tools[name] = ToolDefinition(name=name, handler=handler)

    def execute(self, name: str, **kwargs) -> tuple[bool, GatewayOutput]:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"tool nao registrada: {name}")
        return tool.execute(**kwargs)


def build_session_sender(registry: ToolRegistry) -> Callable[[str, str, int], tuple[bool, GatewayOutput]]:
    def sender(session_key: str, message: str, timeout_sec: int) -> tuple[bool, GatewayOutput]:
        return registry.execute(
            "openclaw.sessions.send",
            session_key=session_key,
            message=message,
            timeout_sec=timeout_sec,
        )

    return sender
