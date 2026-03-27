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

"""
Unit tests for MemoryEntry model - 100% mocked, no external access.
"""

from datetime import datetime
from uuid import UUID, uuid4


class TestMemoryEntryModel:
    """Test MemoryEntry model creation and validation - UNIT TESTS ONLY."""

    def test_memory_entry_creation(self):
        """Test basic memory entry creation."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="active",
            content="This is a test memory",
        )
        
        assert entry.entry_type == "active"
        assert entry.content == "This is a test memory"
        assert entry.id is not None
        assert isinstance(entry.id, UUID)

    def test_memory_entry_with_agent(self):
        """Test memory entry linked to agent."""
        from app.models.memory_entry import MemoryEntry
        
        agent_id = uuid4()
        
        entry = MemoryEntry(
            entry_type="active",
            content="Agent-specific memory",
            agent_id=agent_id,
        )
        
        assert entry.agent_id == agent_id

    def test_memory_entry_with_tags(self):
        """Test memory entry with tags."""
        from app.models.memory_entry import MemoryEntry
        
        tags = ["important", "urgent", "review"]
        
        entry = MemoryEntry(
            entry_type="active",
            content="Memory with tags",
            tags=tags,
        )
        
        assert entry.tags == tags

    def test_memory_entry_with_source_agents(self):
        """Test memory entry with source agents."""
        from app.models.memory_entry import MemoryEntry
        
        source_agents = ["agent-1", "agent-2"]
        
        entry = MemoryEntry(
            entry_type="active",
            content="Aggregated memory",
            source_agents=source_agents,
        )
        
        assert entry.source_agents == source_agents

    def test_memory_entry_status_values(self):
        """Test valid entry_type values for memory entry."""
        from app.models.memory_entry import MemoryEntry
        
        valid_types = ["active", "candidate", "global", "archived"]
        
        for entry_type in valid_types:
            entry = MemoryEntry(
                entry_type=entry_type,
                content=f"Memory type {entry_type}",
            )
            assert entry.entry_type == entry_type

    def test_memory_entry_shared(self):
        """Test shared memory entry (null agent)."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="global",
            content="Shared knowledge for all agents",
        )
        
        assert entry.agent_id is None

    def test_memory_entry_promotion(self):
        """Test memory entry promotion."""
        from app.models.memory_entry import MemoryEntry
        from datetime import datetime
        
        now = datetime.utcnow()
        
        entry = MemoryEntry(
            entry_type="candidate",
            content="Pending promotion",
            promoted_at=now,
        )
        
        assert entry.promoted_at == now

    def test_memory_entry_timestamps(self):
        """Test automatic timestamp creation."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="active",
            content="Timestamp test",
        )
        
        assert entry.created_at is not None
        assert entry.updated_at is not None
        assert isinstance(entry.created_at, datetime)


class TestMemoryEntryWorkflow:
    """Test memory entry workflow transitions - UNIT TESTS ONLY."""

    def test_candidate_to_active(self):
        """Test memory promotion from candidate to active."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="candidate",
            content="Candidate memory",
        )
        
        entry.entry_type = "active"
        
        assert entry.entry_type == "active"

    def test_active_to_archived(self):
        """Test memory archival."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="active",
            content="Active memory to archive",
        )
        
        entry.entry_type = "archived"
        
        assert entry.entry_type == "archived"


class TestMemoryEntryTypes:
    """Test different memory entry types - UNIT TESTS ONLY."""

    def test_active_memory(self):
        """Test active memory type."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="active",
            content="Currently used memory",
        )
        
        assert entry.entry_type == "active"

    def test_global_memory(self):
        """Test global memory type (shared)."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="global",
            content="Shared across all agents",
        )
        
        assert entry.entry_type == "global"

    def test_archived_memory(self):
        """Test archived memory type."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="archived",
            content="Historical memory",
        )
        
        assert entry.entry_type == "archived"


class TestMemoryEntryEdgeCases:
    """Test edge cases for MemoryEntry model."""

    def test_memory_entry_id_is_uuid(self):
        """Test that memory entry ID is UUID."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="uuid-memory",
            content="Memory with UUID",
        )
        
        assert isinstance(entry.id, UUID)
        assert len(str(entry.id)) == 36

    def test_memory_entry_empty_content(self):
        """Test memory entry with empty content."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="empty-memory",
            content="",
        )
        
        assert entry.content == ""

    def test_memory_entry_none_values(self):
        """Test memory entry with None values."""
        from app.models.memory_entry import MemoryEntry
        
        entry = MemoryEntry(
            entry_type="none-values-memory",
            agent_id=None,
            tags=None,
            source_agents=None,
        )
        
        assert entry.agent_id is None
        assert entry.tags is None
        assert entry.source_agents is None

    def test_memory_entry_large_content(self):
        """Test memory entry with large content."""
        from app.models.memory_entry import MemoryEntry
        
        content = "x" * 100000
        
        entry = MemoryEntry(
            entry_type="large-content-memory",
            content=content,
        )
        
        assert len(entry.content) == 100000
