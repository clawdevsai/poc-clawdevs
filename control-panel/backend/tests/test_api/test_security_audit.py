# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient):
    # Test agents list
    # Use follow_redirects=False to ensure we catch 401 directly
    response = await client.get("/agents")
    assert response.status_code == 401, f"Agents list returned {response.status_code}, expected 401"

    # Test governance
    response = await client.get("/api/governance/constitution/rules")
    assert response.status_code == 401, f"Governance rules returned {response.status_code}, expected 401"

    # Test memory RAG
    response = await client.get("/api/memory/rag/search?query=test")
    assert response.status_code == 401, f"Memory RAG search returned {response.status_code}, expected 401"

    # Test health summary
    response = await client.get("/api/health/summary")
    assert response.status_code == 401, f"Health summary returned {response.status_code}, expected 401"

@pytest.mark.asyncio
async def test_bfla_sync_agents(client: AsyncClient, db_session):
    # Create a non-admin user
    from app.core.auth import get_password_hash
    from app.models import User
    user = User(
        username="viewer",
        password_hash=get_password_hash("test-password"),
        role="viewer",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Login as viewer
    response = await client.post(
        "/auth/login",
        json={"username": "viewer", "password": "test-password"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to access admin sync endpoint
    response = await client.post("/agents/admin/sync", headers=headers)
    assert response.status_code == 403, f"Admin sync should be forbidden for viewer, got {response.status_code}"

    # Attempt to create repository
    response = await client.post("/repositories", headers=headers, json={
        "name": "test",
        "full_name": "org/test"
    })
    assert response.status_code == 403, f"Create repository should be forbidden for viewer, got {response.status_code}"
