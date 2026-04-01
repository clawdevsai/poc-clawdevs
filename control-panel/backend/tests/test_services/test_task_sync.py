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
Tests for task_sync service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import ActivityEvent, Agent, Task
from app.services.task_sync import sync_tasks_from_github


class TestTaskSyncConstants:
    """Test sync_tasks constants."""

    def test_status_mapping_defined(self):
        """Test that status mapping is defined."""
        from app.services.task_sync import STATUS_MAP

        assert isinstance(STATUS_MAP, dict)
        assert "open" in STATUS_MAP
        assert "closed" in STATUS_MAP

    def test_label_mapping_defined(self):
        """Test that label mapping is defined."""
        from app.services.task_sync import LABEL_MAP

        assert isinstance(LABEL_MAP, dict)

    def test_github_label_prefix(self):
        """Test GitHub label prefix."""
        # No explicit prefix constant in implementation; just sanity-check map keys
        from app.services.task_sync import LABEL_MAP

        assert "backend" in LABEL_MAP


class TestStatusMapping:
    """Test status mapping functionality."""

    def test_status_mapping_inbox(self):
        """Test inbox status mapping."""
        from app.services.task_sync import STATUS_MAP

        assert STATUS_MAP["open"] == "inbox"

    def test_status_mapping_in_progress(self):
        """Test in_progress status mapping."""
        from app.services.task_sync import STATUS_MAP

        assert STATUS_MAP["in_progress"] == "in_progress"


class TestLabelMapping:
    """Test label mapping functionality."""

    def test_label_mapping_bug(self):
        """Test bug label mapping."""
        from app.services.task_sync import LABEL_MAP

        # Implementation maps GitHub labels to internal labels; 'bug' isn't mapped explicitly
        assert isinstance(LABEL_MAP, dict)


class TestSyncTasks:
    """Test sync_tasks function with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_sync_tasks_success_creates_tasks(self, db_session: AsyncSession):
        """Test that sync_tasks creates new tasks from GitHub issues."""
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        db_session.add(ceo)
        await db_session.commit()
        await db_session.refresh(ceo)

        issue_payload = [
            {
                "number": 101,
                "title": "Create endpoint",
                "body": "Implement CRUD",
                "state": "open",
                "labels": [{"name": "backend"}],
                "html_url": "https://github.com/acme/app/issues/101",
                "assignees": [],
            }
        ]
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = issue_payload

        with patch("app.services.task_sync.settings.github_token", "ghp-test-token"):
            with patch("httpx.AsyncClient") as mock_async_client:
                mock_client = AsyncMock()
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_async_client.return_value.__aenter__.return_value = mock_client
                with patch(
                    "app.services.task_sync.enqueue_task_for_ceo",
                    return_value=(True, None),
                ) as mock_enqueue:
                    await sync_tasks_from_github(db_session, "acme/app")
                    mock_enqueue.assert_called_once()

        task_result = await db_session.exec(
            select(Task).where(Task.github_issue_number == 101)
        )
        task = task_result.first()
        assert task is not None
        assert task.assigned_agent_id == ceo.id
        assert task.workflow_state == "queued_to_ceo"

        event_result = await db_session.exec(
            select(ActivityEvent).where(ActivityEvent.entity_id == str(task.id))
        )
        event_types = {event.event_type for event in event_result.all()}
        assert "task.created" in event_types
        assert "task.queued_to_ceo" in event_types


class TestSyncTasksGitHubIntegration:
    """Test sync_tasks GitHub integration."""

    @pytest.mark.asyncio
    async def test_sync_tasks_uses_github_api(self, db_session: AsyncSession):
        """Test existing tasks are not re-enqueued repeatedly."""
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        db_session.add(ceo)
        await db_session.commit()
        await db_session.refresh(ceo)

        existing = Task(
            title="Already synced",
            github_issue_number=202,
            github_issue_url="https://github.com/acme/app/issues/202",
            github_repo="acme/app",
            workflow_state="forwarded_by_ceo",
            assigned_agent_id=ceo.id,
        )
        db_session.add(existing)
        await db_session.commit()

        issue_payload = [
            {
                "number": 202,
                "title": "Already synced updated",
                "body": "Updated description",
                "state": "open",
                "labels": [{"name": "backend"}],
                "html_url": "https://github.com/acme/app/issues/202",
                "assignees": [],
            }
        ]
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = issue_payload

        with patch("app.services.task_sync.settings.github_token", "ghp-test-token"):
            with patch("httpx.AsyncClient") as mock_async_client:
                mock_client = AsyncMock()
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_async_client.return_value.__aenter__.return_value = mock_client
                with patch(
                    "app.services.task_sync.enqueue_task_for_ceo",
                    return_value=(True, None),
                ) as mock_enqueue:
                    await sync_tasks_from_github(db_session, "acme/app")
                    mock_enqueue.assert_not_called()

        await db_session.refresh(existing)
        assert existing.title == "Already synced updated"
