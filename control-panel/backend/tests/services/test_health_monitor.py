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
import asyncio
from app.core.config import get_settings


def test_health_monitor_config_exists():
    """Verify health monitor config variables exist"""
    settings = get_settings()
    assert hasattr(settings, 'HEALTH_MONITOR_ENABLED')
    assert hasattr(settings, 'HEALTH_MONITOR_INTERVAL_SECONDS')
    assert settings.HEALTH_MONITOR_INTERVAL_SECONDS == 300


@pytest.mark.asyncio
async def test_health_monitor_loop_initialization():
    """Verify health monitor initializes without errors"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop(interval_seconds=5)
    assert monitor.interval_seconds == 5
    assert monitor.enabled is False  # Starts disabled until started


@pytest.mark.asyncio
async def test_health_monitor_start_stop():
    """Verify health monitor can be started and stopped"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop(interval_seconds=1)

    # Should start disabled
    assert monitor.enabled is False

    # Start it
    await monitor.start()
    assert monitor.enabled is True

    # Stop it
    await monitor.stop()
    assert monitor.enabled is False


@pytest.mark.asyncio
async def test_gather_db_metrics(test_engine):
    """Verify database metrics are gathered correctly"""
    from app.services.health_monitor import HealthMonitorLoop

    monitor = HealthMonitorLoop()
    metrics = await monitor._gather_db_metrics(engine=test_engine)

    # Verify structure
    assert "connection_pool" in metrics
    assert "max_connections" in metrics["connection_pool"]
    assert "active_connections" in metrics["connection_pool"]
    assert "percentage" in metrics["connection_pool"]

    # Verify reasonable values
    assert 0 <= metrics["connection_pool"]["percentage"] <= 100


@pytest.mark.asyncio
async def test_gather_agent_metrics(db_session):
    """Verify agent metrics are gathered correctly"""
    from app.services.health_monitor import HealthMonitorLoop
    from app.models import Agent
    from datetime import datetime, timezone, timedelta
    from uuid import uuid4

    # Create test agents
    now = datetime.now(timezone.utc)

    agent1 = Agent(
        id=uuid4(),
        slug="dev_backend",
        display_name="Backend Developer",
        role="developer",
        status="active",
        runtime_status="working",
        openclaw_session_id="session-uuid-1",
        last_heartbeat_at=now - timedelta(minutes=5),
    )

    agent2 = Agent(
        id=uuid4(),
        slug="qa_tester",
        display_name="QA Tester",
        role="tester",
        status="active",
        runtime_status="idle",
        openclaw_session_id="session-uuid-2",
        last_heartbeat_at=now - timedelta(minutes=2),
    )

    # Add agents to test session
    db_session.add(agent1)
    db_session.add(agent2)
    await db_session.commit()

    # Gather metrics
    monitor = HealthMonitorLoop()
    metrics = await monitor._gather_agent_metrics(session=db_session)

    # Verify structure
    assert "agents" in metrics
    assert "total" in metrics
    assert "timestamp" in metrics

    # Verify agents list
    assert isinstance(metrics["agents"], list)
    assert len(metrics["agents"]) == 2
    assert metrics["total"] == 2

    # Verify agent structure
    for agent_metric in metrics["agents"]:
        assert "slug" in agent_metric
        assert "display_name" in agent_metric
        assert "status" in agent_metric
        assert "runtime_status" in agent_metric
        assert "last_heartbeat_at" in agent_metric
        assert "heartbeat_age_minutes" in agent_metric
        assert "openclaw_session_id" in agent_metric

    # Verify specific values
    agent1_metric = next(a for a in metrics["agents"] if a["slug"] == "dev_backend")
    assert agent1_metric["display_name"] == "Backend Developer"
    assert agent1_metric["status"] == "active"
    assert agent1_metric["runtime_status"] == "working"
    assert agent1_metric["openclaw_session_id"] == "session-uuid-1"
    assert agent1_metric["heartbeat_age_minutes"] >= 4  # Allow some timing variance

    # Verify timestamp is ISO format
    assert isinstance(metrics["timestamp"], str)
    assert "T" in metrics["timestamp"]  # ISO format check
