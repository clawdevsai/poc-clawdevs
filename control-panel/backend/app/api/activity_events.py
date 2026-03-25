from typing import Annotated, Optional
from fastapi import APIRouter, Query, Depends
from sqlmodel import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import ActivityEvent, Agent, Session

router = APIRouter()


class ActivityEventResponse(BaseModel):
    id: str
    event_type: str
    description: str
    agent_id: Optional[str] = None
    created_at: datetime


def _build_description_from_session(session: Session) -> str:
    """Build a human-readable description from session data."""
    channel = session.channel_type or "unknown"
    agent = session.agent_slug or "unknown"

    if session.status == "active":
        return f"Active session with {agent} via {channel}"
    else:
        return f"Session ended with {agent}"


def _event_type_from_session(session: Session) -> str:
    """Determine event type from session status."""
    if session.status == "active":
        return "session.active"
    elif session.status == "ended":
        return "session.ended"
    else:
        return "session.updated"


class ActivityEventsListResponse(BaseModel):
    items: list[ActivityEventResponse]
    total: int


async def _generate_activity_from_sessions(db_session) -> list[ActivityEventResponse]:
    """Generate activity events from recent sessions (in-memory, no DB table needed)."""
    # Get agents mapping for display names
    agent_result = await db_session.exec(select(Agent))
    agents = {a.id: a for a in agent_result.all()}
    agent_by_slug = {a.slug: a for a in agents.values()}

    # Get recent sessions
    result = await db_session.exec(
        select(Session)
        .order_by(Session.last_active_at.desc().nulls_last())
        .limit(20)
    )
    sessions = result.all()

    items = []
    for idx, session in enumerate(sessions):
        # Find agent info
        agent_id = None
        agent_name = session.agent_slug or "Unknown"
        if session.agent_slug and session.agent_slug in agent_by_slug:
            agent = agent_by_slug[session.agent_slug]
            agent_id = str(agent.id)
            agent_name = agent.display_name or agent.slug

        # Build description
        channel = session.channel_type or "direct"
        if session.status == "active":
            desc = f"Active session with {agent_name} via {channel}"
        else:
            desc = f"Session {session.status} with {agent_name}"

        event = ActivityEventResponse(
            id=f"sess-{session.id}-{idx}",
            event_type=_event_type_from_session(session),
            description=desc,
            agent_id=agent_id,
            created_at=session.last_active_at or session.created_at or datetime.utcnow(),
        )
        items.append(event)

    return items


@router.get("", response_model=ActivityEventsListResponse)
async def list_activity_events(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(20, ge=1, le=100),
    agent_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
):
    """List recent activity events generated from sessions and other sources."""
    # Generate activity from sessions (in-memory approach - no DB table needed)
    items = await _generate_activity_from_sessions(session)

    # Apply agent filter if specified
    if agent_id:
        items = [i for i in items if i.agent_id == agent_id]

    # Apply event type filter if specified
    if event_type:
        items = [i for i in items if i.event_type == event_type]

    # Apply limit
    total = len(items)
    items = items[:limit]

    return ActivityEventsListResponse(items=items, total=total)
