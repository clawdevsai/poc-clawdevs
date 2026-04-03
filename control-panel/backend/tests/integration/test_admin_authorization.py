import pytest
from httpx import AsyncClient
from app.core.auth import get_password_hash
from app.models import User, Agent
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

@pytest.mark.asyncio
async def test_admin_endpoints_protected(client: AsyncClient, db_session: AsyncSession):
    # Create a non-admin user
    user = User(
        username="user",
        password_hash=get_password_hash("password"),
        role="user",
    )
    db_session.add(user)

    await db_session.commit()
    await db_session.refresh(user)

    # Login as non-admin
    response = await client.post(
        "/auth/login",
        json={"username": "user", "password": "password"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test administrative endpoints (Expected to fail with 403)

    # 1. Cluster endpoints
    for path in ["/cluster/pods", "/cluster/info", "/cluster/events", "/cluster/pvcs"]:
        response = await client.get(path, headers=headers)
        assert response.status_code == 403, f"Endpoint {path} should be protected"

    # 2. Repository write endpoints
    response = await client.post("/repositories", headers=headers, json={
        "name": "test", "full_name": "org/test"
    })
    assert response.status_code == 403

    response = await client.patch("/repositories/00000000-0000-0000-0000-000000000000", headers=headers, json={"name": "updated"})
    assert response.status_code == 403

    response = await client.delete("/repositories/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 403

    # 3. Agent sync (Admin)
    response = await client.post("/agents/admin/sync", headers=headers)
    assert response.status_code == 403

    # 4. Settings info
    response = await client.get("/settings/info", headers=headers)
    assert response.status_code == 403

    # 5. Cron trigger
    response = await client.post("/crons/ceo/trigger", headers=headers)
    assert response.status_code == 403
