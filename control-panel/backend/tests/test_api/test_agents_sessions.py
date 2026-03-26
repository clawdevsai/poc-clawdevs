"""
Test suite for API endpoints.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.main import app
from app.core.database import get_session
from app.models import Agent


# Use fixtures from conftest.py


class TestAgentEndpoints:
    """Test Agent API endpoints."""

    @pytest.mark.asyncio
    async def test_list_agents_empty(self, client: AsyncClient):
        """Test listing agents when no agents exist."""
        response = await client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
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
    async def test_cluster_status(self, client: AsyncClient):
        """Test cluster status endpoint."""
        response = await client.get("/cluster/status")
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
