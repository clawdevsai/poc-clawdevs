# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import col, select
from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta, UTC
from uuid import UUID

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import Metric, Session
from app.services.context_metrics import (
    compute_overview_metrics,
    DEFAULT_WINDOW_MINUTES,
    validate_window_minutes,
)
from app.services.task_metrics import TaskMetricsService

router = APIRouter()


def _to_naive_utc(dt: datetime | None) -> datetime | None:
    """Convert any datetime to naive UTC datetime."""
    if dt is None:
        return None
    # If it has timezone info, convert to UTC and strip it
    if dt.tzinfo is not None:
        return dt.astimezone(UTC).replace(tzinfo=None)
    # If it's already naive, assume it's UTC
    return dt


class OverviewMetrics(BaseModel):
    active_agents: int
    pending_approvals: int
    open_tasks: int
    tokens_24h: float
    tokens_consumed_total: float
    tokens_consumed_avg_per_task: float
    backlog_count: int
    tasks_in_progress: int
    tasks_completed: int


class CycleTimeResponse(BaseModel):
    cycle_time_avg_seconds: float
    cycle_time_p95_seconds: float
    window_minutes: int


class ThroughputItem(BaseModel):
    group: str
    completed_count: int


class ThroughputResponse(BaseModel):
    window_minutes: int
    group_by: str
    items: list[ThroughputItem]


class MetricResponse(BaseModel):
    metric_type: str
    value: float
    period_start: datetime
    period_end: datetime | None
    agent_id: str | None


class MetricsListResponse(BaseModel):
    items: list[MetricResponse]
    total: int


@router.get("", response_model=MetricsListResponse)
async def list_metrics(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    metric_type: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=90),
    hours: int = Query(24, ge=1, le=168),
    interval_minutes: int = Query(1, ge=1, le=60),
    agent_id: Optional[str] = Query(None),
):
    since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

    # Fallback for dashboard usage chart: derive sessions/day straight from sessions table.
    if metric_type == "sessions":
        day_start = since.replace(hour=0, minute=0, second=0, microsecond=0)
        day_bucket = func.date_trunc("day", Session.created_at)
        query = (
            select(day_bucket, func.count(Session.id))
            .where(col(Session.created_at) >= day_start)
            .group_by(day_bucket)
            .order_by(day_bucket.asc())
        )
        rows = (await session.exec(query)).all()
        count_by_day: dict[datetime, float] = {}
        for bucket, count in rows:
            if bucket is None:
                continue
            # Normalize bucket datetime to naive UTC
            normalized_bucket = _to_naive_utc(bucket)
            if normalized_bucket is not None:
                count_by_day[normalized_bucket] = float(count)

        start_day = day_start
        today = (
            datetime.now(timezone.utc)
            .replace(tzinfo=None)
            .replace(hour=0, minute=0, second=0, microsecond=0)
        )
        session_items: list[MetricResponse] = []
        cursor = start_day
        while cursor <= today:
            session_items.append(
                MetricResponse(
                    metric_type="sessions",
                    value=count_by_day.get(cursor, 0.0),
                    period_start=cursor,
                    period_end=cursor + timedelta(days=1),
                    agent_id=None,
                )
            )
            cursor = cursor + timedelta(days=1)

        return MetricsListResponse(items=session_items, total=len(session_items))

    # Real-time active sessions time series (last N hours, bucketed by minute interval).
    if metric_type == "active_sessions":
        bucket = timedelta(minutes=interval_minutes)
        now = datetime.now(timezone.utc).replace(tzinfo=None, second=0, microsecond=0)
        series_start = now - timedelta(hours=hours)
        points = int((now - series_start) / bucket) + 1

        # We only need sessions that could intersect the window.
        session_query = select(Session).where(
            func.coalesce(Session.last_active_at, Session.created_at)
            >= (series_start - timedelta(hours=24))
        )
        session_rows = (await session.exec(session_query)).all()

        diffs = [0] * (points + 1)

        def _to_index(ts: datetime) -> int:
            return int((ts - series_start).total_seconds() // (interval_minutes * 60))

        for sess in session_rows:
            start = _to_naive_utc(
                sess.started_at or sess.created_at or sess.last_active_at
            )
            if start is None:
                continue

            if sess.status == "active":
                end = now
            else:
                end = _to_naive_utc(sess.ended_at or sess.last_active_at or start)

            if end < series_start or start > now:
                continue

            start_clamped = max(start, series_start)
            end_clamped = min(end, now)
            start_idx = max(0, min(points - 1, _to_index(start_clamped)))
            end_idx = max(0, min(points - 1, _to_index(end_clamped)))

            if start_idx > end_idx:
                continue

            diffs[start_idx] += 1
            if end_idx + 1 < len(diffs):
                diffs[end_idx + 1] -= 1

        active_items: list[MetricResponse] = []
        current = 0
        for i in range(points):
            current += diffs[i]
            period_start = series_start + (bucket * i)
            active_items.append(
                MetricResponse(
                    metric_type="active_sessions",
                    value=float(max(current, 0)),
                    period_start=period_start,
                    period_end=period_start + bucket,
                    agent_id=None,
                )
            )

        return MetricsListResponse(items=active_items, total=len(active_items))

    metric_query = (
        select(Metric)
        .where(col(Metric.period_start) >= since)
        .order_by(col(Metric.period_start).asc())
    )
    if metric_type:
        metric_query = metric_query.where(col(Metric.metric_type) == metric_type)
    if agent_id:
        metric_query = metric_query.where(col(Metric.agent_id) == UUID(agent_id))

    result = await session.exec(metric_query)
    metrics = result.all()
    items = [
        MetricResponse(
            metric_type=m.metric_type,
            value=m.value,
            period_start=m.period_start,
            period_end=m.period_end,
            agent_id=str(m.agent_id) if m.agent_id else None,
        )
        for m in metrics
    ]
    return MetricsListResponse(items=items, total=len(items))


@router.get("/overview", response_model=OverviewMetrics)
async def overview_metrics(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    window_minutes: int = Query(DEFAULT_WINDOW_MINUTES),
):
    try:
        validate_window_minutes(window_minutes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = await compute_overview_metrics(session, window_minutes)
    return OverviewMetrics(**payload)


@router.get("/cycle-time", response_model=CycleTimeResponse)
async def cycle_time_metrics(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    window_minutes: int = Query(DEFAULT_WINDOW_MINUTES),
):
    try:
        validate_window_minutes(window_minutes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = TaskMetricsService(session)
    payload = await service.get_cycle_time(window_minutes)
    return CycleTimeResponse(window_minutes=window_minutes, **payload)


@router.get("/throughput", response_model=ThroughputResponse)
async def throughput_metrics(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    window_minutes: int = Query(DEFAULT_WINDOW_MINUTES),
    group_by: str = Query("label"),
):
    try:
        validate_window_minutes(window_minutes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    service = TaskMetricsService(session)
    try:
        items = await service.get_throughput(window_minutes, group_by=group_by)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ThroughputResponse(window_minutes=window_minutes, group_by=group_by, items=items)
