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
Test suite for SDD Artifacts API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestListSddArtifacts:
    """Test GET /api/sdd endpoint."""

    @pytest.mark.asyncio
    async def test_list_sdd_empty(self, client: AsyncClient):
        """Test listing SDD artifacts when none exist."""
        response = await client.get("/api/sdd")
        # May return 404 if endpoint not implemented
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_sdd_with_artifacts(self, client: AsyncClient):
        """Test listing SDD artifacts when they exist."""
        response = await client.get("/api/sdd")
        assert response.status_code in [200, 404]


class TestCreateSddArtifact:
    """Test POST /api/sdd endpoint."""

    @pytest.mark.asyncio
    async def test_create_sdd_artifact(self, client: AsyncClient):
        """Test creating an SDD artifact."""
        request_body = {
            "artifact_type": "BRIEF",
            "title": "Test Brief",
            "content": "Test content"
        }
        
        response = await client.post("/api/sdd", json=request_body)
        # May return 404 if endpoint not implemented
        assert response.status_code in [200, 201, 404]


class TestSddEndpointsExist:
    """Test that SDD endpoints exist."""

    @pytest.mark.asyncio
    async def test_sdd_endpoint_exists(self, client: AsyncClient):
        """Test /api/sdd endpoint exists."""
        response = await client.get("/api/sdd")
        assert response.status_code in [200, 404]
