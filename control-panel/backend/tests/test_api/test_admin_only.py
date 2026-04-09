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
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import User
from app.core.auth import get_password_hash

@pytest_asyncio.fixture(scope="function")
async def regular_user(db_session: AsyncSession) -> User:
    user = User(
        username="user",
        password_hash=get_password_hash("test-password"),
        role="user",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def user_auth_headers(client: AsyncClient, regular_user: User) -> dict:
    response = await client.post(
        "/auth/login",
        json={"username": "user", "password": "test-password"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_cluster_info_admin_only(client: AsyncClient, user_auth_headers: dict):
    response = await client.get("/cluster/info", headers=user_auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@pytest.mark.asyncio
async def test_settings_info_admin_only(client: AsyncClient, user_auth_headers: dict):
    response = await client.get("/settings/info", headers=user_auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@pytest.mark.asyncio
async def test_sync_agents_admin_only(client: AsyncClient, user_auth_headers: dict):
    response = await client.post("/agents/admin/sync", headers=user_auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@pytest.mark.asyncio
async def test_create_repository_admin_only(client: AsyncClient, user_auth_headers: dict):
    response = await client.post(
        "/repositories",
        json={"name": "test", "full_name": "org/test"},
        headers=user_auth_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@pytest.mark.asyncio
async def test_trigger_cron_admin_only(client: AsyncClient, user_auth_headers: dict):
    response = await client.post("/crons/test-agent/trigger", headers=user_auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"
