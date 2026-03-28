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
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import CurrentUser
from app.models import Agent, Session as SessionModel
from app.services.openclaw_client import openclaw_client
from app.core.database import get_session

router = APIRouter(prefix="/chat", tags=["chat"])


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
    agent_slug: str = Field(..., max_length=64)
    message: str = Field(..., min_length=1, max_length=4000)


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


async def _latest_session_for_agent(db: AsyncSession, slug: str) -> Optional[SessionModel]:
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


@router.get("/history/{agent_slug}", response_model=ChatHistoryResponse)
async def chat_history(
    agent_slug: str,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    await _ensure_agent(db, agent_slug)
    session_row = await _latest_session_for_agent(db, agent_slug)
    if not session_row or not session_row.openclaw_session_id:
        return ChatHistoryResponse(agent_slug=agent_slug, messages=[])

    oc_session = await openclaw_client.get_session(session_row.openclaw_session_id)
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


async def _stream_sse(agent_slug: str, prompt: str) -> AsyncGenerator[str, None]:
    async for event in openclaw_client.stream_chat(agent_slug=agent_slug, message=prompt):
        if event.get("event") == "delta":
            yield f"data: {event['data']}\n\n"
        elif event.get("event") == "done":
            yield "data: [DONE]\n\n"
        elif event.get("event") == "error":
            yield f"data: {event['data']}\n\n"


@router.post("/stream")
async def chat_stream(
    body: ChatRequest,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    await _ensure_agent(db, body.agent_slug)
    return EventSourceResponse(_stream_sse(body.agent_slug, body.message))
