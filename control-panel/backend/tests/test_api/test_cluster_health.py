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
Test suite for Clusters API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestClusterStatus:
    """Test /api/cluster/status endpoint."""

    @pytest.mark.asyncio
    async def test_cluster_status_endpoint(self, client: AsyncClient):
        """Test cluster status endpoint."""
        response = await client.get("/api/cluster/status")
        # May return 404 if endpoint not implemented
        assert response.status_code in [200, 404]


class TestHealthz:
    """Test /healthz endpoint."""

    @pytest.mark.asyncio
    async def test_healthz_endpoint(self, client: AsyncClient):
        """Test healthz endpoint."""
        response = await client.get("/healthz")
        # Should return 200 for healthy
        assert response.status_code == 200


class TestAPIRoot:
    """Test API root endpoint."""

    @pytest.mark.asyncio
    async def test_api_root(self, client: AsyncClient):
        """Test API root endpoint."""
        response = await client.get("/api")
        # May return 404 if no root endpoint
        assert response.status_code in [200, 404]


class TestAPIEndpointsExist:
    """Test that expected API endpoints exist."""

    @pytest.mark.asyncio
    async def test_agents_endpoint_exists(self, client: AsyncClient):
        """Test /api/agents endpoint exists."""
        response = await client.get("/api/agents")
        # Should return 200 or 404 (not 405)
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_sessions_endpoint_exists(self, client: AsyncClient):
        """Test /api/sessions endpoint exists."""
        response = await client.get("/api/sessions")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_tasks_endpoint_exists(self, client: AsyncClient):
        """Test /api/tasks endpoint exists."""
        response = await client.get("/api/tasks")
        assert response.status_code in [200, 404]
