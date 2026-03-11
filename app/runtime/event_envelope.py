#!/usr/bin/env python3
"""Envelope minimo para trafego interno entre governanca, runtime e agentes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4


RESERVED_EVENT_FIELDS = frozenset({"type", "issue_id", "run_id", "trace_id", "attempt", "budget_started_at"})


@dataclass(slots=True)
class EventEnvelope:
    event_type: str
    payload: dict[str, Any]
    issue_id: str | None
    run_id: str
    trace_id: str
    attempt: int
    budget_started_at: float

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "EventEnvelope":
        run_id = str(payload.get("run_id") or uuid4())
        trace_id = str(payload.get("trace_id") or run_id)
        attempt = int(payload.get("attempt") or 1)
        budget_started_at = float(payload.get("budget_started_at") or 0.0)
        if budget_started_at <= 0:
            from time import time as now

            budget_started_at = now()
        issue_id = payload.get("issue_id")
        event_type = str(payload.get("type") or "unknown")
        data = {k: v for k, v in payload.items() if k not in RESERVED_EVENT_FIELDS}
        return cls(
            event_type=event_type,
            payload=data,
            issue_id=str(issue_id).strip() if issue_id else None,
            run_id=run_id,
            trace_id=trace_id,
            attempt=attempt,
            budget_started_at=budget_started_at,
        )

    def to_payload(self) -> dict[str, str]:
        flattened = {
            "type": self.event_type,
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "attempt": str(self.attempt),
            "budget_started_at": str(self.budget_started_at),
        }
        if self.issue_id:
            flattened["issue_id"] = self.issue_id
        for key, value in self.payload.items():
            flattened[key] = "" if value is None else str(value)
        return flattened

    def next_attempt_payload(self, **extra_payload: Any) -> dict[str, str]:
        next_payload = dict(self.payload)
        next_payload.update(extra_payload)
        return EventEnvelope(
            event_type=self.event_type,
            payload=next_payload,
            issue_id=self.issue_id,
            run_id=self.run_id,
            trace_id=self.trace_id,
            attempt=self.attempt + 1,
            budget_started_at=self.budget_started_at,
        ).to_payload()
