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
Tests for session_sync service.
"""
import json

import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.session import Session as SessionRow


class TestSyncSessions:
    """Test sync_sessions function with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_sync_persists_openclaw_session_keys(
        self, db_session: AsyncSession, tmp_path, monkeypatch
    ):
        """sessions.json keys are stored as openclaw_session_key."""
        monkeypatch.setattr(
            "app.services.session_sync.settings",
            type("S", (), {"openclaw_data_path": tmp_path})(),
        )
        monkeypatch.setattr(
            "app.services.session_sync.get_discovered_agent_slugs",
            lambda: ["po"],
        )
        sessions_file = tmp_path / "agents" / "po" / "sessions" / "sessions.json"
        sessions_file.parent.mkdir(parents=True)
        sessions_file.write_text(
            json.dumps(
                {
                    "agent:po:main": {
                        "sessionId": "sid-main",
                        "updatedAt": 1_710_000_000_000,
                    },
                    "agent:po:delegation-xyz": {
                        "sessionId": "sid-sub",
                        "updatedAt": 1_710_000_000_000,
                    },
                }
            ),
            encoding="utf-8",
        )
        from app.services.session_sync import sync_sessions

        await sync_sessions(db_session)
        result = await db_session.exec(select(SessionRow))
        rows = list(result.all())
        assert len(rows) == 2
        by_key = {r.openclaw_session_key: r for r in rows}
        assert by_key["agent:po:main"].openclaw_session_id == "sid-main"
        assert by_key["agent:po:delegation-xyz"].openclaw_session_id == "sid-sub"

    @pytest.mark.asyncio
    async def test_sync_sessions_handles_missing_file(
        self, db_session: AsyncSession, tmp_path, monkeypatch
    ):
        """No sessions.json: sync commits with no rows."""
        monkeypatch.setattr(
            "app.services.session_sync.settings",
            type("S", (), {"openclaw_data_path": tmp_path})(),
        )
        monkeypatch.setattr(
            "app.services.session_sync.get_discovered_agent_slugs",
            lambda: ["po"],
        )
        from app.services.session_sync import sync_sessions

        await sync_sessions(db_session)
        result = await db_session.exec(select(SessionRow))
        assert list(result.all()) == []


class TestParseTimestamp:
    """Test _parse_timestamp helper function."""

    def test_parse_timestamp_valid(self):
        """Test parsing valid timestamp."""
        from app.services.session_sync import _parse_timestamp

        result = _parse_timestamp("1234567890.123")
        assert result is not None


class TestCountMessagesInSessionFile:
    """Test _count_messages_in_session_file helper function."""

    def test_count_messages_valid_file(self, tmp_path):
        """Test counting messages in valid session file."""
        from app.services.session_sync import _count_messages_in_session_file

        session_file = tmp_path / "session.jsonl"
        session_file.write_text(
            json.dumps({"type": "message", "message": {"role": "user", "content": "hi"}}) + "\n" +
            json.dumps({"type": "message", "message": {"role": "assistant", "content": "hello"}}) + "\n" +
            json.dumps({"type": "other", "something": "else"}) + "\n",
            encoding="utf-8"
        )

        assert _count_messages_in_session_file(session_file) == 2


@pytest.mark.asyncio
async def test_sync_sessions_skips_unchanged(db_session: AsyncSession, tmp_path, monkeypatch):
    """Verify that _count_messages_in_session_file is skipped for unchanged sessions."""
    from datetime import datetime, timezone
    from app.services.session_sync import sync_sessions
    import app.services.session_sync as session_sync
    from unittest.mock import MagicMock

    # Setup
    monkeypatch.setattr(session_sync, "settings", type("S", (), {"openclaw_data_path": tmp_path})())
    monkeypatch.setattr(session_sync, "get_discovered_agent_slugs", lambda: ["po"])

    ts = 1_710_000_000_000
    dt = datetime.fromtimestamp(ts / 1000, timezone.utc).replace(tzinfo=None)

    # Create existing session in DB
    existing = SessionRow(
        openclaw_session_id="sid-1",
        openclaw_session_key="key-1",
        agent_slug="po",
        status="completed",
        last_active_at=dt,
        message_count=10
    )
    db_session.add(existing)
    await db_session.commit()

    # Setup filesystem
    sessions_file = tmp_path / "agents" / "po" / "sessions" / "sessions.json"
    sessions_file.parent.mkdir(parents=True)
    sessions_file.write_text(json.dumps({
        "key-1": {
            "sessionId": "sid-1",
            "updatedAt": ts,
        }
    }))

    # Mock _count_messages_in_session_file to track calls
    mock_count = MagicMock(return_value=10)
    monkeypatch.setattr(session_sync, "_count_messages_in_session_file", mock_count)

    # First sync should skip because timestamps and status match
    await sync_sessions(db_session)
    mock_count.assert_not_called()

    # Update updatedAt in JSON
    new_ts = ts + 1000
    sessions_file.write_text(json.dumps({
        "key-1": {
            "sessionId": "sid-1",
            "updatedAt": new_ts,
        }
    }))

    # Second sync should call it
    await sync_sessions(db_session)
    mock_count.assert_called_once()
