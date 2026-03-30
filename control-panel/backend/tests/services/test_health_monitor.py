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
