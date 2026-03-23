from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, paginate
from pydantic import BaseModel
from datetime import datetime, timezone
from uuid import UUID

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import MemoryEntry

router = APIRouter()


class MemoryEntryResponse(BaseModel):
    id: str
    agent_id: str | None
    entry_type: str
    content: str
    tags: list[str] | None
    source_agents: list[str] | None
    promoted_at: datetime | None
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=Page[MemoryEntryResponse])
async def list_memory(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    agent_id: Optional[str] = Query(None),
    entry_type: Optional[str] = Query(None),
):
    query = select(MemoryEntry).order_by(MemoryEntry.created_at.desc())
    if agent_id:
        query = query.where(MemoryEntry.agent_id == UUID(agent_id))
    if entry_type:
        query = query.where(MemoryEntry.entry_type == entry_type)
    result = await session.exec(query)
    entries = result.all()
    return paginate([
        MemoryEntryResponse(
            id=str(e.id), agent_id=str(e.agent_id) if e.agent_id else None,
            entry_type=e.entry_type, content=e.content,
            tags=e.tags, source_agents=e.source_agents,
            promoted_at=e.promoted_at, created_at=e.created_at, updated_at=e.updated_at,
        )
        for e in entries
    ])


@router.post("/{entry_id}/promote")
async def promote_entry(
    entry_id: str,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(select(MemoryEntry).where(MemoryEntry.id == UUID(entry_id)))
    entry = result.first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    if entry.entry_type != "candidate":
        raise HTTPException(status_code=400, detail="Only candidate entries can be promoted")
    entry.entry_type = "global"
    entry.promoted_at = datetime.now(timezone.utc)
    entry.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return {"status": "promoted", "id": entry_id}
