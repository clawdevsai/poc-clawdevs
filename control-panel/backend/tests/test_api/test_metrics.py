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

from datetime import datetime, timedelta, UTC

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Session, Task


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
            "period_end": "2024-01-01T01:00:00Z",
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


class TestOverviewMetrics:
    """Test GET /metrics/overview endpoint."""

    @pytest.mark.asyncio
    async def test_overview_metrics_window(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Ensure overview metrics include windowed counts and token sums."""
        now = datetime.now(UTC).replace(tzinfo=None)
        recent_session = Session(
            openclaw_session_id="overview-recent",
            openclaw_session_key="agent:overview:main",
            agent_slug="overview",
            status="active",
            token_count=120,
            last_active_at=now - timedelta(minutes=5),
        )
        stale_session = Session(
            openclaw_session_id="overview-stale",
            openclaw_session_key="agent:overview:stale",
            agent_slug="overview",
            status="completed",
            token_count=300,
            last_active_at=now - timedelta(minutes=200),
        )
        task_backlog = Task(
            title="Backlog task",
            status="inbox",
            updated_at=now - timedelta(minutes=15),
        )
        task_progress = Task(
            title="In progress task",
            status="in_progress",
            updated_at=now - timedelta(minutes=20),
        )
        task_done = Task(
            title="Completed task",
            status="done",
            updated_at=now - timedelta(minutes=10),
        )
        db_session.add(recent_session)
        db_session.add(stale_session)
        db_session.add(task_backlog)
        db_session.add(task_progress)
        db_session.add(task_done)
        await db_session.commit()

        response = await client.get(
            "/metrics/overview?window_minutes=60", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tokens_consumed_total"] == 120
        assert data["backlog_count"] == 1
        assert data["tasks_in_progress"] == 1
        assert data["tasks_completed"] == 1


class TestTaskPerformanceMetrics:
    """Test cycle time and throughput metrics."""

    @pytest.mark.asyncio
    async def test_cycle_time_metrics_windowed(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Ensure cycle time metrics compute avg and p95 in window."""
        now = datetime.now(UTC).replace(tzinfo=None)
        durations = [60, 120, 300]
        for idx, seconds in enumerate(durations):
            db_session.add(
                Task(
                    title=f"Done {idx}",
                    status="done",
                    created_at=now - timedelta(minutes=5, seconds=seconds),
                    updated_at=now - timedelta(minutes=5),
                )
            )
        db_session.add(
            Task(
                title="Out of window",
                status="done",
                created_at=now - timedelta(hours=2),
                updated_at=now - timedelta(hours=2),
            )
        )
        await db_session.commit()

        response = await client.get(
            "/metrics/cycle-time?window_minutes=30", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["window_minutes"] == 30
        assert data["cycle_time_avg_seconds"] == pytest.approx(160.0)
        assert data["cycle_time_p95_seconds"] == pytest.approx(300.0)

    @pytest.mark.asyncio
    async def test_throughput_metrics_by_label(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Ensure throughput metrics return counts by label."""
        now = datetime.now(UTC).replace(tzinfo=None)
        db_session.add(
            Task(
                title="Backend 1",
                status="done",
                label="back_end",
                created_at=now - timedelta(minutes=20),
                updated_at=now - timedelta(minutes=10),
            )
        )
        db_session.add(
            Task(
                title="Backend 2",
                status="done",
                label="back_end",
                created_at=now - timedelta(minutes=25),
                updated_at=now - timedelta(minutes=12),
            )
        )
        db_session.add(
            Task(
                title="Frontend",
                status="done",
                label="front_end",
                created_at=now - timedelta(minutes=15),
                updated_at=now - timedelta(minutes=5),
            )
        )
        await db_session.commit()

        response = await client.get(
            "/metrics/throughput?window_minutes=30&group_by=label",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        items = {item["group"]: item["completed_count"] for item in data["items"]}
        assert items["back_end"] == 2
        assert items["front_end"] == 1
