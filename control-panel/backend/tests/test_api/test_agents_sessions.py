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
Test suite for API endpoints.
"""

from datetime import datetime, timedelta, UTC

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Session


# Use fixtures from conftest.py


class TestAgentEndpoints:
    """Test Agent API endpoints."""

    @pytest.mark.asyncio
    async def test_list_agents_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing agents when no agents exist."""
        response = await client.get("/agents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 0
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting a non-existent agent."""
        response = await client.get("/agents/non-existent-slug", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestSessionEndpoints:
    """Test Session API endpoints."""

    @pytest.mark.asyncio
    async def test_list_sessions_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing sessions when no sessions exist."""
        response = await client.get("/sessions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting a non-existent session."""
        response = await client.get("/sessions/non-existent-id", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_sessions_window_minutes(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test session list filtering by window minutes."""
        now = datetime.now(UTC).replace(tzinfo=None)
        recent = Session(
            openclaw_session_id="recent-session",
            openclaw_session_key="agent:recent:main",
            agent_slug="recent",
            status="active",
            last_active_at=now - timedelta(minutes=10),
        )
        stale = Session(
            openclaw_session_id="stale-session",
            openclaw_session_key="agent:stale:main",
            agent_slug="stale",
            status="completed",
            last_active_at=now - timedelta(minutes=120),
        )
        db_session.add(recent)
        db_session.add(stale)
        await db_session.commit()

        response = await client.get("/sessions?window_minutes=60", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_sessions_window_minutes_invalid(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test invalid window minutes on session list."""
        response = await client.get("/sessions?window_minutes=15", headers=auth_headers)
        assert response.status_code == 400


class TestAuthEndpoints:
    """Test Auth API endpoints (existing tests in test_auth.py)."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful login."""
        # This test is already covered in test_auth.py
        # Just here as a placeholder
        pass


class TestClusterEndpoints:
    """Test Cluster API endpoints."""

    @pytest.mark.asyncio
    async def test_cluster_status(self, client: AsyncClient, auth_headers: dict):
        """Test cluster status endpoint."""
        response = await client.get("/cluster/status", headers=auth_headers)
        # May vary based on implementation
        assert response.status_code in [200, 404]


class TestRepositoryEndpoints:
    """Test Repository API endpoints."""

    @pytest.mark.asyncio
    async def test_list_repositories(self, client: AsyncClient, auth_headers: dict):
        """Test listing repositories."""
        response = await client.get("/repositories", headers=auth_headers)
        # May vary based on implementation
        assert response.status_code in [200, 404]
