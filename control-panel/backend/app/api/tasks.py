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

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_session
from app.models import ActivityEvent, Task
from app.services.failure_detector import FailureDetector
from app.services.task_workflow import (
    WORKFLOW_COMPLETED,
    WORKFLOW_FAILED,
    WORKFLOW_QUEUED_TO_CEO,
    enqueue_task_for_ceo,
    get_agent_slug_map,
    get_ceo_agent,
    log_task_event,
)

router = APIRouter()


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: str
    priority: str
    label: str | None
    assigned_agent_id: str | None
    assigned_agent_slug: str | None
    github_issue_number: int | None
    github_issue_url: str | None
    github_repo: str | None
    due_at: datetime | None
    workflow_state: str
    workflow_last_error: str | None
    workflow_attempts: int
    created_at: datetime
    updated_at: datetime


class TaskTimelineEventResponse(BaseModel):
    id: str
    event_type: str
    from_agent_slug: str | None
    to_agent_slug: str | None
    description: str
    created_at: datetime
    payload: dict | None


class TaskTimelineResponse(BaseModel):
    items: list[TaskTimelineEventResponse]
    total: int


class TaskFailureResponse(BaseModel):
    message: str | None
    stack_trace: str | None
    evidence: list[str]


class CreateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    assigned_agent_id: str | None = None  # Ignored: all tasks start with CEO.
    label: str | None = None
    github_repo: str | None = None


class UpdateTaskRequest(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigned_agent_id: str | None = None
    title: str | None = None
    description: str | None = None
    label: str | None = None
    github_repo: str | None = None


class TasksListResponse(BaseModel):
    items: list[TaskResponse]
    total: int


def _to_task_response(task: Task, slug_map: dict[str, str]) -> TaskResponse:
    assigned_id = str(task.assigned_agent_id) if task.assigned_agent_id else None
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        label=task.label,
        assigned_agent_id=assigned_id,
        assigned_agent_slug=slug_map.get(assigned_id) if assigned_id else None,
        github_issue_number=task.github_issue_number,
        github_issue_url=task.github_issue_url,
        github_repo=task.github_repo,
        due_at=task.due_at,
        workflow_state=task.workflow_state,
        workflow_last_error=task.workflow_last_error,
        workflow_attempts=task.workflow_attempts,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


async def _load_slug_map_for_tasks(
    session: AsyncSession,
    tasks: list[Task],
) -> dict[str, str]:
    agent_ids = {t.assigned_agent_id for t in tasks if t.assigned_agent_id}
    return await get_agent_slug_map(
        session, {agent_id for agent_id in agent_ids if agent_id}
    )


@router.get("", response_model=TasksListResponse)
async def list_tasks(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    status: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
):
    query = select(Task).order_by(col(Task.created_at).desc())
    if status:
        query = query.where(Task.status == status)
    if label:
        query = query.where(Task.label == label)

    result = await session.exec(query)
    tasks = result.all()
    slug_map = await _load_slug_map_for_tasks(session, tasks)
    items = [_to_task_response(t, slug_map) for t in tasks]
    return TasksListResponse(items=items, total=len(items))


@router.get("/{task_id}/timeline", response_model=TaskTimelineResponse)
async def task_timeline(
    task_id: UUID,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    result = await session.exec(
        select(ActivityEvent)
        .where(ActivityEvent.entity_type == "task")
        .where(ActivityEvent.entity_id == str(task_id))
        .order_by(col(ActivityEvent.created_at).asc())
    )
    events = result.all()

    items: list[TaskTimelineEventResponse] = []
    for event in events:
        payload = event.payload or {}
        description = (
            payload.get("description")
            if isinstance(payload, dict) and payload.get("description")
            else event.event_type
        )
        items.append(
            TaskTimelineEventResponse(
                id=str(event.id),
                event_type=event.event_type,
                from_agent_slug=(
                    payload.get("from_agent_slug")
                    if isinstance(payload, dict)
                    else None
                ),
                to_agent_slug=(
                    payload.get("to_agent_slug") if isinstance(payload, dict) else None
                ),
                description=description,
                created_at=event.created_at,
                payload=payload if isinstance(payload, dict) else None,
            )
        )

    return TaskTimelineResponse(items=items, total=len(items))


@router.get("/{task_id}/failure", response_model=TaskFailureResponse)
async def task_failure_detail(
    task_id: UUID,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    detector = FailureDetector(session)
    detail = await detector.get_failure_detail(task_id)
    if detail is None:
        return TaskFailureResponse(message=None, stack_trace=None, evidence=[])

    return TaskFailureResponse(
        message=detail.get("message"),
        stack_trace=detail.get("stack_trace"),
        evidence=detail.get("evidence") or [],
    )


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    body: CreateTaskRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    import logging
    from datetime import timezone

    logger = logging.getLogger(__name__)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    ceo_agent = await get_ceo_agent(session)

    if ceo_agent is None:
        logger.warning("CEO agent not found, attempting sync_agents...")
        try:
            from app.services.agent_sync import sync_agents

            await sync_agents(session)
            ceo_agent = await get_ceo_agent(session)
        except Exception as e:
            logger.error(f"Failed to sync agents: {e}")

    if ceo_agent is None:
        logger.error("CEO agent still not found after sync attempt")
        raise HTTPException(
            status_code=503,
            detail="Agente CEO não encontrado. Verifique se o sync de agentes foi executado.",
        )

    workflow_state = WORKFLOW_QUEUED_TO_CEO

    task = Task(
        title=body.title,
        description=body.description,
        priority=body.priority,
        assigned_agent_id=ceo_agent.id,
        label=body.label,
        github_repo=body.github_repo,
        workflow_state=workflow_state,
        workflow_last_error=None,
        workflow_attempts=0,
        created_at=now,
        updated_at=now,
    )
    session.add(task)

    await log_task_event(
        session,
        task_id=task.id,
        event_type="task.created",
        description="Task criada",
        to_agent_slug="ceo",
    )
    await log_task_event(
        session,
        task_id=task.id,
        event_type="task.queued_to_ceo",
        description="Task enfileirada para despacho via CEO",
        agent_id=ceo_agent.id,
        to_agent_slug="ceo",
    )
    await session.commit()
    await session.refresh(task)

    queued, error = enqueue_task_for_ceo(task.id)
    if not queued:
        task.workflow_state = WORKFLOW_FAILED
        task.workflow_last_error = error
        await log_task_event(
            session,
            task_id=task.id,
            event_type="task.failed",
            description="Falha ao enfileirar task para o CEO",
            agent_id=ceo_agent.id,
            to_agent_slug="ceo",
            payload={"error": error},
        )
        await session.commit()
        await session.refresh(task)

    slug_map = await _load_slug_map_for_tasks(session, [task])
    return _to_task_response(task, slug_map)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    body: UpdateTaskRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import timezone

    result = await session.exec(select(Task).where(Task.id == task_id))
    task = result.first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    previous_status = task.status

    if body.status is not None:
        task.status = body.status
    if body.priority is not None:
        task.priority = body.priority
    if body.assigned_agent_id is not None:
        task.assigned_agent_id = UUID(body.assigned_agent_id)
    if body.title is not None:
        task.title = body.title
    if body.description is not None:
        task.description = body.description
    if body.label is not None:
        task.label = body.label
    if body.github_repo is not None:
        task.github_repo = body.github_repo

    if body.status and body.status != previous_status:
        if body.status == "done":
            task.workflow_state = WORKFLOW_COMPLETED
            task.workflow_last_error = None
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.completed",
                description="Task marcada como concluida",
                agent_id=task.assigned_agent_id,
            )
        elif body.status == "cancelled":
            task.workflow_state = WORKFLOW_FAILED
            await log_task_event(
                session,
                task_id=task.id,
                event_type="task.failed",
                description="Task marcada como cancelada",
                agent_id=task.assigned_agent_id,
            )

    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    await session.refresh(task)

    slug_map = await _load_slug_map_for_tasks(session, [task])
    return _to_task_response(task, slug_map)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()
