#!/usr/bin/env python3
"""Base simples para agentes do runtime principal."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
from typing import Any

from app.bootstrap import bootstrap_paths
from app.runtime import AgentResult, ExecutionPolicy, PreparedRun, RunContext


bootstrap_paths()


@dataclass(slots=True)
class AgentSettings:
    role_name: str
    stream_name: str
    consumer_group: str
    consumer_name: str
    session_key: str
    policy: ExecutionPolicy


class BaseRoleAgent(ABC):
    settings: AgentSettings

    @property
    def role_name(self) -> str:
        return self.settings.role_name

    @property
    def stream_name(self) -> str:
        return self.settings.stream_name

    @property
    def consumer_group(self) -> str:
        return self.settings.consumer_group

    @property
    def consumer_name(self) -> str:
        return self.settings.consumer_name

    @property
    def session_key(self) -> str:
        return self.settings.session_key

    @property
    def policy(self) -> ExecutionPolicy:
        return self.settings.policy

    def prepare(self, redis_client: Any, ctx: RunContext) -> PreparedRun:
        return PreparedRun()

    @abstractmethod
    def build_instruction(self, redis_client: Any, ctx: RunContext) -> str:
        raise NotImplementedError

    def on_success(self, redis_client: Any, ctx: RunContext, send_output: dict | str) -> AgentResult:
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="agent.forwarded",
            summary=f"[{self.role_name}] XACK {self.stream_name} {ctx.message_id}",
            metadata={"run_id": ctx.run_id},
        )

    def on_error(self, redis_client: Any, ctx: RunContext | None, error: Exception) -> None:
        message_id = ctx.message_id if ctx else "unknown"
        print(f"[{self.role_name}] Erro ao processar {message_id}: {error}", file=sys.stderr)
