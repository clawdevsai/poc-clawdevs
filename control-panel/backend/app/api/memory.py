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
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Query, Response
from sqlmodel import col, select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from datetime import datetime, UTC
from uuid import UUID

from app.core.database import get_session
from app.core.config import get_settings
from app.api.deps import CurrentUser
from app.models import MemoryEntry
from app.services.memory_sync import sync_memory_entries

router = APIRouter()
settings = get_settings()


class MemoryEntryResponse(BaseModel):
    id: str
    agent_id: str | None
    agent_slug: str | None
    entry_type: str
    content: str
    title: str
    body: str
    tags: list[str] | None
    source_agents: list[str] | None
    created_at: datetime
    updated_at: datetime


class MemoryListResponse(BaseModel):
    items: list[MemoryEntryResponse]
    total: int


class MemoryFileResponse(BaseModel):
    agent_slug: str
    file_name: str
    content: str
    updated_at: datetime | None


def _memory_file_path(agent_slug: str) -> Path:
    if not agent_slug.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid agent slug")
    return Path(settings.openclaw_data_path) / "memory" / agent_slug / "MEMORY.md"


@router.get("", response_model=MemoryListResponse)
async def list_memory(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    agent_id: Optional[str] = Query(None),
    agent_slug: Optional[str] = Query(None),
    entry_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
):
    # Best-effort sync from OpenClaw files before serving memory.
    await sync_memory_entries(session)

    query = select(MemoryEntry).order_by(col(MemoryEntry.created_at).desc())
    count_query = select(func.count(MemoryEntry.id))

    if agent_id:
        # Backward compatibility: /memory historically filters by agent_slug in UI.
        # If agent_id is provided, return empty (id->slug map is not persisted in this schema).
        return MemoryListResponse(items=[], total=0)
    if agent_slug:
        query = query.where(MemoryEntry.agent_slug == agent_slug)
        count_query = count_query.where(MemoryEntry.agent_slug == agent_slug)
    if entry_type:
        query = query.where(MemoryEntry.entry_type == entry_type)
        count_query = count_query.where(MemoryEntry.entry_type == entry_type)
    if search:
        pattern = f"%{search}%"
        query = query.where(col(MemoryEntry.body).ilike(pattern))
        count_query = count_query.where(col(MemoryEntry.body).ilike(pattern))

    total = (await session.exec(count_query)).one() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await session.exec(query)
    entries = result.all()
    items = [
        MemoryEntryResponse(
            id=str(e.id),
            agent_id=None,
            agent_slug=e.agent_slug or "shared",
            entry_type=e.entry_type,
            content=e.body or "",
            title=e.title or "Memory entry",
            body=e.body or "",
            tags=e.tags,
            source_agents=e.source_agents,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        for e in entries
    ]
    return MemoryListResponse(items=items, total=total)


@router.get("/agent/{agent_slug}/file", response_model=MemoryFileResponse)
async def get_memory_file(
    agent_slug: str,
    _: CurrentUser,
):
    memory_file = _memory_file_path(agent_slug)
    if not memory_file.exists():
        raise HTTPException(status_code=404, detail="Memory file not found")
    try:
        content = memory_file.read_text(encoding="utf-8")
    except OSError:
        raise HTTPException(status_code=500, detail="Failed to read memory file")

    mtime = datetime.utcfromtimestamp(memory_file.stat().st_mtime)
    return MemoryFileResponse(
        agent_slug=agent_slug,
        file_name="MEMORY.md",
        content=content,
        updated_at=mtime,
    )


@router.get("/agent/{agent_slug}/file/download")
async def download_memory_file(
    agent_slug: str,
    _: CurrentUser,
):
    memory_file = _memory_file_path(agent_slug)
    if not memory_file.exists():
        raise HTTPException(status_code=404, detail="Memory file not found")
    try:
        content = memory_file.read_text(encoding="utf-8")
    except OSError:
        raise HTTPException(status_code=500, detail="Failed to read memory file")

    filename = f"{agent_slug}-MEMORY.md"
    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@router.post("/{entry_id}/promote")
async def promote_entry(
    entry_id: str,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(
        select(MemoryEntry).where(MemoryEntry.id == UUID(entry_id))
    )
    entry = result.first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    if entry.entry_type != "candidate":
        raise HTTPException(
            status_code=400, detail="Only candidate entries can be promoted"
        )
    entry.entry_type = "global"
    entry.updated_at = datetime.now(UTC)
    await session.commit()
    return {"status": "promoted", "id": entry_id}
