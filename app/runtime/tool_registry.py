#!/usr/bin/env python3
"""Registry minimo de ferramentas do runtime."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from typing import Callable

from .agent_runtime import GatewayOutput
from .openclaw_session import OpenClawSessionConfig

ToolHandler = Callable[..., tuple[bool, GatewayOutput]]


@dataclass(slots=True)
class ToolDefinition:
    name: str
    handler: ToolHandler
    allowed_roles: tuple[str, ...] = ()

    def execute(self, **kwargs) -> tuple[bool, GatewayOutput]:
        return self.handler(**kwargs)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, name: str, handler: ToolHandler, *, allowed_roles: tuple[str, ...] = ()) -> None:
        self._tools[name] = ToolDefinition(name=name, handler=handler, allowed_roles=allowed_roles)

    def execute(self, name: str, *, role_name: str | None = None, **kwargs) -> tuple[bool, GatewayOutput]:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"tool nao registrada: {name}")
        if tool.allowed_roles and role_name not in tool.allowed_roles:
            raise PermissionError(f"role sem permissao para tool {name}: {role_name}")
        return tool.execute(**kwargs)

    def list_tools_for_role(self, role_name: str) -> tuple[str, ...]:
        tools = []
        for name, tool in self._tools.items():
            if not tool.allowed_roles or role_name in tool.allowed_roles:
                tools.append(name)
        return tuple(sorted(tools))


def build_session_sender(
    registry: ToolRegistry,
    *,
    role_name: str,
    session_config: OpenClawSessionConfig | None = None,
) -> Callable[[str, str, int], tuple[bool, GatewayOutput]]:
    def sender(session_key: str, message: str, timeout_sec: int) -> tuple[bool, GatewayOutput]:
        ok, output = registry.execute(
            "openclaw.sessions.send",
            role_name=role_name,
            session_key=session_key,
            message=message,
            timeout_sec=timeout_sec,
            session_config=session_config,
        )
        fallback_model = (getattr(session_config, "fallback_model", "") or "").strip() if session_config else ""
        if ok or not fallback_model:
            return ok, output
        fallback_config = replace(session_config, model=fallback_model, fallback_model="")
        return registry.execute(
            "openclaw.sessions.send",
            role_name=role_name,
            session_key=session_key,
            message=message,
            timeout_sec=timeout_sec,
            session_config=fallback_config,
        )

    sender.role_name = role_name  # type: ignore[attr-defined]
    sender.allowed_tools = registry.list_tools_for_role(role_name)  # type: ignore[attr-defined]
    sender.session_config = session_config  # type: ignore[attr-defined]
    return sender
