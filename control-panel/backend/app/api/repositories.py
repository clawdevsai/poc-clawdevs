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
from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from datetime import datetime, UTC
from uuid import UUID

from app.core.database import get_session
from app.api.deps import CurrentUser, AdminUser
from app.models import Repository

router = APIRouter()


class RepositoryResponse(BaseModel):
    id: str
    name: str
    full_name: str
    description: str | None
    default_branch: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CreateRepositoryRequest(BaseModel):
    name: str
    full_name: str  # org/repo
    description: str | None = None
    default_branch: str = "main"


class UpdateRepositoryRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    default_branch: str | None = None
    is_active: bool | None = None


class RepositoriesListResponse(BaseModel):
    items: list[RepositoryResponse]
    total: int


def _to_response(r: Repository) -> RepositoryResponse:
    return RepositoryResponse(
        id=str(r.id),
        name=r.name,
        full_name=r.full_name,
        description=r.description,
        default_branch=r.default_branch,
        is_active=r.is_active,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


@router.get("", response_model=RepositoriesListResponse)
async def list_repositories(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    include_inactive: bool = False,
):
    query = select(Repository).order_by(Repository.name)
    if not include_inactive:
        query = query.where(Repository.is_active)
    result = await session.exec(query)
    repos = result.all()
    return RepositoriesListResponse(
        items=[_to_response(r) for r in repos], total=len(repos)
    )


@router.post("", response_model=RepositoryResponse, status_code=201)
async def create_repository(
    body: CreateRepositoryRequest,
    response: Response,
    _: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime

    normalized_full_name = body.full_name.strip()
    normalized_name = body.name.strip()

    result = await session.exec(
        select(Repository).where(Repository.full_name == normalized_full_name)
    )
    existing = result.first()
    if existing:
        existing.name = normalized_name or existing.name
        existing.description = body.description
        existing.default_branch = body.default_branch
        existing.is_active = True
        existing.updated_at = datetime.now(UTC).replace(tzinfo=None)
        await session.commit()
        await session.refresh(existing)
        response.status_code = status.HTTP_200_OK
        return _to_response(existing)

    repo = Repository(
        name=normalized_name,
        full_name=normalized_full_name,
        description=body.description,
        default_branch=body.default_branch,
        updated_at=datetime.now(UTC).replace(tzinfo=None),
    )
    session.add(repo)
    await session.commit()
    await session.refresh(repo)
    return _to_response(repo)


@router.patch("/{repo_id}", response_model=RepositoryResponse)
async def update_repository(
    repo_id: str,
    body: UpdateRepositoryRequest,
    _: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime

    result = await session.exec(
        select(Repository).where(Repository.id == UUID(repo_id))
    )
    repo = result.first()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    if body.name is not None:
        repo.name = body.name
    if body.description is not None:
        repo.description = body.description
    if body.default_branch is not None:
        repo.default_branch = body.default_branch
    if body.is_active is not None:
        repo.is_active = body.is_active
    repo.updated_at = datetime.now(UTC).replace(tzinfo=None)
    await session.commit()
    await session.refresh(repo)
    return _to_response(repo)


@router.delete("/{repo_id}", status_code=204)
async def delete_repository(
    repo_id: str,
    _: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(
        select(Repository).where(Repository.id == UUID(repo_id))
    )
    repo = result.first()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    await session.delete(repo)
    await session.commit()
