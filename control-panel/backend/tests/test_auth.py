import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post("/auth/login", json={
        "username": "admin",
        "password": "test-password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    response = await client.post("/auth/login", json={
        "username": "admin",
        "password": "wrong"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token(client, auth_token):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
