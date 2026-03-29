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

from typing import Annotated, Any, AsyncGenerator, Optional
import asyncio
import json
import httpx
import re
import hashlib
import logging
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sse_starlette.sse import EventSourceResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser, require_agent_access
from app.models import Agent, MemoryEntry, Session as SessionModel
from app.services.openclaw_client import openclaw_client
from app.services.embedding_service import EmbeddingService
from app.services.agent_sync import _status_from_heartbeat
from app.core.config import get_settings
from app.core.database import get_session

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()
logger = logging.getLogger(__name__)

SESSION_KEY_RE = re.compile(r"^agent:(?P<slug>[a-zA-Z0-9_-]+):(?P<rest>.+)$")
TURN_ID_SANITIZE_RE = re.compile(r"[^a-zA-Z0-9._:-]+")
EMBEDDING_DIMENSION = 1536


class ToolCall(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    tool: Optional[str] = None
    input: Optional[Any] = None
    result: Optional[Any] = None


class Message(BaseModel):
    role: str
    content: str
    tool_calls: list[ToolCall] | None = None


class ChatHistoryResponse(BaseModel):
    agent_slug: str
    messages: list[Message]


class ChatRequest(BaseModel):
    agent_slug: Optional[str] = Field(default=None, max_length=64)
    session_key: Optional[str] = Field(default=None, max_length=512)
    message: str = Field(..., min_length=1, max_length=4000)


class ChatRagTurnRequest(BaseModel):
    agent_slug: Optional[str] = Field(default=None, max_length=64)
    session_key: str = Field(..., min_length=1, max_length=512)
    turn_id: str = Field(..., min_length=1, max_length=128)
    user_message: str = Field(..., min_length=1, max_length=4000)
    assistant_message: str = Field(..., min_length=1, max_length=40000)


class ChatRagTurnResponse(BaseModel):
    status: str
    memory_id: str


def _parse_agent_session_key(session_key: str) -> tuple[str, str]:
    value = (session_key or "").strip()
    match = SESSION_KEY_RE.match(value)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="session_key must match 'agent:<slug>:<rest>'",
        )
    slug = match.group("slug").strip().lower()
    if not slug:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="session_key must include an agent slug",
        )
    return slug, value


def _resolve_agent_and_session_key_fields(
    agent_slug: Optional[str],
    session_key: Optional[str],
) -> tuple[str, str]:
    if session_key:
        session_slug, normalized_session_key = _parse_agent_session_key(session_key)
        if agent_slug and agent_slug.strip().lower() != session_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="agent_slug does not match session_key agent",
            )
        return session_slug, normalized_session_key

    if not agent_slug:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="agent_slug is required when session_key is not provided",
        )

    normalized_slug = agent_slug.strip().lower()
    return normalized_slug, f"agent:{normalized_slug}:main"


def _resolve_agent_and_session_key(body: ChatRequest) -> tuple[str, str]:
    return _resolve_agent_and_session_key_fields(body.agent_slug, body.session_key)


def _normalize_turn_id(raw_turn_id: str) -> str:
    normalized = TURN_ID_SANITIZE_RE.sub("-", raw_turn_id.strip()).strip("-")
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="turn_id is invalid after normalization",
        )
    return normalized[:96]


def _build_turn_source_path(agent_slug: str, session_key: str, turn_id: str) -> str:
    session_hash = hashlib.sha1(session_key.encode("utf-8")).hexdigest()[:16]
    return f"chat-rag/{agent_slug}/{session_hash}/{turn_id}"


def _compose_turn_memory_body(user_message: str, assistant_message: str) -> str:
    return (
        "## User\n"
        f"{user_message.strip()}\n\n"
        "## Assistant\n"
        f"{assistant_message.strip()}\n"
    )


async def _resolve_session_id_for_key(
    agent_slug: str, session_key: str
) -> Optional[str]:
    sessions_index_path = (
        Path(settings.openclaw_data_path)
        / "agents"
        / agent_slug
        / "sessions"
        / "sessions.json"
    )

    try:
        if sessions_index_path.exists():
            with open(sessions_index_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if isinstance(payload, dict):
                session_obj = payload.get(session_key)
                if isinstance(session_obj, dict):
                    session_id = session_obj.get("sessionId")
                    if isinstance(session_id, str) and session_id.strip():
                        return session_id.strip()
    except (OSError, json.JSONDecodeError):
        pass

    sessions = await openclaw_client.get_sessions(limit=1000)
    for item in sessions:
        if not isinstance(item, dict):
            continue
        if item.get("key") != session_key:
            continue
        session_id = item.get("sessionId") or item.get("session_id")
        if isinstance(session_id, str) and session_id.strip():
            return session_id.strip()

    return None


def _parse_message(msg: dict) -> Optional[Message]:
    """Parse OpenClaw message format into the public schema."""
    if not isinstance(msg, dict):
        return None

    role = msg.get("role", "unknown")
    content = msg.get("content", "")

    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text", ""))
        content = "\n".join(parts)
    elif not isinstance(content, str):
        content = str(content) if content else ""

    tool_calls: list[ToolCall] | None = None
    raw_tool_calls = msg.get("toolCalls") or msg.get("tool_calls")
    if raw_tool_calls and isinstance(raw_tool_calls, list):
        parsed_calls: list[ToolCall] = []
        for tc in raw_tool_calls:
            if not isinstance(tc, dict):
                continue
            parsed_calls.append(
                ToolCall(
                    id=tc.get("id"),
                    name=tc.get("name") or tc.get("function", {}).get("name"),
                    tool=tc.get("tool") or tc.get("function", {}).get("name"),
                    input=tc.get("input") or tc.get("arguments"),
                    result=tc.get("result"),
                )
            )
        tool_calls = parsed_calls or None

    return Message(role=role, content=content, tool_calls=tool_calls)


async def _ensure_agent(session: AsyncSession, slug: str) -> Agent:
    result = await session.exec(select(Agent).where(Agent.slug == slug))
    agent = result.first()
    if agent is None:
        # Try to sync agents (in case bootstrap failed)
        from app.services.agent_sync import sync_agents
        import logging

        logger = logging.getLogger(__name__)

        try:
            logger.info(f"Agent '{slug}' not found, attempting sync_agents...")
            await sync_agents(session)

            # Try again after sync
            result = await session.exec(select(Agent).where(Agent.slug == slug))
            agent = result.first()
        except Exception as e:
            logger.error(f"Failed to sync agents: {e}", exc_info=True)

        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )
    return agent


async def _latest_session_for_agent(
    db: AsyncSession, slug: str
) -> Optional[SessionModel]:
    stmt = (
        select(SessionModel)
        .where(SessionModel.agent_slug == slug)
        .order_by(
            SessionModel.last_active_at.is_(None),
            SessionModel.last_active_at.desc(),
            SessionModel.created_at.desc(),
        )
        .limit(1)
    )
    result = await db.exec(stmt)
    return result.first()


async def _wakeup_agent(agent_slug: str) -> bool:
    """
    Try to wake up an agent by sending a lightweight request to OpenClaw.
    This triggers the agent to start if it's idle or stopped.
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        session_key = f"agent:{agent_slug}:wakeup"
        payload = {
            "model": f"openclaw/{agent_slug}",
            "messages": [{"role": "system", "content": "__WAKEUP__"}],
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {openclaw_client.headers.get('Authorization', '')}",
            "Content-Type": "application/json",
            "x-openclaw-session-key": session_key,
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{openclaw_client.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            if r.status_code in (200, 201, 202):
                logger.info(f"Wakeup signal sent to agent '{agent_slug}'")
                return True
            else:
                logger.warning(f"Wakeup failed for '{agent_slug}': {r.status_code}")
                return False
    except Exception as e:
        logger.warning(f"Failed to send wakeup to agent '{agent_slug}': {e}")
        return False


async def _wait_for_agent_online(
    db: AsyncSession, agent_slug: str, timeout_seconds: float = 5.0
) -> bool:
    """
    Wait for agent to come online (poll status).

    Args:
        db: Database session
        agent_slug: Agent slug
        timeout_seconds: Max time to wait

    Returns:
        True if agent came online, False if timeout
    """
    import logging
    from app.services.agent_sync import sync_agents_runtime

    logger = logging.getLogger(__name__)
    start_time = asyncio.get_event_loop().time()
    poll_interval = 0.3  # Poll every 300ms
    sync_attempted = False
    wakeup_attempted = False

    while True:
        # Sync agent runtime status (reads heartbeats from disk)
        try:
            await sync_agents_runtime(db)
        except Exception as e:
            logger.warning(f"Failed to sync agent runtime: {e}")

        # Get latest agent status
        stmt = select(Agent).where(Agent.slug == agent_slug)
        result = await db.exec(stmt)
        agent = result.first()

        if not agent:
            # Try full sync if not found
            if not sync_attempted:
                logger.info(
                    f"Agent '{agent_slug}' not found during wait, attempting full sync..."
                )
                try:
                    from app.services.agent_sync import sync_agents

                    await sync_agents(db)
                    sync_attempted = True
                    # Retry fetch
                    result = await db.exec(stmt)
                    agent = result.first()
                except Exception as e:
                    logger.error(f"Failed to sync agents: {e}")

            if not agent:
                return False

        # Calculate current status
        current_status = _status_from_heartbeat(
            agent.last_heartbeat_at, has_active_session=False
        )

        # If online or working, we're good
        if current_status in ["online", "working"]:
            return True

        # If offline and haven't tried wakeup yet, try to wake the agent
        if current_status == "offline" and not wakeup_attempted:
            logger.info(f"Agent '{agent_slug}' is offline, attempting wakeup...")
            wakeup_attempted = True
            await _wakeup_agent(agent_slug)

        # Check timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout_seconds:
            logger.warning(
                f"Agent '{agent_slug}' did not come online within {timeout_seconds}s"
            )
            return False

        # Wait before polling again
        await asyncio.sleep(poll_interval)


@router.get("/history/{agent_slug}", response_model=ChatHistoryResponse)
async def chat_history(
    agent_slug: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_session)],
    session_key: Annotated[Optional[str], Query(max_length=512)] = None,
):
    await require_agent_access(agent_slug, current_user, db)
    await _ensure_agent(db, agent_slug)

    target_session_id: Optional[str] = None
    if session_key:
        session_slug, normalized_session_key = _parse_agent_session_key(session_key)
        if session_slug != agent_slug.strip().lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="agent_slug does not match session_key agent",
            )
        target_session_id = await _resolve_session_id_for_key(
            agent_slug, normalized_session_key
        )
        if not target_session_id:
            return ChatHistoryResponse(agent_slug=agent_slug, messages=[])
    else:
        session_row = await _latest_session_for_agent(db, agent_slug)
        if not session_row or not session_row.openclaw_session_id:
            return ChatHistoryResponse(agent_slug=agent_slug, messages=[])
        target_session_id = session_row.openclaw_session_id

    oc_session = await openclaw_client.get_session(target_session_id)
    messages_raw = []
    if oc_session and isinstance(oc_session, dict):
        messages_raw = (
            oc_session.get("messages")
            or oc_session.get("history")
            or oc_session.get("conversation")
            or []
        )

    parsed: list[Message] = []
    for msg in messages_raw:
        parsed_msg = _parse_message(msg)
        if parsed_msg:
            parsed.append(parsed_msg)

    return ChatHistoryResponse(agent_slug=agent_slug, messages=parsed)


async def _stream_sse(
    agent_slug: str, prompt: str, session_key: str
) -> AsyncGenerator[str, None]:
    async for event in openclaw_client.stream_chat(
        agent_slug=agent_slug, message=prompt, session_key=session_key
    ):
        if event.get("event") == "delta":
            yield f"data: {event['data']}\n\n"
        elif event.get("event") == "done":
            yield "data: [DONE]\n\n"
        elif event.get("event") == "error":
            yield f"data: {event['data']}\n\n"


@router.post("/stream")
async def chat_stream(
    body: ChatRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    resolved_agent_slug, resolved_session_key = _resolve_agent_and_session_key(body)
    await require_agent_access(resolved_agent_slug, current_user, db)
    agent = await _ensure_agent(db, resolved_agent_slug)

    # Get current status
    current_status = _status_from_heartbeat(agent.last_heartbeat_at)

    # If agent is offline or idle, wait for it to come online
    if current_status in ["offline", "idle"]:
        agent_came_online = await _wait_for_agent_online(
            db, resolved_agent_slug, timeout_seconds=3.0
        )

        if not agent_came_online:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agente offline - aguarde e tente novamente",
            )

    return EventSourceResponse(
        _stream_sse(resolved_agent_slug, body.message, resolved_session_key)
    )


@router.post("/rag/turn", response_model=ChatRagTurnResponse)
async def persist_chat_turn_rag(
    body: ChatRagTurnRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    resolved_agent_slug, resolved_session_key = _resolve_agent_and_session_key_fields(
        body.agent_slug, body.session_key
    )
    await require_agent_access(resolved_agent_slug, current_user, db)
    await _ensure_agent(db, resolved_agent_slug)

    normalized_turn_id = _normalize_turn_id(body.turn_id)
    source_file_path = _build_turn_source_path(
        resolved_agent_slug,
        resolved_session_key,
        normalized_turn_id,
    )

    existing_result = await db.exec(
        select(MemoryEntry).where(MemoryEntry.source_file_path == source_file_path)
    )
    existing_entry = existing_result.first()
    if existing_entry:
        return ChatRagTurnResponse(status="exists", memory_id=str(existing_entry.id))

    memory_body = _compose_turn_memory_body(body.user_message, body.assistant_message)
    tags = [
        "chat-rag",
        f"agent:{resolved_agent_slug}",
        f"session:{resolved_session_key}",
        f"turn:{normalized_turn_id}",
    ]

    embedding_service = EmbeddingService()
    embedding: list[float] | None = None
    embedding_generated_at: datetime | None = None
    try:
        generated_embedding = await embedding_service.generate_embedding(memory_body)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Embedding generation failed for chat turn: %s", exc)
        generated_embedding = None

    if generated_embedding:
        if len(generated_embedding) == EMBEDDING_DIMENSION:
            embedding = generated_embedding
            embedding_generated_at = datetime.now(UTC).replace(tzinfo=None)
        else:
            logger.warning(
                "Skipping chat turn embedding due to dimension mismatch: %s",
                len(generated_embedding),
            )

    memory_entry = MemoryEntry(
        agent_slug=resolved_agent_slug,
        title=f"Chat turn {resolved_agent_slug}:{normalized_turn_id}",
        body=memory_body,
        entry_type="active",
        tags=tags,
        source_agents=[resolved_agent_slug],
        embedding=embedding,
        embedding_model=embedding_service.model,
        chunk_index=0,
        source_file_path=source_file_path,
        embedding_generated_at=embedding_generated_at,
    )
    db.add(memory_entry)
    await db.commit()
    await db.refresh(memory_entry)

    return ChatRagTurnResponse(status="created", memory_id=str(memory_entry.id))
