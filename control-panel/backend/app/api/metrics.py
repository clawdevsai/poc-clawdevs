from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import Metric, Approval, Task, Agent

router = APIRouter()


class OverviewMetrics(BaseModel):
    active_agents: int
    pending_approvals: int
    open_tasks: int
    tokens_24h: float


@router.get("/overview", response_model=OverviewMetrics)
async def overview_metrics(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    agents_result = await session.exec(select(Agent).where(Agent.status == "active"))
    active_agents = len(agents_result.all())

    approvals_result = await session.exec(
        select(Approval).where(Approval.status == "pending")
    )
    pending_approvals = len(approvals_result.all())

    tasks_result = await session.exec(
        select(Task).where(Task.status.in_(["inbox", "in_progress", "review"]))
    )
    open_tasks = len(tasks_result.all())

    metrics_result = await session.exec(
        select(Metric).where(
            Metric.metric_type == "tokens_used",
            Metric.period_start >= since,
        )
    )
    tokens_24h = sum(m.value for m in metrics_result.all())

    return OverviewMetrics(
        active_agents=active_agents,
        pending_approvals=pending_approvals,
        open_tasks=open_tasks,
        tokens_24h=tokens_24h,
    )
