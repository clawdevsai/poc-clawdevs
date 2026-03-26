"""Session synchronization service.

Fetches sessions from OpenClaw runtime (from filesystem) and syncs them to the database.
This makes Telegram and other channel sessions visible in the control panel.
"""

import json
from datetime import datetime
from pathlib import Path
from sqlmodel import select
from app.models import Session
from app.core.config import get_settings

settings = get_settings()

AGENT_SLUGS = [
    "ceo", "po", "arquiteto", "dev_backend", "dev_frontend",
    "dev_mobile", "qa_engineer", "devops_sre", "security_engineer",
    "ux_designer", "dba_data_engineer", "memory_curator",
]


async def sync_sessions(db_session) -> None:
    """Fetch sessions from OpenClaw filesystem and upsert them into the database."""
    base_path = Path(settings.openclaw_data_path)

    for agent_slug in AGENT_SLUGS:
        sessions_file = base_path / "agents" / agent_slug / "sessions" / "sessions.json"

        if not sessions_file.exists():
            continue

        try:
            with open(sessions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(data, dict):
            continue

        for session_key, oc_session in data.items():
            if not isinstance(oc_session, dict):
                continue

            session_id = oc_session.get("sessionId")
            if not session_id:
                continue

            # Try to find existing session
            result = await db_session.exec(
                select(Session).where(Session.openclaw_session_id == session_id)
            )
            existing = result.first()

            # Parse timestamps
            updated_at = _parse_timestamp(oc_session.get("updatedAt"))
            last_active_at = updated_at  # Use updatedAt as lastActiveAt

            # Determine status - sessions without recent updates are considered idle
            status = "active"  # Default to active, we don't have explicit ended info

            # Extract channel info from deliveryContext or origin
            delivery = oc_session.get("deliveryContext", {})
            origin = oc_session.get("origin", {})

            channel_type = delivery.get("channel") or origin.get("provider") or origin.get("surface")
            channel_peer = delivery.get("to") or origin.get("to")

            # Get message count and token metrics from session data
            message_count = 0
            token_count = 0
            
            # Try to get token metrics directly from session metadata
            if "totalTokens" in oc_session:
                token_count = oc_session.get("totalTokens", 0)
            elif "inputTokens" in oc_session or "outputTokens" in oc_session:
                token_count = oc_session.get("inputTokens", 0) + oc_session.get("outputTokens", 0)
            elif "contextTokens" in oc_session:
                token_count = oc_session.get("contextTokens", 0)
            
            # Count messages from session file if exists
            session_file = oc_session.get("sessionFile")
            if session_file:
                # Handle both absolute and relative paths
                if session_file.startswith("/"):
                    session_path = Path(session_file)
                else:
                    session_path = base_path / session_file
                
                message_count = _count_messages_in_session_file(session_path)

            if existing:
                # Update existing session
                existing.agent_slug = agent_slug
                existing.channel_type = channel_type or existing.channel_type
                existing.channel_peer = str(channel_peer) if channel_peer else existing.channel_peer
                existing.status = status
                existing.message_count = message_count
                existing.token_count = token_count
                existing.last_active_at = last_active_at or existing.last_active_at
            else:
                # Create new session
                new_session = Session(
                    openclaw_session_id=session_id,
                    agent_slug=agent_slug,
                    channel_type=channel_type,
                    channel_peer=str(channel_peer) if channel_peer else None,
                    status=status,
                    message_count=message_count,
                    token_count=token_count,
                    started_at=last_active_at,  # Use first seen as started
                    last_active_at=last_active_at,
                )
                db_session.add(new_session)

    await db_session.commit()


def _parse_timestamp(ts) -> datetime | None:
    """Parse timestamp from various formats."""
    if not ts:
        return None

    if isinstance(ts, (int, float)):
        # Assume milliseconds if > year 2000 in seconds
        if ts > 946684800000:
            ts = ts / 1000
        return datetime.utcfromtimestamp(ts)

    if isinstance(ts, str):
        try:
            # Try ISO format
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            pass
        try:
            # Try parsing as float timestamp
            ts_num = float(ts)
            if ts_num > 946684800000:
                ts_num = ts_num / 1000
            return datetime.utcfromtimestamp(ts_num)
        except ValueError:
            pass

    return None


def _count_messages_in_session_file(session_file: Path) -> int:
    """Count messages in a session JSONL file."""
    if not session_file.exists():
        return 0

    try:
        count = 0
        with open(session_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        # Count only user and assistant messages
                        role = msg.get("role", "").lower()
                        if role in ("user", "assistant"):
                            count += 1
                    except json.JSONDecodeError:
                        pass
        return count
    except OSError:
        return 0
