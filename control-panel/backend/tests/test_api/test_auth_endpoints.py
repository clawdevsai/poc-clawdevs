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
Test suite for Auth API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestLogin:
    """Test POST /auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, admin_user):
        """Test successful login."""
        request_body = {"username": "admin", "password": "test-password"}

        response = await client.post("/auth/login", json=request_body)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, admin_user):
        """Test login with wrong password."""
        request_body = {"username": "admin", "password": "wrong-password"}

        response = await client.post("/auth/login", json=request_body)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_unknown_user(self, client: AsyncClient):
        """Test login with unknown user."""
        request_body = {"username": "nobody", "password": "password"}

        response = await client.post("/auth/login", json=request_body)
        assert response.status_code == 401


class TestMe:
    """Test /auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_me_without_token(self, client: AsyncClient):
        """Test /auth/me without token returns 401."""
        response = await client.get("/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_valid_token(self, client: AsyncClient, admin_user):
        """Test /auth/me with valid token."""
        # First get a token
        login_response = await client.post(
            "/auth/login", json={"username": "admin", "password": "test-password"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "role" in data

    @pytest.mark.asyncio
    async def test_me_with_invalid_token(self, client: AsyncClient):
        """Test /auth/me with invalid token."""
        response = await client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401


class TestAuthEndpointsExist:
    """Test that auth endpoints exist."""

    @pytest.mark.asyncio
    async def test_login_endpoint_exists(self, client: AsyncClient):
        """Test /auth/login endpoint exists."""
        response = await client.post(
            "/auth/login", json={"username": "test", "password": "test"}
        )
        # May return 401 for failed login, but endpoint exists
        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_me_endpoint_exists(self, client: AsyncClient):
        """Test /auth/me endpoint exists."""
        response = await client.get("/auth/me")
        # Should return 401 without token, but endpoint exists
        assert response.status_code in [200, 401]
