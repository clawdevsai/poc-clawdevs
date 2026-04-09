# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_agents_requires_auth(client: AsyncClient):
    """Verify that GET /agents requires authentication."""
    response = await client.get("/agents")
    assert response.status_code == 401
    # FastAPI returns "Not authenticated" when the security scheme (HTTPBearer)
    # is missing the token entirely.
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_health_summary_requires_auth(client: AsyncClient):
    """Verify that GET /api/health/summary requires authentication."""
    response = await client.get("/api/health/summary")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_health_failures_requires_auth(client: AsyncClient):
    """Verify that GET /api/health/failures requires authentication."""
    response = await client.get("/api/health/failures")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_health_escalations_requires_auth(client: AsyncClient):
    """Verify that GET /api/health/escalations requires authentication."""
    response = await client.get("/api/health/escalations")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_health_task_requires_auth(client: AsyncClient):
    """Verify that GET /api/health/tasks/{id} requires authentication."""
    # Use the prefix /api/health as defined in the health_api router
    response = await client.get("/api/health/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_list_agents_authenticated(client: AsyncClient, auth_headers: dict):
    """Verify that GET /agents works when authenticated."""
    response = await client.get("/agents", headers=auth_headers)
    assert response.status_code == 200
    assert "items" in response.json()
