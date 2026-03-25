from typing import Annotated, Optional
from fastapi import APIRouter, Query
from sqlmodel import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import ActivityEvent, Agent

router = APIRouter()


class ActivityEventResponse(BaseModel):
    id: str
    event_type: str
    description: str
    agent_id: Optional[str] = None
    created_at: datetime

    @classmethod
    def from_orm(cls, event: ActivityEvent, agent_map: dict) -> "ActivityEventResponse":
        # Build description from event data
        description = event.payload.get("description", "") if event.payload else ""
        if not description:
            description = _build_description(event)

        return cls(
            id=str(event.id),
            event_type=event.event_type,
            description=description,
            agent_id=str(event.agent_id) if event.agent_id else None,
            created_at=event.created_at,
        )


def _build_description(event: ActivityEvent) -> str:
    """Build a human-readable description from the event data."""
    event_type = event.event_type
    entity_type = event.entity_type or "item"
    entity_id = event.entity_id or "unknown"

    descriptions = {
        "session.created": f"New session started",
        "session.ended": f"Session ended",
        "session.message": f"New message in session",
        "agent.status_change": f"Agent status changed",
        "agent.heartbeat": f"Agent heartbeat received",
        "cron.executed": f"Cron job executed",
        "task.created": f"Task created",
        "task.completed": f"Task completed",
        "approval.requested": f"Approval requested",
        "approval.approved": f"Request approved",
        "approval.rejected": f"Request rejected",
        "memory.added": f"Memory entry added",
        "sdd.created": f"SDD document created",
    }

    return descriptions.get(event_type, f"{event_type.replace('.', ' ').title()}")


class ActivityEventsListResponse(BaseModel):
    items: list[ActivityEventResponse]
    total: int


@router.get("", response_model=ActivityEventsListResponse)
async def list_activity_events(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(20, ge=1, le=100),
    agent_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
):
    """List recent activity events with optional filtering."""
    from app.services.activity_sync import sync_all_activity

    # Build base query
    query = select(ActivityEvent).order_by(desc(ActivityEvent.created_at))

    # Apply filters
    if agent_id:
        try:
            agent_uuid = UUID(agent_id)
            query = query.where(ActivityEvent.agent_id == agent_uuid)
        except ValueError:
            pass  # Invalid UUID, ignore filter

    if event_type:
        query = query.where(ActivityEvent.event_type == event_type)

    # Get total count
    count_query = select(ActivityEvent).where(query.whereclause) if query.whereclause else select(ActivityEvent)
    count_result = await session.exec(count_query)
    total = len(count_result.all())

    # If no events exist, sync from sessions
    if total == 0:
        await sync_all_activity(session)
        # Re-query after sync
        count_result = await session.exec(count_query)
        total = len(count_result.all())

    # Apply limit
    query = query.limit(limit)

    result = await session.exec(query)
    events = result.all()

    # Build agent map for description enrichment
    agent_ids = {e.agent_id for e in events if e.agent_id}
    agent_map = {}
    if agent_ids:
        agent_result = await session.exec(
            select(Agent).where(Agent.id.in_(agent_ids))
        )
        agent_map = {a.id: a for a in agent_result.all()}

    items = [ActivityEventResponse.from_orm(e, agent_map) for e in events]

    return ActivityEventsListResponse(items=items, total=total)
