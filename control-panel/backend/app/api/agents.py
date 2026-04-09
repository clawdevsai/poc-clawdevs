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
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from datetime import datetime, UTC

from app.core.database import get_session
from app.api.deps import CurrentUser, AdminUser
from app.models import Agent
from app.services.agent_sync import sync_agents_runtime, sync_agents
from app.services.agent_activity import get_agent_current_activity

router = APIRouter()


class AgentResponse(BaseModel):
    id: str
    slug: str
    display_name: str
    role: str
    avatar_url: str | None
    status: str
    runtime_status: str | None = None  # online|working|idle|offline
    current_model: str | None
    last_heartbeat_at: datetime | None
    cron_expression: str | None
    cron_last_run_at: datetime | None
    cron_next_run_at: datetime | None
    cron_status: str
    created_at: datetime
    current_activity: str | None = None
    current_activity_full: str | None = None
    current_activity_at: datetime | None = None
    # Backward-compatible aliases still consumed by frontend screens.
    model: str | None = None
    last_heartbeat: datetime | None = None

    @classmethod
    def from_orm(
        cls,
        agent: Agent,
        *,
        current_activity: str | None = None,
        current_activity_full: str | None = None,
        current_activity_at: datetime | None = None,
    ) -> "AgentResponse":
        return cls(
            id=str(agent.id),
            slug=agent.slug,
            display_name=agent.display_name,
            role=agent.role,
            avatar_url=agent.avatar_url,
            status=agent.status,
            runtime_status=agent.runtime_status,
            current_model=agent.current_model,
            last_heartbeat_at=agent.last_heartbeat_at,
            cron_expression=agent.cron_expression,
            cron_last_run_at=agent.cron_last_run_at,
            cron_next_run_at=agent.cron_next_run_at,
            cron_status=agent.cron_status,
            created_at=agent.created_at,
            current_activity=current_activity,
            current_activity_full=current_activity_full,
            current_activity_at=current_activity_at,
            model=agent.current_model,
            last_heartbeat=agent.last_heartbeat_at,
        )


class AgentsListResponse(BaseModel):
    items: list[AgentResponse]
    total: int


@router.get("", response_model=AgentsListResponse)
async def list_agents(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """List all agents."""
    import logging

    logger = logging.getLogger(__name__)

    await sync_agents_runtime(session)
    result = await session.exec(select(Agent).order_by(Agent.slug))
    agents = result.all()
    logger.info(f"list_agents: Found {len(agents)} agents in database")
    items = [AgentResponse.from_orm(a) for a in agents]
    return AgentsListResponse(items=items, total=len(items))


@router.get("/{slug}", response_model=AgentResponse)
async def get_agent(
    slug: str,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    await sync_agents_runtime(session)
    result = await session.exec(select(Agent).where(Agent.slug == slug))
    agent = result.first()
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{slug}' not found")
    current_activity, current_activity_full, current_activity_at = (
        get_agent_current_activity(agent.slug)
    )
    return AgentResponse.from_orm(
        agent,
        current_activity=current_activity,
        current_activity_full=current_activity_full,
        current_activity_at=current_activity_at,
    )


@router.patch("/{slug}/status", response_model=AgentResponse)
async def update_agent_status(
    slug: str,
    body: dict,
    _: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(select(Agent).where(Agent.slug == slug))
    agent = result.first()
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{slug}' not found")
    if "status" in body:
        agent.status = body["status"]
    if "current_model" in body:
        agent.current_model = body["current_model"]
    from datetime import datetime

    agent.updated_at = datetime.now(UTC).replace(tzinfo=None)
    await session.commit()
    await session.refresh(agent)
    return AgentResponse.from_orm(agent)


class SyncResponse(BaseModel):
    message: str
    created: int
    updated: int
    total: int


@router.post("/admin/sync", response_model=SyncResponse)
async def sync_agents_admin(
    _: AdminUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Admin endpoint to manually trigger agent synchronization.
    This is useful for debugging if agents aren't appearing.
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Get count before
        result_before = await session.exec(select(Agent))
        count_before = len(result_before.all())

        # Sync
        logger.info("Admin triggered agent sync...")
        await sync_agents(session)

        # Get count after
        result_after = await session.exec(select(Agent))
        agents_after = result_after.all()
        count_after = len(agents_after)

        created = max(0, count_after - count_before)
        updated = 0  # We don't track this separately in the API response

        logger.info(f"Sync complete: {created} agents created, {count_after} total")

        return SyncResponse(
            message=f"Synchronized {created} new agents",
            created=created,
            updated=updated,
            total=count_after,
        )
    except Exception as e:
        logger.error(f"Admin sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
