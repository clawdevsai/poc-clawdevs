from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, paginate
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import Agent

router = APIRouter()


class AgentResponse(BaseModel):
    id: str
    slug: str
    display_name: str
    role: str
    avatar_url: str | None
    status: str
    current_model: str | None
    last_heartbeat_at: datetime | None
    cron_expression: str | None
    cron_last_run_at: datetime | None
    cron_next_run_at: datetime | None
    cron_status: str
    created_at: datetime

    @classmethod
    def from_orm(cls, agent: Agent) -> "AgentResponse":
        return cls(
            id=str(agent.id),
            slug=agent.slug,
            display_name=agent.display_name,
            role=agent.role,
            avatar_url=agent.avatar_url,
            status=agent.status,
            current_model=agent.current_model,
            last_heartbeat_at=agent.last_heartbeat_at,
            cron_expression=agent.cron_expression,
            cron_last_run_at=agent.cron_last_run_at,
            cron_next_run_at=agent.cron_next_run_at,
            cron_status=agent.cron_status,
            created_at=agent.created_at,
        )


@router.get("", response_model=Page[AgentResponse])
async def list_agents(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(select(Agent).order_by(Agent.slug))
    agents = result.all()
    return paginate([AgentResponse.from_orm(a) for a in agents])


@router.get("/{slug}", response_model=AgentResponse)
async def get_agent(
    slug: str,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(select(Agent).where(Agent.slug == slug))
    agent = result.first()
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{slug}' not found")
    return AgentResponse.from_orm(agent)


@router.patch("/{slug}/status", response_model=AgentResponse)
async def update_agent_status(
    slug: str,
    body: dict,
    _: CurrentUser,
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
    from datetime import datetime, timezone
    agent.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(agent)
    return AgentResponse.from_orm(agent)
