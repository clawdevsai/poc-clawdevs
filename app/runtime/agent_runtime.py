#!/usr/bin/env python3
"""Contratos minimos para agentes rodando no runtime compartilhado."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from .policies import ExecutionPolicy
from .run_context import RunContext

RedisClient = Any
GatewayOutput = dict | str


@dataclass(slots=True)
class AgentResult:
    status: str = "forwarded"
    status_code: str = "forwarded"
    event_name: str = "agent.forwarded"
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PreparedRun:
    instruction: str | None = None
    should_send: bool = True
    ack_on_exit: bool = True
    result: AgentResult | None = None


@runtime_checkable
class StreamAgent(Protocol):
    role_name: str
    stream_name: str
    consumer_group: str
    consumer_name: str
    session_key: str
    policy: ExecutionPolicy

    def prepare(self, redis_client: RedisClient, ctx: RunContext) -> PreparedRun:
        ...

    def build_instruction(self, redis_client: RedisClient, ctx: RunContext) -> str:
        ...

    def on_success(
        self,
        redis_client: RedisClient,
        ctx: RunContext,
        send_output: GatewayOutput,
    ) -> AgentResult | None:
        ...

    def on_error(self, redis_client: RedisClient, ctx: RunContext | None, error: Exception) -> None:
        ...
