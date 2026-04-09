"""Task performance metrics calculations."""

from __future__ import annotations

from datetime import datetime, timedelta, UTC
from math import ceil

from sqlalchemy import func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Task


class TaskMetricsService:
    """Compute task cycle time and throughput metrics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cycle_time(self, window_minutes: int) -> dict:
        """Return average and p95 cycle time (seconds) for completed tasks."""
        since = datetime.now(UTC).replace(tzinfo=None) - timedelta(
            minutes=window_minutes
        )
        result = await self.session.exec(
            select(Task).where(
                col(Task.status) == "done",
                col(Task.updated_at) >= since,
            )
        )
        durations: list[float] = []
        for task in result.all():
            if task.created_at and task.updated_at:
                delta = (task.updated_at - task.created_at).total_seconds()
                if delta >= 0:
                    durations.append(float(delta))

        if not durations:
            return {
                "cycle_time_avg_seconds": 0.0,
                "cycle_time_p95_seconds": 0.0,
            }

        durations.sort()
        avg = sum(durations) / len(durations)
        p95_index = max(0, ceil(0.95 * len(durations)) - 1)
        p95 = durations[p95_index]
        return {
            "cycle_time_avg_seconds": float(avg),
            "cycle_time_p95_seconds": float(p95),
        }

    async def get_throughput(self, window_minutes: int, group_by: str = "label") -> list[dict]:
        """Return completed task counts grouped by label."""
        if group_by != "label":
            raise ValueError("group_by must be 'label'")

        since = datetime.now(UTC).replace(tzinfo=None) - timedelta(
            minutes=window_minutes
        )
        stmt = (
            select(Task.label, func.count(Task.id))
            .where(col(Task.status) == "done", col(Task.updated_at) >= since)
            .group_by(Task.label)
        )
        rows = (await self.session.exec(stmt)).all()
        items: list[dict] = []
        for label, count in rows:
            group = label if label else "unlabeled"
            items.append({"group": group, "completed_count": int(count)})
        return items
