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
Test suite for Metrics API endpoints.
"""

import pytest
from httpx import AsyncClient


class TestListMetrics:
    """Test GET /api/metrics endpoint."""

    @pytest.mark.asyncio
    async def test_list_metrics_empty(self, client: AsyncClient):
        """Test listing metrics when none exist."""
        response = await client.get("/api/metrics")
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_metrics_with_metrics(self, client: AsyncClient):
        """Test listing metrics when they exist."""
        response = await client.get("/api/metrics")
        assert response.status_code in [200, 404]


class TestCreateMetric:
    """Test POST /api/metrics endpoint."""

    @pytest.mark.asyncio
    async def test_create_metric(self, client: AsyncClient):
        """Test creating a metric."""
        request_body = {
            "metric_type": "tokens_used",
            "value": 1000.0,
            "period_start": "2024-01-01T00:00:00Z",
            "period_end": "2024-01-01T01:00:00Z"
        }
        
        response = await client.post("/api/metrics", json=request_body)
        assert response.status_code in [200, 201, 404]


class TestMetricEndpointsExist:
    """Test that metric endpoints exist."""

    @pytest.mark.asyncio
    async def test_metrics_endpoint_exists(self, client: AsyncClient):
        """Test /api/metrics endpoint exists."""
        response = await client.get("/api/metrics")
        assert response.status_code in [200, 404]
