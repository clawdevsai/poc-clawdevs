"""Parallelism gating with adaptive thresholds."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from sqlmodel import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import ActivityEvent, Task

PARALLELISM_EVENT_TYPE = "task.parallelism_blocked"
THRESHOLD_EVENT_TYPE = "task.parallelism_thresholds_updated"


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    k = (len(values_sorted) - 1) * percentile
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values_sorted[int(k)]
    d0 = values_sorted[f] * (c - k)
    d1 = values_sorted[c] * (k - f)
    return d0 + d1


async def fetch_parallelism_metrics(session, lookback: int) -> dict:
    result = await session.exec(
        select(Task)
        .where(Task.status == "done")
        .order_by(Task.updated_at.desc())
        .limit(lookback)
    )
    tasks = result.all()
    costs = [float(t.actual_cost or 0.0) for t in tasks]
    latencies = []
    for task in tasks:
        if task.created_at and task.updated_at:
            latencies.append((task.updated_at - task.created_at).total_seconds())

    return {
        "sample_size": len(tasks),
        "avg_cost": sum(costs) / len(costs) if costs else 0.0,
        "avg_latency_seconds": sum(latencies) / len(latencies) if latencies else 0.0,
        "p95_cost": _percentile(costs, 0.95) if costs else 0.0,
        "p95_latency_seconds": _percentile(latencies, 0.95) if latencies else 0.0,
    }


def compute_adaptive_thresholds(metrics: dict, settings) -> dict:
    if metrics.get("sample_size", 0) < settings.ORCH_PARALLELISM_ADAPTIVE_MIN_SAMPLES:
        return {
            "cost_threshold": settings.ORCH_PARALLELISM_COST_THRESHOLD,
            "latency_threshold_seconds": settings.ORCH_PARALLELISM_LATENCY_THRESHOLD_SECONDS,
        }

    adaptive_cost = max(
        settings.ORCH_PARALLELISM_COST_THRESHOLD,
        metrics.get("avg_cost", 0.0) * settings.ORCH_PARALLELISM_COST_MULTIPLIER,
        metrics.get("p95_cost", 0.0),
    )
    adaptive_latency = max(
        settings.ORCH_PARALLELISM_LATENCY_THRESHOLD_SECONDS,
        metrics.get("avg_latency_seconds", 0.0)
        * settings.ORCH_PARALLELISM_LATENCY_MULTIPLIER,
        metrics.get("p95_latency_seconds", 0.0),
    )
    return {
        "cost_threshold": float(adaptive_cost),
        "latency_threshold_seconds": float(adaptive_latency),
    }


async def persist_adaptive_thresholds(
    session, *, thresholds: dict, sample_size: int
) -> None:
    settings = get_settings()
    thresholds_path = Path(settings.openclaw_data_path) / "parallelism_thresholds.json"
    thresholds_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "cost_threshold": thresholds.get("cost_threshold"),
        "latency_threshold_seconds": thresholds.get("latency_threshold_seconds"),
        "sample_size": sample_size,
    }
    thresholds_path.write_text(json.dumps(payload), encoding="utf-8")

    event = ActivityEvent(
        event_type=THRESHOLD_EVENT_TYPE,
        entity_type="system",
        entity_id="parallelism",
        payload=payload,
    )
    session.add(event)


def should_allow_parallelism(in_progress_count: int, metrics: dict, settings) -> bool:
    if settings.ORCH_PARALLELISM_FORCE:
        return True
    if not settings.ORCH_PARALLELISM_ENABLED:
        return False
    if in_progress_count == 0:
        return True
    return (
        metrics.get("avg_cost", 0.0) <= settings.ORCH_PARALLELISM_COST_THRESHOLD
        and metrics.get("avg_latency_seconds", 0.0)
        <= settings.ORCH_PARALLELISM_LATENCY_THRESHOLD_SECONDS
    )


async def evaluate_parallelism_gate(session, in_progress_count: int) -> tuple[bool, str]:
    settings = get_settings()
    metrics = await fetch_parallelism_metrics(session, settings.ORCH_PARALLELISM_LOOKBACK_TASKS)

    if settings.ORCH_PARALLELISM_ADAPTIVE_ENABLED:
        thresholds = compute_adaptive_thresholds(metrics, settings)
        settings.ORCH_PARALLELISM_COST_THRESHOLD = thresholds["cost_threshold"]
        settings.ORCH_PARALLELISM_LATENCY_THRESHOLD_SECONDS = thresholds[
            "latency_threshold_seconds"
        ]
        await persist_adaptive_thresholds(
            session, thresholds=thresholds, sample_size=metrics.get("sample_size", 0)
        )

    if settings.ORCH_PARALLELISM_FORCE:
        return True, "force_enabled"
    if not settings.ORCH_PARALLELISM_ENABLED:
        return False, "disabled"
    if in_progress_count == 0:
        return True, "sequential_allowed"
    allowed = should_allow_parallelism(in_progress_count, metrics, settings)
    return (True, "thresholds_met") if allowed else (False, "thresholds_exceeded")


async def evaluate_parallelism_gate_sync(in_progress_count: int) -> tuple[bool, str]:
    async with AsyncSessionLocal() as session:
        return await evaluate_parallelism_gate(session, in_progress_count)
