"""Activity events synchronization service.
Generates activity events from existing sessions and other data sources
to populate the Recent Activity feed.
"""
from datetime import datetime
from sqlmodel import select
from app.models import ActivityEvent, Session, Agent


async def sync_activity_from_sessions(db_session) -> int:
    """Generate activity events from existing sessions.

    Returns the number of events created.
    """
    # Get agents mapping
    agent_result = await db_session.exec(select(Agent))
    agents = {a.slug: a.id for a in agent_result.all()}

    # Get recent sessions
    result = await db_session.exec(
        select(Session)
        .order_by(Session.last_active_at.desc())
        .limit(50)
    )
    sessions = result.all()

    created_count = 0

    for session in sessions:
        # Check if we already have an event for this session
        existing = await db_session.exec(
            select(ActivityEvent).where(
                ActivityEvent.entity_id == session.openclaw_session_id,
                ActivityEvent.event_type.in_(["session.created", "session.active"])
            )
        )
        if existing.first():
            continue

        # Determine agent_id
        agent_id = None
        if session.agent_slug and session.agent_slug in agents:
            agent_id = agents[session.agent_slug]

        # Create activity event for session
        event_type = "session.active" if session.status == "active" else "session.ended"

        payload = {
            "description": f"Session {session.status} via {session.channel_type or 'unknown'}",
            "message_count": session.message_count,
            "channel_type": session.channel_type,
            "channel_peer": session.channel_peer,
        }

        event = ActivityEvent(
            event_type=event_type,
            agent_id=agent_id,
            entity_type="session",
            entity_id=session.openclaw_session_id,
            payload=payload,
            created_at=session.last_active_at or session.created_at,
        )
        db_session.add(event)
        created_count += 1

    if created_count > 0:
        await db_session.commit()

    return created_count


async def sync_all_activity(db_session) -> dict:
    """Sync all activity sources.

    Returns a summary of created events.
    """
    session_events = await sync_activity_from_sessions(db_session)

    return {
        "session_events": session_events,
        "total": session_events,
    }
