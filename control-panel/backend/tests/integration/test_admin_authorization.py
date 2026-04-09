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

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import User, Agent, Repository
from app.core.auth import get_password_hash
from uuid import uuid4

@pytest.fixture
async def regular_user(db_session: AsyncSession) -> User:
    user = User(
        username="regular-user",
        password_hash=get_password_hash("test-password"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def regular_auth_headers(client: AsyncClient, regular_user: User) -> dict:
    response = await client.post(
        "/auth/login",
        json={"username": "regular-user", "password": "test-password"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_sync_agents_admin_requires_admin(client: AsyncClient, regular_auth_headers: dict):
    """Test that POST /agents/admin/sync requires admin role."""
    response = await client.post("/agents/admin/sync", headers=regular_auth_headers)
    # This is expected to FAIL (return 200) before the fix
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_cluster_pods_requires_admin(client: AsyncClient, regular_auth_headers: dict):
    """Test that GET /cluster/pods requires admin role."""
    response = await client.get("/cluster/pods", headers=regular_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_trigger_cron_requires_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    regular_auth_headers: dict
):
    """Test that POST /crons/{agent_slug}/trigger requires admin role."""
    agent = Agent(slug="test-agent", display_name="Test Agent", role="tester")
    db_session.add(agent)
    await db_session.commit()

    response = await client.post("/crons/test-agent/trigger", headers=regular_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_repository_requires_admin(client: AsyncClient, regular_auth_headers: dict):
    """Test that POST /repositories requires admin role."""
    payload = {
        "name": "new-repo",
        "full_name": "org/new-repo"
    }
    response = await client.post("/repositories", json=payload, headers=regular_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_repository_requires_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    regular_auth_headers: dict
):
    """Test that PATCH /repositories/{id} requires admin role."""
    repo = Repository(name="test", full_name="org/test")
    db_session.add(repo)
    await db_session.commit()

    response = await client.patch(f"/repositories/{repo.id}", json={"name": "updated"}, headers=regular_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_repository_requires_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    regular_auth_headers: dict
):
    """Test that DELETE /repositories/{id} requires admin role."""
    repo = Repository(name="test", full_name="org/test")
    db_session.add(repo)
    await db_session.commit()

    response = await client.delete(f"/repositories/{repo.id}", headers=regular_auth_headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_settings_info_requires_admin(client: AsyncClient, regular_auth_headers: dict):
    """Test that GET /settings/info requires admin role."""
    response = await client.get("/settings/info", headers=regular_auth_headers)
    assert response.status_code == 403
