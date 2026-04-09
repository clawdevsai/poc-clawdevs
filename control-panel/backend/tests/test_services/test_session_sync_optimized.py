# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.session import Session as SessionRow
from app.services.session_sync import sync_sessions

@pytest.mark.asyncio
async def test_sync_sessions_skips_unchanged(db_session: AsyncSession, tmp_path, monkeypatch):
    """
    Verifies that _count_messages_in_session_file is NOT called if the session
    updatedAt in the filesystem is not newer than last_active_at in the DB.
    """
    monkeypatch.setattr(
        "app.services.session_sync.settings",
        type("S", (), {"openclaw_data_path": tmp_path})(),
    )
    monkeypatch.setattr(
        "app.services.session_sync.get_discovered_agent_slugs",
        lambda: ["po"],
    )

    # 1. Setup existing session in DB
    last_active = datetime(2024, 1, 1, 12, 0, 0)
    existing_session = SessionRow(
        openclaw_session_id="sid-1",
        openclaw_session_key="agent:po:main",
        agent_slug="po",
        last_active_at=last_active,
        message_count=5
    )
    db_session.add(existing_session)
    await db_session.commit()

    # 2. Setup sessions.json with SAME timestamp
    sessions_file = tmp_path / "agents" / "po" / "sessions" / "sessions.json"
    sessions_file.parent.mkdir(parents=True)
    sessions_file.write_text(
        json.dumps({
            "agent:po:main": {
                "sessionId": "sid-1",
                "updatedAt": last_active.isoformat()
            }
        }),
        encoding="utf-8"
    )

    # 3. Sync and mock message counter
    with patch("app.services.session_sync._count_messages_in_session_file") as mock_count:
        await sync_sessions(db_session)
        # Should be skipped because updatedAt == last_active_at
        mock_count.assert_not_called()

    # 4. Update sessions.json with NEWER timestamp
    newer_active = last_active + timedelta(minutes=5)
    sessions_file.write_text(
        json.dumps({
            "agent:po:main": {
                "sessionId": "sid-1",
                "updatedAt": newer_active.isoformat()
            }
        }),
        encoding="utf-8"
    )

    with patch("app.services.session_sync._count_messages_in_session_file") as mock_count:
        mock_count.return_value = 10
        await sync_sessions(db_session)
        # Should be called because updatedAt > last_active_at
        mock_count.assert_called_once()

    # Verify DB was updated
    await db_session.refresh(existing_session)
    assert existing_session.message_count == 10
    assert existing_session.last_active_at == newer_active
