"""
Unit tests for MemoryEntry model.
"""

from datetime import UTC, datetime
from uuid import UUID


class TestMemoryEntryModel:
    def test_memory_entry_creation(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(
            entry_type="active",
            title="Test memory",
            body="This is a test memory",
        )

        assert entry.entry_type == "active"
        assert entry.title == "Test memory"
        assert entry.body == "This is a test memory"
        assert entry.id is not None
        assert isinstance(entry.id, UUID)

    def test_memory_entry_with_agent(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(
            entry_type="active",
            title="Agent memory",
            body="Agent-specific memory",
            agent_slug="qa_engineer",
        )

        assert entry.agent_slug == "qa_engineer"

    def test_memory_entry_with_tags(self):
        from app.models.memory_entry import MemoryEntry

        tags = ["important", "urgent", "review"]
        entry = MemoryEntry(
            entry_type="active",
            title="Tagged memory",
            body="Memory with tags",
            tags=tags,
        )

        assert entry.tags == tags

    def test_memory_entry_with_source_agents(self):
        from app.models.memory_entry import MemoryEntry

        source_agents = ["agent-1", "agent-2"]
        entry = MemoryEntry(
            entry_type="active",
            title="Aggregated memory",
            body="Aggregated memory",
            source_agents=source_agents,
        )

        assert entry.source_agents == source_agents

    def test_memory_entry_status_values(self):
        from app.models.memory_entry import MemoryEntry

        valid_types = ["active", "candidate", "global", "archived"]
        for entry_type in valid_types:
            entry = MemoryEntry(
                entry_type=entry_type,
                title=f"Memory {entry_type}",
                body=f"Memory type {entry_type}",
            )
            assert entry.entry_type == entry_type

    def test_memory_entry_shared(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(
            entry_type="global",
            title="Shared memory",
            body="Shared knowledge for all agents",
        )

        assert entry.agent_slug is None

    def test_memory_entry_embedding_timestamp(self):
        from app.models.memory_entry import MemoryEntry

        now = datetime.now(UTC)
        entry = MemoryEntry(
            entry_type="candidate",
            title="Embedding test",
            body="Pending embedding",
            embedding_generated_at=now,
        )

        assert entry.embedding_generated_at == now

    def test_memory_entry_timestamps(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(
            entry_type="active",
            title="Timestamp test",
            body="Timestamp body",
        )

        assert entry.created_at is not None
        assert entry.updated_at is not None
        assert isinstance(entry.created_at, datetime)


class TestMemoryEntryWorkflow:
    def test_candidate_to_active(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(entry_type="candidate", title="Candidate", body="Body")
        entry.entry_type = "active"
        assert entry.entry_type == "active"

    def test_active_to_archived(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(entry_type="active", title="Active", body="Body")
        entry.entry_type = "archived"
        assert entry.entry_type == "archived"


class TestMemoryEntryTypes:
    def test_global_memory_type(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(entry_type="global", title="Global", body="Shared")
        assert entry.entry_type == "global"

    def test_archived_memory_type(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(entry_type="archived", title="Archived", body="History")
        assert entry.entry_type == "archived"


class TestMemoryEntryEdgeCases:
    def test_memory_entry_id_is_uuid(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(
            entry_type="active",
            title="UUID test",
            body="Memory with UUID",
        )

        assert isinstance(entry.id, UUID)
        assert len(str(entry.id)) == 36

    def test_memory_entry_empty_body(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(
            entry_type="active",
            title="Empty body",
            body="",
        )

        assert entry.body == ""

    def test_memory_entry_none_values(self):
        from app.models.memory_entry import MemoryEntry

        entry = MemoryEntry(
            entry_type="active",
            title="None values",
            agent_slug=None,
            tags=None,
            source_agents=None,
        )

        assert entry.agent_slug is None
        assert entry.tags is None
        assert entry.source_agents is None

    def test_memory_entry_large_body(self):
        from app.models.memory_entry import MemoryEntry

        body = "x" * 100000
        entry = MemoryEntry(
            entry_type="active",
            title="Large body",
            body=body,
        )

        assert len(entry.body or "") == 100000
