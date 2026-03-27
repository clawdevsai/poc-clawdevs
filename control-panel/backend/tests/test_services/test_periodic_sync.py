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

"""Tests for periodic_sync tasks."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from app.tasks.periodic_sync import (
    run_sync_agents,
    run_sync_sessions,
    run_sync_tasks,
    schedule_periodic_tasks,
)


class TestRunSyncAgents:
    """Test run_sync_agents function."""

    @pytest.mark.asyncio
    async def test_run_sync_agents_success(self):
        """Test run_sync_agents calls sync_agents_runtime."""
        with patch("app.tasks.periodic_sync.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            with patch("app.tasks.periodic_sync.sync_agents_runtime") as mock_sync:
                mock_sync.return_value = None

                await run_sync_agents()

                mock_sync.assert_awaited_once_with(mock_session)

    @pytest.mark.asyncio
    async def test_run_sync_agents_handles_exception(self):
        """Test run_sync_agents logs and raises exceptions."""
        with patch("app.tasks.periodic_sync.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            with patch("app.tasks.periodic_sync.sync_agents_runtime") as mock_sync:
                mock_sync.side_effect = Exception("Sync failed")

                with pytest.raises(Exception, match="Sync failed"):
                    await run_sync_agents()


class TestRunSyncSessions:
    """Test run_sync_sessions function."""

    @pytest.mark.asyncio
    async def test_run_sync_sessions_success(self):
        """Test run_sync_sessions calls sync_sessions."""
        with patch("app.tasks.periodic_sync.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            with patch("app.tasks.periodic_sync.sync_sessions") as mock_sync:
                mock_sync.return_value = None

                await run_sync_sessions()

                mock_sync.assert_awaited_once_with(mock_session)


class TestRunSyncTasks:
    """Test run_sync_tasks function."""

    @pytest.mark.asyncio
    async def test_run_sync_tasks_success(self):
        """Test run_sync_tasks calls sync_tasks."""
        with patch("app.tasks.periodic_sync.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session_local.return_value.__aenter__.return_value = mock_session

            with patch("app.tasks.periodic_sync.sync_tasks") as mock_sync:
                mock_sync.return_value = None

                await run_sync_tasks()

                mock_sync.assert_awaited_once_with(mock_session)


class TestSchedulePeriodicTasks:
    """Test schedule_periodic_tasks function."""

    def test_schedule_creates_three_jobs(self):
        """Test that schedule_periodic_tasks schedules three sync jobs."""
        with patch("app.tasks.periodic_sync.Redis") as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis

            mock_scheduler = MagicMock()
            mock_scheduler.get_jobs.return_value = []

            with patch(
                "app.tasks.periodic_sync.Scheduler", return_value=mock_scheduler
            ):
                with patch("app.tasks.periodic_sync.logger"):
                    schedule_periodic_tasks()

            # Should call schedule three times
            assert mock_scheduler.schedule.call_count == 3

    def test_schedule_cancels_existing_jobs(self):
        """Test that existing jobs are cancelled before scheduling new ones."""
        with patch("app.tasks.periodic_sync.Redis") as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis

            mock_scheduler = MagicMock()
            # Create mock jobs
            mock_job1 = MagicMock()
            mock_job1.func_name = "app.tasks.periodic_sync.run_sync_agents"
            mock_job2 = MagicMock()
            mock_job2.func_name = "app.tasks.periodic_sync.run_sync_sessions"
            mock_job3 = MagicMock()
            mock_job3.func_name = "app.tasks.periodic_sync.run_sync_tasks"
            mock_job4 = MagicMock()
            mock_job4.func_name = "other.function"
            mock_scheduler.get_jobs.return_value = [
                mock_job1,
                mock_job2,
                mock_job3,
                mock_job4,
            ]

            with patch(
                "app.tasks.periodic_sync.Scheduler", return_value=mock_scheduler
            ):
                with patch("app.tasks.periodic_sync.logger"):
                    schedule_periodic_tasks()

            # Should cancel only the three sync jobs
            assert mock_scheduler.cancel.call_count == 3
            cancel_calls = [c[0][0] for c in mock_scheduler.cancel.call_args_list]
            assert mock_job1 in cancel_calls
            assert mock_job2 in cancel_calls
            assert mock_job3 in cancel_calls
            assert mock_job4 not in cancel_calls

    def test_schedule_intervals_correct(self):
        """Test that jobs are scheduled with correct intervals."""
        with patch("app.tasks.periodic_sync.Redis") as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis

            mock_scheduler = MagicMock()
            mock_scheduler.get_jobs.return_value = []

            with patch(
                "app.tasks.periodic_sync.Scheduler", return_value=mock_scheduler
            ):
                with patch("app.tasks.periodic_sync.logger"):
                    schedule_periodic_tasks()

            # Check schedule calls
            schedule_calls = mock_scheduler.schedule.call_args_list

            # First call should be run_sync_agents with interval=60
            assert "run_sync_agents" in str(schedule_calls[0])
            call_kwargs = schedule_calls[0][1]
            assert call_kwargs["interval"] == 60

            # Second call should be run_sync_sessions with interval=60
            assert "run_sync_sessions" in str(schedule_calls[1])
            call_kwargs = schedule_calls[1][1]
            assert call_kwargs["interval"] == 60

            # Third call should be run_sync_tasks with interval=300
            assert "run_sync_tasks" in str(schedule_calls[2])
            call_kwargs = schedule_calls[2][1]
            assert call_kwargs["interval"] == 300

    def test_schedule_time_offsets(self):
        """Test that jobs are scheduled with appropriate time offsets."""
        with patch("app.tasks.periodic_sync.Redis") as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis

            mock_scheduler = MagicMock()
            mock_scheduler.get_jobs.return_value = []

            with patch("app.tasks.periodic_sync.datetime") as mock_datetime:
                # Mock current time
                mock_now = datetime(2024, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now

                with patch(
                    "app.tasks.periodic_sync.Scheduler", return_value=mock_scheduler
                ):
                    with patch("app.tasks.periodic_sync.logger"):
                        schedule_periodic_tasks()

                # Verify scheduled_time for each job
                schedule_calls = mock_scheduler.schedule.call_args_list

                # First job: now + 10 seconds
                assert schedule_calls[0][1]["scheduled_time"] == mock_now + timedelta(
                    seconds=10
                )

                # Second job: now + 30 seconds
                assert schedule_calls[1][1]["scheduled_time"] == mock_now + timedelta(
                    seconds=30
                )

                # Third job: now + 50 seconds
                assert schedule_calls[2][1]["scheduled_time"] == mock_now + timedelta(
                    seconds=50
                )

    def test_schedule_return_scheduler(self):
        """Test that schedule_periodic_tasks returns the scheduler."""
        with patch("app.tasks.periodic_sync.Redis") as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis

            mock_scheduler = MagicMock()
            mock_scheduler.get_jobs.return_value = []

            with patch(
                "app.tasks.periodic_sync.Scheduler", return_value=mock_scheduler
            ):
                with patch("app.tasks.periodic_sync.logger"):
                    result = schedule_periodic_tasks()

            assert result is mock_scheduler
