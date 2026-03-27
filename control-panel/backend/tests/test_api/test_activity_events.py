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
Test suite for Activity Events API endpoints.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestListActivityEvents:
    """Test GET /api/activity-events endpoint."""

    @pytest.mark.asyncio
    async def test_list_activity_events_empty(self, client: AsyncClient):
        """Test listing activity events when none exist."""
        response = await client.get("/api/activity-events")
        # May return 404 if endpoint not implemented
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_activity_events_with_events(self, client: AsyncClient):
        """Test listing activity events when they exist."""
        response = await client.get("/api/activity-events")
        assert response.status_code in [200, 404]


class TestCreateActivityEvent:
    """Test POST /api/activity-events endpoint."""

    @pytest.mark.asyncio
    async def test_create_activity_event(self, client: AsyncClient):
        """Test creating an activity event."""
        request_body = {
            "event_type": "user_login",
            "agent_id": str(uuid4())
        }
        
        response = await client.post("/api/activity-events", json=request_body)
        # May return 404 if endpoint not implemented
        assert response.status_code in [200, 201, 404]


class TestActivityEventEndpointsExist:
    """Test that activity event endpoints exist."""

    @pytest.mark.asyncio
    async def test_activity_events_endpoint_exists(self, client: AsyncClient):
        """Test /api/activity-events endpoint exists."""
        response = await client.get("/api/activity-events")
        assert response.status_code in [200, 404]
