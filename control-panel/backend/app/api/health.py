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

"""
Health and Failure Detection API Endpoints

Provides task health monitoring, failure tracking, and escalation status.
"""

import logging
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models.task import Task
from app.services.failure_detector import FailureDetector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


class TaskHealthResponse:
    """Response model for task health status."""

    task_id: str
    status: str  # healthy|unhealthy|failed|escalated
    failure_count: int
    consecutive_failures: int
    last_error: Optional[str]
    last_failed_at: Optional[str]
    escalated_to_agent_id: Optional[str]
    escalation_reason: Optional[str]


class HealthSummaryResponse:
    """Response model for health summary."""

    total_tasks: int
    healthy_tasks: int
    unhealthy_tasks: int
    failed_tasks: int
    escalated_tasks: int
    health_percentage: float


@router.get("/tasks/{task_id}")
async def get_task_health(
    task_id: UUID,
    _: CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get health status of a specific task.

    Args:
        task_id: UUID of the task to monitor

    Returns:
        Task health status with failure count and escalation info

    Raises:
        404: Task not found
    """
    if not task_id:
        raise HTTPException(status_code=400, detail="Invalid task_id format")

    detector = FailureDetector(session)
    health = await detector.get_task_health(task_id)

    if health["status"] == "unknown":
        raise HTTPException(status_code=404, detail="Task not found")

    return health


@router.get("/summary")
async def get_health_summary(
    _: CurrentUser,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get overall health summary across all tasks."""
    tasks = (await session.exec(select(Task))).all()

    healthy_count = 0
    unhealthy_count = 0
    failed_count = 0
    escalated_count = 0

    for task in tasks:
        if task.escalated_to_agent_id:
            escalated_count += 1
        elif task.consecutive_failures >= 3:
            failed_count += 1
        elif task.consecutive_failures > 0:
            unhealthy_count += 1
        else:
            healthy_count += 1

    total = len(tasks)
    (healthy_count / total * 100) if total > 0 else 0

    return {
        "healthy": healthy_count,
        "stalled": unhealthy_count,
        "failed": failed_count,
        "blocked": escalated_count,
    }


@router.get("/failures")
async def get_failed_tasks(
    _: CurrentUser,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> dict:
    """Get list of failed/unhealthy tasks."""
    statement = (
        select(Task)
        .where(col(Task.failure_count) > 0)
        .order_by(col(Task.last_failed_at).desc())
        .offset(offset)
        .limit(limit)
    )

    tasks = (await session.exec(statement)).all()
    total = (await session.exec(select(Task).where(col(Task.failure_count) > 0))).all()

    return {
        "total": len(total),
        "offset": offset,
        "limit": limit,
        "tasks": [
            {
                "id": str(task.id),
                "title": task.title,
                "status": task.status,
                "failure_count": task.failure_count,
                "consecutive_failures": task.consecutive_failures,
                "last_error": task.last_error,
                "last_failed_at": (
                    task.last_failed_at.isoformat() if task.last_failed_at else None
                ),
                "escalated": task.escalated_to_agent_id is not None,
            }
            for task in tasks
        ],
    }


@router.get("/escalations")
async def get_escalated_tasks(
    _: CurrentUser,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(100, ge=1, le=1000),
) -> dict:
    """Get list of escalated tasks."""
    statement = (
        select(Task)
        .where(col(Task.escalated_to_agent_id).is_not(None))
        .order_by(col(Task.escalated_at).desc())
        .limit(limit)
    )

    tasks = (await session.exec(statement)).all()
    total = (
        await session.exec(
            select(Task).where(col(Task.escalated_to_agent_id).is_not(None))
        )
    ).all()

    return {
        "total": len(total),
        "limit": limit,
        "escalations": [
            {
                "task_id": str(task.id),
                "title": task.title,
                "escalated_to_agent_id": str(task.escalated_to_agent_id),
                "escalation_reason": task.escalation_reason,
                "escalated_at": (
                    task.escalated_at.isoformat() if task.escalated_at else None
                ),
                "failure_count": task.failure_count,
            }
            for task in tasks
        ],
    }
