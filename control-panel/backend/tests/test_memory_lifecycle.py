import json
from pathlib import Path

import pytest

from app.services import memory_lifecycle


@pytest.mark.asyncio
async def test_compact_memory_writes_archive_and_event(tmp_path, monkeypatch):
    memory_root = tmp_path / "memory"
    agent_dir = memory_root / "agent1"
    agent_dir.mkdir(parents=True, exist_ok=True)
    memory_file = agent_dir / "MEMORY.md"
    memory_file.write_text("# Memory\nLine 1\nLine 2\n", encoding="utf-8")

    async def fake_compress(self, output, tool_name=""):
        return {
            "compressed": output,
            "original_size": len(output),
            "compressed_size": len(output),
        }

    async def fake_summarize(self, content, intent=None, max_words=100):
        return {"summary": "summary", "key_points": []}

    monkeypatch.setattr(memory_lifecycle.AdaptiveCompressor, "compress_adaptive", fake_compress)
    monkeypatch.setattr(memory_lifecycle.IntelligentSummarizer, "summarize", fake_summarize)

    result = await memory_lifecycle.compact_memory(
        agent_slug="agent1",
        task_id="task1",
        reason="test",
        memory_root=memory_root,
    )

    assert Path(result["archive_path"]).exists()
    events_file = agent_dir / "events.jsonl"
    assert events_file.exists()
    events = [json.loads(line) for line in events_file.read_text().splitlines()]
    assert any(event.get("event_type") == "compaction_completed" for event in events)


def test_merge_memory_prefers_high_priority():
    merged = memory_lifecycle.merge_memory(
        "current", "incoming", incoming_confidence=0.8, incoming_priority=1
    )
    assert merged.startswith("incoming")
    assert "[merge] confidence=0.8 priority=1" in merged


def test_merge_memory_appends_low_priority():
    merged = memory_lifecycle.merge_memory(
        "current", "incoming", incoming_confidence=0.2, incoming_priority=1
    )
    assert "## Conflict Append" in merged
    assert merged.startswith("current")
    assert "[merge] confidence=0.2 priority=1" in merged
