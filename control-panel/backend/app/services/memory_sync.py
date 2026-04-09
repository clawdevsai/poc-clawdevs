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

"""Memory synchronization service.

Loads OpenClaw MEMORY.md files from the shared data PVC and upserts lightweight
entries into the panel database so the UI can display per-agent memory.
"""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from sqlmodel import col, select

from app.core.config import get_settings
from app.models import MemoryEntry
from app.services.memory_lifecycle import MemoryAccessLayer

settings = get_settings()


def _extract_title(content: str, fallback: str) -> str:
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            title = line.lstrip("#").strip()
            if title:
                return title
    return fallback


async def sync_memory_entries(db_session) -> None:
    """Sync MEMORY.md files from OpenClaw filesystem into memory_entries table."""
    base_path = Path(settings.openclaw_data_path) / "memory"
    if not base_path.exists():
        return

    access_layer = MemoryAccessLayer(memory_root=base_path)

    agent_dirs = [
        p.name for p in base_path.iterdir() if p.is_dir() and p.name != "shared"
    ]
    changed = False

    # Per-agent MEMORY.md
    for slug in agent_dirs:
        content = access_layer.read_memory(slug).strip()

        if not content:
            continue

        title = _extract_title(content, f"{slug} memory")
        result_entry = await db_session.exec(
            select(MemoryEntry)
            .where(col(MemoryEntry.agent_slug) == slug)
            .where(col(MemoryEntry.entry_type) == "active")
            .order_by(col(MemoryEntry.updated_at).desc())
        )
        existing = result_entry.first()

        if existing:
            if existing.body != content or existing.title != title:
                existing.title = title
                existing.body = content
                existing.tags = [slug]
                existing.source_agents = [slug]
                existing.updated_at = datetime.now(UTC).replace(tzinfo=None)
                changed = True
        else:
            db_session.add(
                MemoryEntry(
                    agent_slug=slug,
                    title=title,
                    body=content,
                    entry_type="active",
                    tags=[slug],
                    source_agents=[slug],
                )
            )
            changed = True

    # Shared memory
    content = access_layer.read_memory("shared").strip()

    if content:
        title = _extract_title(content, "Shared memory")
        shared_result = await db_session.exec(
            select(MemoryEntry)
            .where(col(MemoryEntry.agent_slug).is_(None))
            .where(col(MemoryEntry.entry_type) == "global")
            .order_by(col(MemoryEntry.updated_at).desc())
        )
        shared_existing = shared_result.first()

        if shared_existing:
            if shared_existing.body != content or shared_existing.title != title:
                shared_existing.title = title
                shared_existing.body = content
                shared_existing.tags = ["shared"]
                shared_existing.source_agents = ["shared"]
                shared_existing.updated_at = datetime.now(UTC).replace(tzinfo=None)
                changed = True
        else:
            db_session.add(
                MemoryEntry(
                    agent_slug=None,
                    title=title,
                    body=content,
                    entry_type="global",
                    tags=["shared"],
                    source_agents=["shared"],
                )
            )
            changed = True

    if changed:
        await db_session.commit()
