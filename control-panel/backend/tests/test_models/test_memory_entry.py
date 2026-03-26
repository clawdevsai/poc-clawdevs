import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, create_engine, Session
from app.models.memory_entry import MemoryEntry


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


class TestMemoryEntryModel:
    """Test MemoryEntry model creation and validation."""

    def test_memory_entry_creation(self, db_session):
        """Test basic memory entry creation."""
        entry = MemoryEntry(
            entry_type="active",
            content="This is a test memory",
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.id is not None
        assert isinstance(entry.id, UUID)
        assert entry.entry_type == "active"
        assert entry.content == "This is a test memory"
        assert entry.created_at is not None

    def test_memory_entry_with_agent(self, db_session):
        """Test memory entry linked to agent."""
        agent_id = uuid4()
        entry = MemoryEntry(
            entry_type="active",
            content="Agent-specific memory",
            agent_id=agent_id,
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.agent_id == agent_id

    def test_memory_entry_with_tags(self, db_session):
        """Test memory entry with tags."""
        tags = ["important", "urgent", "review"]
        entry = MemoryEntry(
            entry_type="active",
            content="Memory with tags",
            tags=tags,
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.tags == tags

    def test_memory_entry_with_source_agents(self, db_session):
        """Test memory entry with source agents."""
        source_agents = ["agent-1", "agent-2"]
        entry = MemoryEntry(
            entry_type="active",
            content="Aggregated memory",
            source_agents=source_agents,
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.source_agents == source_agents

    def test_memory_entry_status_values(self, db_session):
        """Test valid entry_type values for memory entry."""
        valid_types = ["active", "candidate", "global", "archived"]

        for entry_type in valid_types:
            entry = MemoryEntry(
                entry_type=entry_type,
                content=f"Memory type {entry_type}",
            )
            db_session.add(entry)
            db_session.commit()

            assert entry.entry_type == entry_type

    def test_memory_entry_shared(self, db_session):
        """Test shared memory entry (null agent)."""
        entry = MemoryEntry(
            entry_type="global",
            content="Shared knowledge for all agents",
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.agent_id is None

    def test_memory_entry_promotion(self, db_session):
        """Test memory entry promotion."""
        now = datetime.utcnow()
        entry = MemoryEntry(
            entry_type="candidate",
            content="Pending promotion",
            promoted_at=now,
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.promoted_at == now

    def test_memory_entry_timestamps(self, db_session):
        """Test automatic timestamp creation."""
        entry = MemoryEntry(
            entry_type="active",
            content="Timestamp test",
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.created_at is not None
        assert entry.updated_at is not None
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.updated_at, datetime)


class TestMemoryEntryWorkflow:
    """Test memory entry workflow transitions."""

    def test_candidate_to_active(self, db_session):
        """Test memory promotion from candidate to active."""
        entry = MemoryEntry(
            entry_type="candidate",
            content="Candidate memory",
        )
        db_session.add(entry)
        db_session.commit()

        entry.entry_type = "active"
        db_session.commit()

        assert entry.entry_type == "active"

    def test_active_to_archived(self, db_session):
        """Test memory archival."""
        entry = MemoryEntry(
            entry_type="active",
            content="Active memory to archive",
        )
        db_session.add(entry)
        db_session.commit()

        entry.entry_type = "archived"
        db_session.commit()

        assert entry.entry_type == "archived"


class TestMemoryEntryTypes:
    """Test different memory entry types."""

    def test_active_memory(self, db_session):
        """Test active memory type."""
        entry = MemoryEntry(
            entry_type="active",
            content="Currently used memory",
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.entry_type == "active"

    def test_global_memory(self, db_session):
        """Test global memory type (shared)."""
        entry = MemoryEntry(
            entry_type="global",
            content="Shared across all agents",
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.entry_type == "global"

    def test_archived_memory(self, db_session):
        """Test archived memory type."""
        entry = MemoryEntry(
            entry_type="archived",
            content="Historical memory",
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.entry_type == "archived"
