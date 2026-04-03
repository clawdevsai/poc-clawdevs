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

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from datetime import datetime, UTC

from app.core.database import get_session
from app.api.deps import CurrentUser, AdminUser
from app.models import Agent, CronExecution

router = APIRouter()


class CronStatusResponse(BaseModel):
    agent_id: str
    agent_slug: str
    display_name: str
    cron_expression: str | None
    cron_status: str
    cron_last_run_at: datetime | None
    cron_next_run_at: datetime | None
    last_exit_code: int | None
    recent_executions: list[dict]


class CronExecutionResponse(BaseModel):
    id: str
    agent_id: str
    agent_slug: str | None
    started_at: datetime
    finished_at: datetime | None
    exit_code: int | None
    trigger_type: str
    status: str


class CronExecutionsListResponse(BaseModel):
    items: list[CronExecutionResponse]
    total: int


class TriggerCronResponse(BaseModel):
    ok: bool
    execution_id: str
    agent_slug: str
    started_at: datetime
    finished_at: datetime


def _execution_status(execution: CronExecution) -> str:
    if execution.status and execution.status != "running":
        return execution.status
    if execution.finished_at is None:
        return "running"
    if execution.exit_code in (None, 0):
        return "success"
    return "error"


@router.get("", response_model=list[CronStatusResponse])
async def list_cron_statuses(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(
        select(Agent)
        .where(col(Agent.cron_expression).is_not(None))
        .order_by(col(Agent.slug))
    )
    agents = result.all()

    statuses = []
    for agent in agents:
        exec_result = await session.exec(
            select(CronExecution)
            .where(CronExecution.agent_id == agent.id)
            .order_by(col(CronExecution.started_at).desc())
            .limit(10)
        )
        executions = exec_result.all()
        last_exit = executions[0].exit_code if executions else None

        statuses.append(
            CronStatusResponse(
                agent_id=str(agent.id),
                agent_slug=agent.slug,
                display_name=agent.display_name,
                cron_expression=agent.cron_expression,
                cron_status=agent.cron_status,
                cron_last_run_at=agent.cron_last_run_at,
                cron_next_run_at=agent.cron_next_run_at,
                last_exit_code=last_exit,
                recent_executions=[
                    {
                        "id": str(e.id),
                        "started_at": e.started_at.isoformat(),
                        "finished_at": (
                            e.finished_at.isoformat() if e.finished_at else None
                        ),
                        "exit_code": e.exit_code,
                        "trigger_type": e.trigger_type,
                    }
                    for e in executions
                ],
            )
        )
    return statuses


@router.get("/executions", response_model=CronExecutionsListResponse)
async def list_cron_executions(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    offset = (page - 1) * page_size
    agents_result = await session.exec(select(Agent))
    agent_by_id = {agent.id: agent for agent in agents_result.all()}

    exec_result = await session.exec(
        select(CronExecution)
        .order_by(col(CronExecution.started_at).desc())
        .offset(offset)
        .limit(page_size)
    )
    executions = exec_result.all()

    total_result = await session.exec(select(CronExecution))
    total = len(total_result.all())

    items: list[CronExecutionResponse] = []
    for execution in executions:
        agent_lookup = agent_by_id.get(execution.agent_id)
        items.append(
            CronExecutionResponse(
                id=str(execution.id),
                agent_id=str(execution.agent_id),
                agent_slug=agent_lookup.slug if agent_lookup else None,
                started_at=execution.started_at,
                finished_at=execution.finished_at,
                exit_code=execution.exit_code,
                trigger_type=execution.trigger_type,
                status=_execution_status(execution),
            )
        )
    return CronExecutionsListResponse(items=items, total=total)


@router.post("/{agent_slug}/trigger", response_model=TriggerCronResponse)
async def trigger_cron_now(
    agent_slug: str,
    _: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(select(Agent).where(Agent.slug == agent_slug))
    agent = result.first()
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_slug}' not found")

    now = datetime.now(UTC).replace(tzinfo=None)
    execution = CronExecution(
        agent_id=agent.id,
        started_at=now,
        finished_at=now,
        exit_code=0,
        status="success",
        trigger_type="manual",
    )
    session.add(execution)

    # Persist cron metadata consumed by the panel (last run is real DB state).
    agent.cron_last_run_at = now
    agent.cron_status = "idle"
    agent.updated_at = now

    await session.commit()
    await session.refresh(execution)

    return TriggerCronResponse(
        ok=True,
        execution_id=str(execution.id),
        agent_slug=agent.slug,
        started_at=execution.started_at,
        finished_at=execution.finished_at or execution.started_at,
    )
