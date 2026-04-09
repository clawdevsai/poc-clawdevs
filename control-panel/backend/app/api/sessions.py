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

from typing import Annotated, Optional
import json
from pathlib import Path
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import col, select, func
from sqlalchemy import case
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from uuid import UUID

from app.core.database import get_session as get_db_session
from app.core.config import get_settings
from app.api.deps import CurrentUser
from app.models import Session as SessionModel
from app.services.session_sync import sync_sessions
from app.services.session_labels import session_display_label, session_kind
from app.services.openclaw_client import openclaw_client
from app.services.context_metrics import validate_window_minutes

router = APIRouter()
settings = get_settings()


class MessageResponse(BaseModel):
    role: str
    content: str
    tool_calls: list[dict] | None = None


class SessionResponse(BaseModel):
    id: str
    agent_slug: str | None
    openclaw_session_id: str
    openclaw_session_key: str | None = None
    session_kind: str  # main | sub
    session_label: str
    channel_type: str | None
    channel_peer: str | None
    status: str
    message_count: int
    token_count: int
    started_at: datetime | None
    ended_at: datetime | None
    last_active_at: datetime | None
    created_at: datetime
    messages: list[MessageResponse] | None = None


class SessionsListResponse(BaseModel):
    items: list[SessionResponse]
    total: int


def _session_to_response(
    s: SessionModel,
    *,
    messages: list[MessageResponse] | None = None,
) -> SessionResponse:
    key = s.openclaw_session_key
    slug = s.agent_slug
    return SessionResponse(
        id=str(s.id),
        agent_slug=slug,
        openclaw_session_id=s.openclaw_session_id,
        openclaw_session_key=key,
        session_kind=session_kind(key, slug),
        session_label=session_display_label(key, slug),
        channel_type=s.channel_type,
        channel_peer=s.channel_peer,
        status=s.status,
        message_count=s.message_count,
        token_count=s.token_count,
        started_at=s.started_at,
        ended_at=s.ended_at,
        last_active_at=s.last_active_at,
        created_at=s.created_at,
        messages=messages,
    )


@router.get("", response_model=SessionsListResponse)
async def list_sessions(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    agent_id: Optional[str] = Query(None),
    agent_slug: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    window_minutes: int | None = Query(30),
):
    try:
        validate_window_minutes(window_minutes, allow_none=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Sync sessions from OpenClaw before listing
    await sync_sessions(session)

    # Build base query
    # Keep active sessions first, then order each group by most recent activity.
    status_priority = case(
        (col(SessionModel.status) == "active", 0),
        else_=1,
    )
    base_query = select(SessionModel).order_by(
        status_priority.asc(),
        col(SessionModel.last_active_at).desc(),
    )

    # Filter by agent_slug if provided
    if agent_slug:
        base_query = base_query.where(SessionModel.agent_slug == agent_slug)

    if window_minutes is not None:
        since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            minutes=window_minutes
        )
        base_query = base_query.where(col(SessionModel.last_active_at) >= since)

    # Get total count using func.count()
    count_query = select(func.count(SessionModel.id))
    if agent_slug:
        count_query = count_query.where(SessionModel.agent_slug == agent_slug)
    if window_minutes is not None:
        count_query = count_query.where(col(SessionModel.last_active_at) >= since)
    count_result = await session.exec(count_query)
    total = count_result.one() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    paginated_query = base_query.offset(offset).limit(page_size)
    result = await session.exec(paginated_query)
    sessions = result.all()

    items = [_session_to_response(s, messages=None) for s in sessions]
    return SessionsListResponse(items=items, total=total)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    _: CurrentUser,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Get session details including messages from OpenClaw."""
    # First sync to ensure we have the latest
    await sync_sessions(db_session)

    # Try to find by internal UUID first
    db_session_obj = None
    try:
        uuid_obj = UUID(session_id)
        result = await db_session.exec(
            select(SessionModel).where(SessionModel.id == uuid_obj)
        )
        db_session_obj = result.first()
    except ValueError:
        pass

    # If not found by UUID, try by openclaw_session_id
    if not db_session_obj:
        result = await db_session.exec(
            select(SessionModel).where(SessionModel.openclaw_session_id == session_id)
        )
        db_session_obj = result.first()

    if not db_session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    # Fetch full session details from OpenClaw including messages
    oc_session = await openclaw_client.get_session(db_session_obj.openclaw_session_id)

    # Parse messages if available
    messages = None
    if oc_session and isinstance(oc_session, dict):
        msgs = (
            oc_session.get("messages")
            or oc_session.get("history")
            or oc_session.get("conversation")
        )
        if msgs and isinstance(msgs, list):
            messages = [_parse_message(m) for m in msgs if isinstance(m, dict)]

    # Fallback: read messages from local OpenClaw session JSONL when gateway is unavailable.
    if messages is None:
        messages = _read_messages_from_local_session_file(
            agent_slug=db_session_obj.agent_slug,
            openclaw_session_id=db_session_obj.openclaw_session_id,
        )

    return _session_to_response(db_session_obj, messages=messages)


def _parse_message(msg: dict) -> MessageResponse:
    """Parse a message from OpenClaw format."""
    role = msg.get("role", "unknown")
    content = msg.get("content", "")

    # Handle different content formats
    if isinstance(content, list):
        # Some formats have content as a list of objects
        text_parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
        content = "\n".join(text_parts)
    elif not isinstance(content, str):
        content = str(content) if content else ""

    # Parse tool calls
    tool_calls = None
    raw_tool_calls = msg.get("toolCalls") or msg.get("tool_calls")
    if raw_tool_calls and isinstance(raw_tool_calls, list):
        tool_calls = []
        for tc in raw_tool_calls:
            if isinstance(tc, dict):
                tool_calls.append(
                    {
                        "id": tc.get("id"),
                        "name": tc.get("name") or tc.get("function", {}).get("name"),
                        "tool": tc.get("tool") or tc.get("function", {}).get("name"),
                        "input": tc.get("input") or tc.get("arguments"),
                        "result": tc.get("result"),
                    }
                )

    return MessageResponse(role=role, content=content, tool_calls=tool_calls)


def _read_messages_from_local_session_file(
    agent_slug: str | None,
    openclaw_session_id: str,
) -> list[MessageResponse]:
    if not agent_slug:
        return []

    session_path = (
        Path(settings.openclaw_data_path)
        / "agents"
        / agent_slug
        / "sessions"
        / f"{openclaw_session_id}.jsonl"
    )
    if not session_path.exists():
        return []

    parsed: list[MessageResponse] = []
    try:
        with open(session_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if not isinstance(evt, dict) or evt.get("type") != "message":
                    continue
                message_obj = evt.get("message")
                if not isinstance(message_obj, dict):
                    continue
                parsed.append(_parse_message(message_obj))
    except OSError:
        return []

    return parsed
