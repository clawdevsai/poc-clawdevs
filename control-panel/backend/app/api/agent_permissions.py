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
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel

from app.api.deps import AdminUser
from app.core.database import get_session
from app.models import AgentPermission, User

router = APIRouter(prefix="/agent-permissions", tags=["agent-permissions"])


class AgentPermissionResponse(BaseModel):
    agent_slug: str
    user_id: UUID
    username: str


class GrantAccessRequest(BaseModel):
    agent_slug: str
    user_id: UUID


@router.post("", response_model=AgentPermissionResponse)
async def grant_agent_access(
    body: GrantAccessRequest,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Grant a user access to a specific agent. Admin only."""
    # Check if user exists
    result = await db.exec(select(User).where(User.id == body.user_id))
    user = result.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if permission already exists
    result = await db.exec(
        select(AgentPermission).where(
            (AgentPermission.agent_slug == body.agent_slug)
            & (AgentPermission.user_id == body.user_id)
        )
    )
    existing = result.first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission already exists",
        )

    # Create permission
    permission = AgentPermission(
        agent_slug=body.agent_slug,
        user_id=body.user_id,
    )
    db.add(permission)
    await db.commit()
    await db.refresh(permission)

    return AgentPermissionResponse(
        agent_slug=permission.agent_slug,
        user_id=permission.user_id,
        username=user.username,
    )


@router.delete("/{agent_slug}/{user_id}", status_code=204)
async def revoke_agent_access(
    agent_slug: str,
    user_id: UUID,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Revoke a user's access to an agent. Admin only."""
    result = await db.exec(
        select(AgentPermission).where(
            (AgentPermission.agent_slug == agent_slug)
            & (AgentPermission.user_id == user_id)
        )
    )
    permission = result.first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    await db.delete(permission)
    await db.commit()


@router.get("/{agent_slug}", response_model=list[AgentPermissionResponse])
async def list_agent_permissions(
    agent_slug: str,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """List all users with access to a specific agent. Admin only."""
    result = await db.exec(
        select(AgentPermission, User).where(
            (AgentPermission.agent_slug == agent_slug)
            & (AgentPermission.user_id == User.id)
        )
    )
    rows = result.all()

    permissions = []
    for permission, user in rows:
        permissions.append(
            AgentPermissionResponse(
                agent_slug=permission.agent_slug,
                user_id=permission.user_id,
                username=user.username,
            )
        )

    return permissions
