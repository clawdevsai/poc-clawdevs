from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, paginate
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import Task

router = APIRouter()


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: str
    priority: str
    assigned_agent_id: str | None
    github_issue_number: int | None
    github_issue_url: str | None
    github_repo: str | None
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CreateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    assigned_agent_id: str | None = None


class UpdateTaskRequest(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigned_agent_id: str | None = None


@router.get("", response_model=Page[TaskResponse])
async def list_tasks(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    status: Optional[str] = Query(None),
):
    query = select(Task).order_by(Task.created_at.desc())
    if status:
        query = query.where(Task.status == status)
    result = await session.exec(query)
    tasks = result.all()
    return paginate([
        TaskResponse(
            id=str(t.id), title=t.title, description=t.description,
            status=t.status, priority=t.priority,
            assigned_agent_id=str(t.assigned_agent_id) if t.assigned_agent_id else None,
            github_issue_number=t.github_issue_number,
            github_issue_url=t.github_issue_url,
            github_repo=t.github_repo,
            due_at=t.due_at, created_at=t.created_at, updated_at=t.updated_at,
        )
        for t in tasks
    ])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    body: CreateTaskRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime, timezone
    task = Task(
        title=body.title,
        description=body.description,
        priority=body.priority,
        assigned_agent_id=UUID(body.assigned_agent_id) if body.assigned_agent_id else None,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return TaskResponse(
        id=str(task.id), title=task.title, description=task.description,
        status=task.status, priority=task.priority,
        assigned_agent_id=str(task.assigned_agent_id) if task.assigned_agent_id else None,
        github_issue_number=task.github_issue_number,
        github_issue_url=task.github_issue_url,
        github_repo=task.github_repo,
        due_at=task.due_at, created_at=task.created_at, updated_at=task.updated_at,
    )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    body: UpdateTaskRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime, timezone
    result = await session.exec(select(Task).where(Task.id == UUID(task_id)))
    task = result.first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if body.status is not None:
        task.status = body.status
    if body.priority is not None:
        task.priority = body.priority
    if body.assigned_agent_id is not None:
        task.assigned_agent_id = UUID(body.assigned_agent_id)
    task.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(task)
    return TaskResponse(
        id=str(task.id), title=task.title, description=task.description,
        status=task.status, priority=task.priority,
        assigned_agent_id=str(task.assigned_agent_id) if task.assigned_agent_id else None,
        github_issue_number=task.github_issue_number,
        github_issue_url=task.github_issue_url,
        github_repo=task.github_repo,
        due_at=task.due_at, created_at=task.created_at, updated_at=task.updated_at,
    )
