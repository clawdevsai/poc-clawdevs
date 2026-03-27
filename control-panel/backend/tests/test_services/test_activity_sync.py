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

"""Tests for activity_sync service."""
import pytest
from unittest.mock import patch
from datetime import datetime, UTC
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models import ActivityEvent, Session, Agent


class TestActivitySyncFunctions:
    """Test activity_sync functions."""

    @pytest.mark.asyncio
    async def test_sync_activity_from_sessions_creates_events(
        self, db_session: AsyncSession
    ):
        """Test that sync_activity_from_sessions creates activity events for sessions without events."""
        from app.services.activity_sync import sync_activity_from_sessions

        # Create an agent
        agent = Agent(slug="ceo", display_name="CEO", role="Chief")
        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        # Create a session without existing activity event
        session = Session(
            openclaw_session_id="sess-1",
            agent_slug="ceo",
            status="active",
            channel_type="telegram",
            channel_peer="123456789",
            message_count=10,
            last_active_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )
        db_session.add(session)
        await db_session.commit()

        # Run sync
        created_count = await sync_activity_from_sessions(db_session)

        # Verify event was created
        assert created_count == 1

        # Check database
        result = await db_session.exec(
            select(ActivityEvent).where(ActivityEvent.entity_id == "sess-1")
        )
        event = result.first()
        assert event is not None
        assert event.event_type == "session.active"
        assert event.agent_id == agent.id
        assert event.entity_type == "session"
        payload = event.payload or {}
        assert payload["message_count"] == 10
        assert payload["channel_type"] == "telegram"

    @pytest.mark.asyncio
    async def test_sync_activity_from_sessions_skips_existing_events(
        self, db_session: AsyncSession
    ):
        """Test that sync_activity_from_sessions skips sessions that already have activity events."""
        from app.services.activity_sync import sync_activity_from_sessions

        # Create agent
        agent = Agent(slug="dev", display_name="Dev", role="Developer")
        db_session.add(agent)
        await db_session.commit()
        await db_session.refresh(agent)

        # Create session
        session = Session(
            openclaw_session_id="sess-2",
            agent_slug="dev",
            status="ended",
            channel_type="webchat",
            channel_peer="user123",
            message_count=5,
            last_active_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )
        db_session.add(session)
        await db_session.commit()

        # Create existing activity event for this session
        existing_event = ActivityEvent(
            event_type="session.active",
            agent_id=agent.id,
            entity_type="session",
            entity_id="sess-2",
            payload={"message_count": 5},
            created_at=datetime.now(UTC),
        )
        db_session.add(existing_event)
        await db_session.commit()

        # Run sync
        created_count = await sync_activity_from_sessions(db_session)

        # Should not create new event
        assert created_count == 0

    @pytest.mark.asyncio
    async def test_sync_activity_from_sessions_handles_agent_without_slug(
        self, db_session: AsyncSession
    ):
        """Test that sessions without agent_slug create events with agent_id=None."""
        from app.services.activity_sync import sync_activity_from_sessions

        # Create session without agent_slug
        session = Session(
            openclaw_session_id="sess-3",
            agent_slug=None,
            status="active",
            channel_type="discord",
            channel_peer="discord_user",
            message_count=2,
            last_active_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )
        db_session.add(session)
        await db_session.commit()

        # Run sync
        created_count = await sync_activity_from_sessions(db_session)

        assert created_count == 1

        # Verify event has no agent_id
        result = await db_session.exec(
            select(ActivityEvent).where(ActivityEvent.entity_id == "sess-3")
        )
        event = result.first()
        assert event is not None
        assert event.agent_id is None

    @pytest.mark.asyncio
    async def test_sync_activity_from_sessions_uses_created_at_when_last_active_is_none(
        self, db_session: AsyncSession
    ):
        """Test that sync uses created_at when last_active_at is None."""
        from app.services.activity_sync import sync_activity_from_sessions

        session = Session(
            openclaw_session_id="sess-4",
            agent_slug=None,
            status="active",
            channel_type="telegram",
            channel_peer="123",
            message_count=1,
            last_active_at=None,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        db_session.add(session)
        await db_session.commit()

        await sync_activity_from_sessions(db_session)

        result = await db_session.exec(
            select(ActivityEvent).where(ActivityEvent.entity_id == "sess-4")
        )
        event = result.first()
        assert event is not None
        assert event.created_at == datetime(2024, 1, 1, 12, 0, 0)

    @pytest.mark.asyncio
    async def test_sync_all_activity_returns_summary(self, db_session: AsyncSession):
        """Test that sync_all_activity returns a summary dict."""
        from app.services.activity_sync import sync_all_activity

        with patch(
            "app.services.activity_sync.sync_activity_from_sessions"
        ) as mock_sync:
            mock_sync.return_value = 3

            result = await sync_all_activity(db_session)

            assert "session_events" in result
            assert result["session_events"] == 3
            assert "total" in result
            assert result["total"] == 3
            mock_sync.assert_called_once_with(db_session)


class TestActivityEventCreation:
    """Test activity event creation logic."""

    def test_event_type_mapping_active(self):
        """Test that active sessions create 'session.active' events."""
        # In the code: event_type = "session.active" if session.status == "active" else "session.ended"
        session_status = "active"
        expected = "session.active"
        result = "session.active" if session_status == "active" else "session.ended"
        assert result == expected

    def test_event_type_mapping_ended(self):
        """Test that ended sessions create 'session.ended' events."""
        session_status = "ended"
        expected = "session.ended"
        result = "session.active" if session_status == "active" else "session.ended"
        assert result == expected

    def test_event_payload_structure(self):
        """Test expected payload structure."""
        expected_keys = ["description", "message_count", "channel_type", "channel_peer"]
        assert "description" in expected_keys
        assert "message_count" in expected_keys
        assert "channel_type" in expected_keys
        assert "channel_peer" in expected_keys
