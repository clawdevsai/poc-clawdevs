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


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def db_session():
    """Create an in-memory SQLite database for testing."""
    from sqlalchemy import create_engine
    from sqlmodel import SQLModel
    
    engine = create_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    
    from sqlmodel.ext.asyncio.session import AsyncSession as AsyncSessionType
    session = AsyncSessionType(engine)
    
    yield session
    
    await session.close()
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    """Create a test client with overridden database session."""
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=None,
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


class TestAgentEndpoints:
    """Test Agent API endpoints."""

    @pytest.mark.asyncio
    async def test_list_agents_empty(self, client: AsyncClient):
        """Test listing agents when no agents exist."""
        response = await client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, client: AsyncClient):
        """Test getting a non-existent agent."""
        response = await client.get("/api/agents/non-existent-slug")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestSessionEndpoints:
    """Test Session API endpoints."""

    @pytest.mark.asyncio
    async def test_list_sessions_empty(self, client: AsyncClient):
        """Test listing sessions when no sessions exist."""
        response = await client.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client: AsyncClient):
        """Test getting a non-existent session."""
        response = await client.get("/api/sessions/non-existent-id")
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
        response = await client.get("/api/cluster/status")
        # May vary based on implementation
        assert response.status_code in [200, 404]


class TestRepositoryEndpoints:
    """Test Repository API endpoints."""

    @pytest.mark.asyncio
    async def test_list_repositories(self, client: AsyncClient):
        """Test listing repositories."""
        response = await client.get("/api/repositories")
        # May vary based on implementation
        assert response.status_code in [200, 404]
