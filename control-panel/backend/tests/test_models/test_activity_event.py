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
Unit tests for ActivityEvent model - 100% mocked, no external access.
"""

from datetime import datetime
from uuid import UUID, uuid4


class TestActivityEventModel:
    """Test ActivityEvent model creation and validation - UNIT TESTS ONLY."""

    def test_activity_event_creation(self):
        """Test basic activity event creation."""
        from app.models.activity_event import ActivityEvent

        event = ActivityEvent(
            event_type="user_login",
        )

        assert event.event_type == "user_login"
        assert event.id is not None
        assert isinstance(event.id, UUID)

    def test_activity_event_with_agent(self):
        """Test activity event linked to agent."""
        from app.models.activity_event import ActivityEvent

        agent_id = uuid4()

        event = ActivityEvent(
            event_type="agent_start",
            agent_id=agent_id,
        )

        assert event.agent_id == agent_id

    def test_activity_event_with_user(self):
        """Test activity event linked to user."""
        from app.models.activity_event import ActivityEvent

        user_id = uuid4()

        event = ActivityEvent(
            event_type="user_created",
            user_id=user_id,
        )

        assert event.user_id == user_id

    def test_activity_event_with_payload(self):
        """Test activity event with JSON payload."""
        from app.models.activity_event import ActivityEvent

        payload = {
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "location": "New York",
        }

        event = ActivityEvent(
            event_type="api_call",
            payload=payload,
        )

        assert event.payload == payload

    def test_activity_event_with_entity(self):
        """Test activity event with entity reference."""
        from app.models.activity_event import ActivityEvent

        event = ActivityEvent(
            event_type="entity_updated",
            entity_type="task",
            entity_id="task-123",
        )

        assert event.entity_type == "task"
        assert event.entity_id == "task-123"

    def test_activity_event_timestamp(self):
        """Test automatic timestamp creation."""
        from app.models.activity_event import ActivityEvent

        event = ActivityEvent(
            event_type="test_event",
        )

        assert event.created_at is not None
        assert isinstance(event.created_at, datetime)


class TestActivityEventEdgeCases:
    """Test edge cases for ActivityEvent model."""

    def test_event_id_is_uuid(self):
        """Test that event ID is UUID."""
        from app.models.activity_event import ActivityEvent

        event = ActivityEvent(
            event_type="uuid-event",
        )

        assert isinstance(event.id, UUID)
        assert len(str(event.id)) == 36

    def test_event_empty_payload(self):
        """Test activity event with empty payload."""
        from app.models.activity_event import ActivityEvent

        event = ActivityEvent(
            event_type="empty-payload-event",
            payload={},
        )

        assert event.payload == {}

    def test_event_none_values(self):
        """Test activity event with None values."""
        from app.models.activity_event import ActivityEvent

        event = ActivityEvent(
            event_type="none-values-event",
            agent_id=None,
            user_id=None,
        )

        assert event.agent_id is None
        assert event.user_id is None

    def test_event_large_payload(self):
        """Test activity event with large payload."""
        from app.models.activity_event import ActivityEvent

        payload = {"key": "x" * 10000 for _ in range(100)}

        event = ActivityEvent(
            event_type="large-payload-event",
            payload=payload,
        )

        assert len(event.payload) > 0


class TestActivityEventTypeValues:
    """Test activity event type values - UNIT TESTS ONLY."""

    def test_valid_event_types(self):
        """Test various event types."""
        from app.models.activity_event import ActivityEvent

        valid_types = [
            "user_login",
            "user_logout",
            "user_created",
            "agent_start",
            "agent_stop",
            "agent_error",
            "api_call",
            "api_error",
            "entity_created",
            "entity_updated",
            "entity_deleted",
        ]

        for event_type in valid_types:
            event = ActivityEvent(
                event_type=event_type,
            )
            assert event.event_type == event_type


class TestActivityEventUpdate:
    """Test updating activity events - UNIT TESTS ONLY."""

    def test_update_event_type(self):
        """Test updating event type."""
        from app.models.activity_event import ActivityEvent

        event = ActivityEvent(
            event_type="original_type",
        )

        event.event_type = "updated_type"

        assert event.event_type == "updated_type"

    def test_update_payload(self):
        """Test updating payload."""
        from app.models.activity_event import ActivityEvent

        event = ActivityEvent(
            event_type="test-event",
            payload={"key": "value1"},
        )

        event.payload = {"key": "value2"}

        assert event.payload == {"key": "value2"}
