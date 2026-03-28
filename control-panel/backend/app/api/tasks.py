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
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession
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
    label: str | None
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
    items = [
        TaskResponse(
            id=str(t.id),
            title=t.title,
            description=t.description,
            status=t.status,
            priority=t.priority,
            label=t.label,
            assigned_agent_id=str(t.assigned_agent_id) if t.assigned_agent_id else None,
            github_issue_number=t.github_issue_number,
            github_issue_url=t.github_issue_url,
            github_repo=t.github_repo,
            due_at=t.due_at,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in tasks
    ]
    return TasksListResponse(items=items, total=len(items))


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    body: CreateTaskRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    task = Task(
        title=body.title,
        description=body.description,
        priority=body.priority,
        assigned_agent_id=(
            UUID(body.assigned_agent_id) if body.assigned_agent_id else None
        ),
        label=body.label,
        github_repo=body.github_repo,
        updated_at=now,
        created_at=now,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        label=task.label,
        assigned_agent_id=(
            str(task.assigned_agent_id) if task.assigned_agent_id else None
        ),
        github_issue_number=task.github_issue_number,
        github_issue_url=task.github_issue_url,
        github_repo=task.github_repo,
        due_at=task.due_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
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
    if body.title is not None:
        task.title = body.title
    if body.description is not None:
        task.description = body.description
    if body.label is not None:
        task.label = body.label
    if body.github_repo is not None:
        task.github_repo = body.github_repo
    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    await session.refresh(task)
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        label=task.label,
        assigned_agent_id=(
            str(task.assigned_agent_id) if task.assigned_agent_id else None
        ),
        github_issue_number=task.github_issue_number,
        github_issue_url=task.github_issue_url,
        github_repo=task.github_repo,
        due_at=task.due_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
