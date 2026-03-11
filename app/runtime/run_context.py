#!/usr/bin/env python3
"""Contexto padrao de execucao para processamento de eventos."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import time
from typing import Any

from .event_envelope import EventEnvelope
from .policies import ExecutionPolicy


ISSUE_ID_KEYS = ("issue_id", "issue", "task_id")


def extract_issue_id(event: dict[str, Any]) -> str | None:
    for key in ISSUE_ID_KEYS:
        value = event.get(key)
        if value:
            return str(value).strip() or None
    return None


@dataclass(slots=True)
class RunContext:
    stream_name: str
    message_id: str
    event: dict[str, Any]
    event_type: str
    issue_id: str | None
    run_id: str
    trace_id: str
    attempt: int
    budget_started_at: float
    policy: ExecutionPolicy
    received_at: str
    envelope: EventEnvelope

    @classmethod
    def from_message(
        cls,
        *,
        stream_name: str,
        message_id: str,
        event: dict[str, Any],
        policy: ExecutionPolicy,
    ) -> "RunContext":
        envelope = EventEnvelope.from_payload(event)
        normalized_event = {
            "type": envelope.event_type,
            **({"issue_id": envelope.issue_id} if envelope.issue_id else {}),
            "run_id": envelope.run_id,
            "trace_id": envelope.trace_id,
            "attempt": envelope.attempt,
            **envelope.payload,
        }
        received_at = datetime.now(timezone.utc).isoformat()
        return cls(
            stream_name=stream_name,
            message_id=message_id,
            event=normalized_event,
            event_type=envelope.event_type,
            issue_id=envelope.issue_id or extract_issue_id(normalized_event),
            run_id=envelope.run_id,
            trace_id=envelope.trace_id,
            attempt=envelope.attempt,
            budget_started_at=envelope.budget_started_at,
            policy=policy,
            received_at=received_at,
            envelope=envelope,
        )

    @property
    def elapsed_runtime_sec(self) -> float:
        return max(0.0, time.time() - self.budget_started_at)

    def exceeded_attempt_budget(self) -> bool:
        return self.attempt > self.policy.max_attempts

    def exceeded_runtime_budget(self) -> bool:
        if self.policy.max_runtime_sec is None:
            return False
        return self.elapsed_runtime_sec > self.policy.max_runtime_sec
