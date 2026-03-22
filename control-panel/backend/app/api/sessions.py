from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, paginate
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import Session as SessionModel

router = APIRouter()


class SessionResponse(BaseModel):
    id: str
    agent_id: str | None
    openclaw_session_id: str
    channel_type: str | None
    channel_peer: str | None
    message_count: int
    token_count: int
    started_at: datetime | None
    last_active_at: datetime | None
    created_at: datetime


@router.get("", response_model=Page[SessionResponse])
async def list_sessions(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    agent_id: Optional[str] = Query(None),
):
    query = select(SessionModel).order_by(SessionModel.last_active_at.desc())
    if agent_id:
        from uuid import UUID
        query = query.where(SessionModel.agent_id == UUID(agent_id))
    result = await session.exec(query)
    sessions = result.all()
    return paginate([
        SessionResponse(
            id=str(s.id),
            agent_id=str(s.agent_id) if s.agent_id else None,
            openclaw_session_id=s.openclaw_session_id,
            channel_type=s.channel_type,
            channel_peer=s.channel_peer,
            message_count=s.message_count,
            token_count=s.token_count,
            started_at=s.started_at,
            last_active_at=s.last_active_at,
            created_at=s.created_at,
        )
        for s in sessions
    ])
