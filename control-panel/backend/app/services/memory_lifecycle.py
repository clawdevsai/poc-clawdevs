"""Unified memory access, compaction lifecycle, and merge rules."""

from __future__ import annotations

import json
import logging
from datetime import datetime, UTC
from hashlib import sha256
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.services.adaptive_compressor import AdaptiveCompressor
from app.services.summarizer import IntelligentSummarizer

logger = logging.getLogger(__name__)
settings = get_settings()

MEMORY_ROOT = Path(settings.openclaw_data_path) / "memory"
EVENT_LOG_NAME = "events.jsonl"


class MemoryAccessLayer:
    def __init__(self, memory_root: Path = MEMORY_ROOT) -> None:
        self.memory_root = memory_root
        self._cache: dict[str, str] = {}

    def _resolve_memory_file(self, agent_slug: str) -> Path:
        if agent_slug == "shared":
            return self.memory_root / "shared" / "SHARED_MEMORY.md"
        return self.memory_root / agent_slug / "MEMORY.md"

    def read_memory(self, agent_slug: str) -> str:
        memory_file = self._resolve_memory_file(agent_slug)
        if not memory_file.exists():
            return ""
        try:
            content = memory_file.read_text(encoding="utf-8").strip()
        except OSError:
            return ""
        self._cache[agent_slug] = content
        return content

    def write_memory(self, agent_slug: str, content: str) -> None:
        if not content:
            return
        if len(content) > 200_000:
            content = content[:200_000] + "\n# TRUNCATED"
        memory_file = self._resolve_memory_file(agent_slug)
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        memory_file.write_text(content, encoding="utf-8")
        self._cache[agent_slug] = content


def append_event(memory_root: Path, agent_slug: str, event: dict) -> None:
    event_file = memory_root / agent_slug / EVENT_LOG_NAME
    event_file.parent.mkdir(parents=True, exist_ok=True)
    with event_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def _hash_content(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


async def compact_memory(
    *, agent_slug: str, task_id: str, reason: str, memory_root: Path = MEMORY_ROOT
) -> dict:
    access = MemoryAccessLayer(memory_root=memory_root)
    content = access.read_memory(agent_slug)
    if not content:
        return {"summary": "", "summary_hash": "", "archive_path": ""}

    compressor = AdaptiveCompressor()
    summarizer = IntelligentSummarizer()

    compressed = await compressor.compress_adaptive(content, tool_name="memory")
    summary_result = await summarizer.summarize(compressed.get("compressed", content))
    summary = summary_result.get("summary", "") or content[:200]

    timestamp = datetime.now(UTC).replace(tzinfo=None).isoformat()
    file_stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    archive_dir = memory_root / agent_slug / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{file_stamp}-MEMORY.md"
    archive_path.write_text(content, encoding="utf-8")

    access.write_memory(agent_slug, summary)
    summary_hash = _hash_content(summary)

    event = {
        "event_type": "compaction_completed",
        "agent_id": agent_slug,
        "task_id": task_id,
        "timestamp": timestamp,
        "input_tokens": compressed.get("original_size", 0),
        "output_tokens": compressed.get("compressed_size", 0),
        "summary_hash": summary_hash,
        "files": [str(archive_path)],
        "reason": reason,
    }
    append_event(memory_root, agent_slug, event)

    return {
        "summary": summary,
        "summary_hash": summary_hash,
        "archive_path": str(archive_path),
    }


def merge_memory(
    current: str, incoming: str, incoming_confidence: float, incoming_priority: int
) -> str:
    marker = f"[merge] confidence={incoming_confidence} priority={incoming_priority}"
    if incoming_priority >= 5 or incoming_confidence >= 0.7:
        return f"{incoming}\n{marker}\n\n{current}"
    return f"{current}\n\n## Conflict Append\n{incoming}\n{marker}\n"


def get_last_compaction_at(
    *, memory_root: Path, agent_slug: str
) -> datetime | None:
    event_file = memory_root / agent_slug / EVENT_LOG_NAME
    if not event_file.exists():
        return None
    last_timestamp: datetime | None = None
    try:
        for line in event_file.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event_type") != "compaction_completed":
                continue
            raw_ts = event.get("timestamp")
            if not raw_ts:
                continue
            try:
                ts = datetime.fromisoformat(raw_ts)
            except ValueError:
                continue
            if last_timestamp is None or ts > last_timestamp:
                last_timestamp = ts
    except OSError:
        return None
    return last_timestamp
