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

from datetime import datetime, UTC
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api import chat as chat_api
from app.models import Agent


async def _create_agent(db_session: AsyncSession, slug: str = "po") -> Agent:
    agent = Agent(
        slug=slug,
        display_name=slug.upper(),
        role="Product Owner",
        status="online",
        last_heartbeat_at=datetime.now(UTC).replace(tzinfo=None),
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


class TestChatApi:
    def test_stream_legacy_agent_slug_resolves_main_session(self):
        body = chat_api.ChatRequest(agent_slug="po", message="legacy")
        resolved_agent, resolved_session = chat_api._resolve_agent_and_session_key(body)

        assert resolved_agent == "po"
        assert resolved_session == "agent:po:main"

    @pytest.mark.asyncio
    async def test_stream_uses_session_key(
        self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession
    ):
        await _create_agent(db_session, "po")
        captured: dict[str, str] = {}

        async def fake_events():
            yield {"event": "done"}

        def fake_stream_chat(*, agent_slug: str, message: str, session_key: str):
            captured["agent_slug"] = agent_slug
            captured["message"] = message
            captured["session_key"] = session_key
            return fake_events()

        original_stream_chat = chat_api.openclaw_client.stream_chat
        try:
            chat_api.openclaw_client.stream_chat = fake_stream_chat
            response = await client.post(
                "/chat/stream",
                headers=auth_headers,
                json={"session_key": "agent:po:main", "message": "hello"},
            )
        finally:
            chat_api.openclaw_client.stream_chat = original_stream_chat

        assert response.status_code == 200
        assert captured == {
            "agent_slug": "po",
            "message": "hello",
            "session_key": "agent:po:main",
        }
        assert "data: [DONE]" in response.text

    @pytest.mark.asyncio
    async def test_stream_rejects_invalid_session_key(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            "/chat/stream",
            headers=auth_headers,
            json={"session_key": "main", "message": "hello"},
        )

        assert response.status_code == 422
        assert "session_key" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_stream_rejects_agent_slug_mismatch(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            "/chat/stream",
            headers=auth_headers,
            json={
                "agent_slug": "ceo",
                "session_key": "agent:po:main",
                "message": "hello",
            },
        )

        assert response.status_code == 400
        assert "agent_slug does not match" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_history_reads_specific_session_from_file_index(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        tmp_path,
        monkeypatch,
    ):
        await _create_agent(db_session, "po")
        monkeypatch.setattr(chat_api.settings, "openclaw_data_path", str(tmp_path))

        sessions_dir = tmp_path / "agents" / "po" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        (sessions_dir / "sessions.json").write_text(
            '{"agent:po:main":{"sessionId":"sess-file-1"}}',
            encoding="utf-8",
        )

        get_session_mock = AsyncMock(
            return_value={
                "messages": [{"role": "assistant", "content": "from-index"}]
            }
        )
        monkeypatch.setattr(chat_api.openclaw_client, "get_session", get_session_mock)

        response = await client.get(
            "/chat/history/po",
            headers=auth_headers,
            params={"session_key": "agent:po:main"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["agent_slug"] == "po"
        assert payload["messages"][0]["content"] == "from-index"
        get_session_mock.assert_awaited_once_with("sess-file-1")

    @pytest.mark.asyncio
    async def test_history_uses_gateway_sessions_fallback(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        tmp_path,
        monkeypatch,
    ):
        await _create_agent(db_session, "po")
        monkeypatch.setattr(chat_api.settings, "openclaw_data_path", str(tmp_path))

        monkeypatch.setattr(
            chat_api.openclaw_client,
            "get_sessions",
            AsyncMock(
                return_value=[
                    {"key": "agent:po:cron:sync", "sessionId": "sess-fallback-1"}
                ]
            ),
        )
        monkeypatch.setattr(
            chat_api.openclaw_client,
            "get_session",
            AsyncMock(
                return_value={
                    "messages": [{"role": "assistant", "content": "from-fallback"}]
                }
            ),
        )

        response = await client.get(
            "/chat/history/po",
            headers=auth_headers,
            params={"session_key": "agent:po:cron:sync"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["messages"][0]["content"] == "from-fallback"

    @pytest.mark.asyncio
    async def test_history_session_not_found_returns_empty(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        tmp_path,
        monkeypatch,
    ):
        await _create_agent(db_session, "po")
        monkeypatch.setattr(chat_api.settings, "openclaw_data_path", str(tmp_path))
        monkeypatch.setattr(chat_api.openclaw_client, "get_sessions", AsyncMock(return_value=[]))

        response = await client.get(
            "/chat/history/po",
            headers=auth_headers,
            params={"session_key": "agent:po:main"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["agent_slug"] == "po"
        assert payload["messages"] == []
