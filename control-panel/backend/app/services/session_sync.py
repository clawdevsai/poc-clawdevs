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

"""Session synchronization service.

Fetches sessions from OpenClaw runtime (from filesystem) and syncs them to the database.
This makes Telegram and other channel sessions visible in the control panel.
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from sqlmodel import select
from app.models import Session
from app.core.config import get_settings
from app.services.agent_sync import get_discovered_agent_slugs

settings = get_settings()
ACTIVE_WINDOW = timedelta(minutes=20)


async def sync_sessions(db_session) -> None:
    """Fetch sessions from OpenClaw filesystem and upsert them into the database.
    ⚡ Bolt: Optimized using 'Collect-Batch-Compare' to avoid N+1 queries and redundant updates.
    """
    base_path = Path(settings.openclaw_data_path)
    agent_slugs = get_discovered_agent_slugs()
    collected: list[tuple[str, str, dict, str]] = []

    # 1. Collect all session metadata from all agents first (Batching)
    all_oc_sessions = []
    all_session_ids = set()

    for agent_slug in agent_slugs:
        sessions_file = base_path / "agents" / agent_slug / "sessions" / "sessions.json"
        if not sessions_file.exists():
            continue
        try:
            with open(sessions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for key, oc in data.items():
                        if isinstance(oc, dict) and oc.get("sessionId"):
                            collected.append((agent_slug, key, oc, str(oc["sessionId"])))
        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(data, dict):
            continue

        # Optimization: Fetch all existing sessions for this agent in a single batch.
        # This prevents N+1 queries during the sync loop.
        result = await db_session.exec(
            select(Session).where(Session.agent_slug == agent_slug)
        )
        existing_map = {s.openclaw_session_id: s for s in result.all()}

        # If two JSON keys share the same sessionId, the last one processed wins for
        # the DB row (upsert by openclaw_session_id); openclaw_session_key reflects
        # the last seen key.
        for session_key, oc_session in data.items():
            if not isinstance(oc_session, dict):
                continue
            session_id = oc_session.get("sessionId")
            if session_id:
                all_oc_sessions.append((agent_slug, session_key, oc_session))
                all_session_ids.add(session_id)

    if not all_oc_sessions:
        return

    # 2. Batch lookup existing sessions from DB (O(1) query instead of O(N))
    result = await db_session.exec(
        select(Session).where(Session.openclaw_session_id.in_(list(all_session_ids)))
    )
    existing_map = {s.openclaw_session_id: s for s in result.all()}
    changed = False

    # 3. Process sessions and apply Smart Sync
    for agent_slug, session_key, oc_session in all_oc_sessions:
        session_id = oc_session.get("sessionId")
        existing = existing_map.get(session_id)

        # Parse timestamps for Smart Sync
        updated_at = _parse_timestamp(oc_session.get("updatedAt"))
        last_active_at = updated_at

        # BOLT OPTIMIZATION: Smart Sync
        # Skip processing if session exists and hasn't changed (based on updatedAt)
        if (
            existing
            and last_active_at
            and existing.last_active_at
            and last_active_at == existing.last_active_at
            and existing.status == _derive_session_status(updated_at)
        ):
            continue

            # Try to find existing session from the pre-fetched map.
            existing = existing_map.get(session_id)

            # Parse timestamps
            updated_at = _parse_timestamp(oc_session.get("updatedAt"))
            last_active_at = updated_at  # Use updatedAt as lastActiveAt

            # Smart Sync: Skip processing if the session hasn't changed.
            # We compare the source updatedAt with the DB last_active_at.
            if existing and updated_at and existing.last_active_at == updated_at:
                continue

            status = _derive_session_status(updated_at)

        if session_path and session_path.exists():
            message_count = _count_messages_in_session_file(session_path)

        if existing:
            existing.agent_slug = agent_slug
            existing.openclaw_session_key = session_key
            existing.channel_type = channel_type or existing.channel_type
            existing.channel_peer = (
                str(channel_peer) if channel_peer else existing.channel_peer
            )
            existing.status = status
            existing.message_count = message_count
            existing.token_count = token_count
            existing.last_active_at = last_active_at or existing.last_active_at
            if status == "completed" and existing.ended_at is None:
                existing.ended_at = last_active_at
            changed = True
        else:
            new_session = Session(
                openclaw_session_id=session_id,
                openclaw_session_key=session_key,
                agent_slug=agent_slug,
                channel_type=channel_type,
                channel_peer=str(channel_peer) if channel_peer else None,
                status=status,
                message_count=message_count,
                token_count=token_count,
                started_at=last_active_at,
                last_active_at=last_active_at,
                ended_at=last_active_at if status == "completed" else None,
            )
            channel_peer = delivery.get("to") or origin.get("to")

            # Get message count and token metrics from session data
            message_count = 0
            token_count = 0

            # Try to get token metrics directly from session metadata
            if "totalTokens" in oc_session:
                token_count = oc_session.get("totalTokens", 0)
            elif "inputTokens" in oc_session or "outputTokens" in oc_session:
                token_count = oc_session.get("inputTokens", 0) + oc_session.get(
                    "outputTokens", 0
                )
            elif "contextTokens" in oc_session:
                token_count = oc_session.get("contextTokens", 0)

            # Count messages from session file if exists.
            # This is an expensive filesystem operation (reading/parsing JSONL).
            session_file = oc_session.get("sessionFile")
            session_path: Path | None = None
            if isinstance(session_file, str) and session_file:
                # Handle both absolute and relative paths
                if session_file.startswith("/"):
                    session_path = Path(session_file)
                else:
                    session_path = base_path / session_file
            else:
                # Some OpenClaw entries (cron/run session keys) omit sessionFile.
                # Fallback to canonical session transcript path by sessionId.
                session_path = (
                    base_path
                    / "agents"
                    / agent_slug
                    / "sessions"
                    / f"{session_id}.jsonl"
                )

            if session_path is not None:
                message_count = _count_messages_in_session_file(session_path)

            if existing:
                # Update existing session
                existing.agent_slug = agent_slug
                existing.openclaw_session_key = session_key
                existing.channel_type = channel_type or existing.channel_type
                existing.channel_peer = (
                    str(channel_peer) if channel_peer else existing.channel_peer
                )
                existing.status = status
                existing.message_count = message_count
                existing.token_count = token_count
                existing.last_active_at = last_active_at or existing.last_active_at
                if status == "completed" and existing.ended_at is None:
                    existing.ended_at = last_active_at
            else:
                # Create new session
                new_session = Session(
                    openclaw_session_id=session_id,
                    openclaw_session_key=session_key,
                    agent_slug=agent_slug,
                    channel_type=channel_type,
                    channel_peer=str(channel_peer) if channel_peer else None,
                    status=status,
                    message_count=message_count,
                    token_count=token_count,
                    started_at=last_active_at,  # Use first seen as started
                    last_active_at=last_active_at,
                    ended_at=last_active_at if status == "completed" else None,
                )
                db_session.add(new_session)
                # Ensure the new session is also in existing_map for current loop batch
                existing_map[session_id] = new_session

    await db_session.commit()


def _parse_timestamp(ts) -> datetime | None:
    """Parse timestamp from various formats."""
    if not ts:
        return None

    if isinstance(ts, (int, float)):
        # Assume milliseconds if > year 2000 in seconds
        if ts > 946684800000:
            ts = ts / 1000
        return datetime.fromtimestamp(ts, timezone.utc).replace(tzinfo=None)

    if isinstance(ts, str):
        try:
            # Try ISO format
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(
                tzinfo=None
            )
        except ValueError:
            pass
        try:
            # Try parsing as float timestamp
            ts_num = float(ts)
            if ts_num > 946684800000:
                ts_num = ts_num / 1000
            return datetime.fromtimestamp(ts_num, timezone.utc).replace(tzinfo=None)
        except ValueError:
            pass

    return None


def _derive_session_status(updated_at: datetime | None) -> str:
    """Classify session status from its latest activity timestamp."""
    if updated_at is None:
        return "completed"
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if now_utc - updated_at <= ACTIVE_WINDOW:
        return "active"
    return "completed"


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
                        evt = json.loads(line)
                        if not isinstance(evt, dict):
                            continue
                        # OpenClaw JSONL stores chat turns as:
                        # {"type":"message", "message":{"role":"user|assistant|..."}}
                        if evt.get("type") != "message":
                            continue
                        message_obj = evt.get("message")
                        if not isinstance(message_obj, dict):
                            continue
                        role = str(message_obj.get("role", "")).lower()
                        if role in ("user", "assistant"):
                            count += 1
                    except json.JSONDecodeError:
                        pass
        return count
    except OSError:
        return 0
