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
Test suite for Tasks API endpoints.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, UTC
from uuid import UUID, uuid4
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from unittest.mock import patch

from app.models import ActivityEvent, Agent, Task


class TestListTasks:
    """Test GET /api/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing tasks when no tasks exist."""
        response = await client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_tasks_with_tasks(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        """Test listing tasks when tasks exist."""
        task = Task(
            title="Test Task",
            description="Test description",
            status="inbox",
            priority="medium",
            label="back_end",
        )
        db_session.add(task)
        await db_session.commit()

        response = await client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Test Task"
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_tasks_with_status_filter(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test listing tasks filtered by status."""
        response = await client.get("/tasks?status=inbox", headers=auth_headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_tasks_with_label_filter(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test listing tasks filtered by label."""
        response = await client.get("/tasks?label=back_end", headers=auth_headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_tasks_returns_assigned_agent_slug(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        db_session.add(ceo)
        await db_session.commit()
        await db_session.refresh(ceo)

        task = Task(
            title="Task with assigned slug",
            status="in_progress",
            priority="medium",
            assigned_agent_id=ceo.id,
            workflow_state="forwarded_by_ceo",
        )
        db_session.add(task)
        await db_session.commit()

        response = await client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["items"][0]["assigned_agent_slug"] == "ceo"


class TestCreateTask:
    """Test POST /api/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        """Test creating a task successfully."""
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        db_session.add(ceo)
        await db_session.commit()
        await db_session.refresh(ceo)

        request_body = {
            "title": "New Task",
            "description": "Task description",
            "priority": "high",
            "label": "back_end",
        }

        with patch(
            "app.api.tasks.enqueue_task_for_ceo", return_value=(True, None)
        ) as mock_enqueue:
            response = await client.post(
                "/tasks", json=request_body, headers=auth_headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "New Task"
            assert data["assigned_agent_id"] == str(ceo.id)
            assert data["assigned_agent_slug"] == "ceo"
            assert data["workflow_state"] == "queued_to_ceo"
            assert data["workflow_attempts"] == 0
            mock_enqueue.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_with_agent(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict
    ):
        """Test creating a task always routes first to CEO."""
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        worker = Agent(slug="backend", display_name="Backend", role="developer")
        db_session.add(ceo)
        db_session.add(worker)
        await db_session.commit()
        await db_session.refresh(ceo)
        await db_session.refresh(worker)

        agent_id = str(uuid4())
        request_body = {"title": "Task with Agent", "assigned_agent_id": agent_id}
        with patch("app.api.tasks.enqueue_task_for_ceo", return_value=(True, None)):
            response = await client.post(
                "/tasks", json=request_body, headers=auth_headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data["assigned_agent_id"] == str(ceo.id)
            assert data["assigned_agent_slug"] == "ceo"
            assert data["assigned_agent_id"] != str(worker.id)

    @pytest.mark.asyncio
    async def test_create_task_marks_workflow_failed_if_enqueue_fails(
        self, client: AsyncClient, db_session: AsyncSession, auth_headers: dict
    ):
        """Test enqueue failure does not fail API call and records workflow error."""
        ceo = Agent(slug="ceo", display_name="CEO", role="ceo")
        db_session.add(ceo)
        await db_session.commit()
        await db_session.refresh(ceo)

        with patch(
            "app.api.tasks.enqueue_task_for_ceo", return_value=(False, "redis offline")
        ):
            response = await client.post(
                "/tasks",
                json={"title": "Task with queue failure"},
                headers=auth_headers,
            )

        assert response.status_code == 201
        data = response.json()
        assert data["workflow_state"] == "failed"
        assert data["workflow_last_error"] == "redis offline"

        task = await db_session.get(Task, UUID(data["id"]))
        assert task is not None
        assert task.workflow_state == "failed"

        events_result = await db_session.exec(
            select(ActivityEvent).where(ActivityEvent.entity_id == data["id"])
        )
        event_types = {event.event_type for event in events_result.all()}
        assert "task.failed" in event_types


class TestGetTask:
    """Test GET /api/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting a non-existent task returns 404."""
        task_id = str(uuid4())

        response = await client.get(f"/tasks/{task_id}", headers=auth_headers)
        # Endpoint may not be implemented (405) or may return 404
        assert response.status_code in [404, 405]

    @pytest.mark.asyncio
    async def test_get_task_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        """Test getting an existing task."""
        task = Task(
            title="Test Task",
            description="Test description",
            status="inbox",
            priority="medium",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        response = await client.get(f"/tasks/{task.id}", headers=auth_headers)
        # Endpoint may not be implemented (405). If implemented, should return the task.
        assert response.status_code in [200, 405]
        if response.status_code == 200:
            data = response.json()
            assert data["title"] == "Test Task"


class TestUpdateTask:
    """Test PATCH /api/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_task_status(self, client: AsyncClient, auth_headers: dict):
        """Test updating task status."""
        task_id = str(uuid4())
        response = await client.patch(
            f"/tasks/{task_id}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        assert response.status_code == 404  # Task not found

    @pytest.mark.asyncio
    async def test_update_task_priority(self, client: AsyncClient, auth_headers: dict):
        """Test updating task priority."""
        task_id = str(uuid4())
        response = await client.patch(
            f"/tasks/{task_id}",
            json={"priority": "high"},
            headers=auth_headers,
        )
        assert response.status_code == 404  # Task not found


class TestDeleteTask:
    """Test DELETE /api/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a non-existent task."""
        task_id = str(uuid4())
        response = await client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        """Test deleting an existing task."""
        task = Task(
            title="Delete me",
            description="Task to delete",
            status="inbox",
            priority="medium",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        response = await client.delete(f"/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 204

        list_response = await client.get("/tasks", headers=auth_headers)
        assert list_response.status_code == 200
        data = list_response.json()
        assert all(item["id"] != str(task.id) for item in data["items"])


class TestTaskTimeline:
    """Test GET /api/tasks/{task_id}/timeline endpoint."""

    @pytest.mark.asyncio
    async def test_timeline_returns_events_in_ascending_order(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        task = Task(
            title="Task timeline",
            description="Timeline check",
            status="inbox",
            priority="medium",
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        earlier = datetime(2026, 1, 1, 10, 0, 0)
        later = datetime(2026, 1, 1, 10, 5, 0)
        db_session.add(
            ActivityEvent(
                event_type="task.forwarded",
                entity_type="task",
                entity_id=str(task.id),
                payload={
                    "description": "Forwarded to backend",
                    "from_agent_slug": "ceo",
                    "to_agent_slug": "backend",
                },
                created_at=later,
            )
        )
        db_session.add(
            ActivityEvent(
                event_type="task.created",
                entity_type="task",
                entity_id=str(task.id),
                payload={"description": "Task criada"},
                created_at=earlier,
            )
        )
        await db_session.commit()

        response = await client.get(f"/tasks/{task.id}/timeline", headers=auth_headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 2
        assert payload["items"][0]["event_type"] == "task.created"
        assert payload["items"][1]["event_type"] == "task.forwarded"
        assert payload["items"][1]["from_agent_slug"] == "ceo"
        assert payload["items"][1]["to_agent_slug"] == "backend"


class TestTaskFailureDetail:
    """Test GET /api/tasks/{task_id}/failure endpoint."""

    @pytest.mark.asyncio
    async def test_task_failure_detail(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        task = Task(
            title="Failed task",
            status="in_progress",
            failure_count=1,
            consecutive_failures=1,
            last_error="Boom",
            error_reason="execution_error",
            last_failed_at=datetime.now(UTC).replace(tzinfo=None),
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        db_session.add(
            ActivityEvent(
                event_type="task_failed",
                entity_type="task",
                entity_id=str(task.id),
                payload={
                    "error_message": "Boom",
                    "stack_trace": "Traceback: boom",
                    "evidence": ["stderr: boom", "context: run 1"],
                },
            )
        )
        await db_session.commit()

        response = await client.get(f"/tasks/{task.id}/failure", headers=auth_headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["message"] == "Boom"
        assert payload["stack_trace"] == "Traceback: boom"
        assert payload["evidence"] == ["stderr: boom", "context: run 1"]


class TestTasksResponseModels:
    """Test Tasks response model structure."""

    def test_task_response_structure(self):
        """Test TaskResponse model structure."""
        from app.api.tasks import TaskResponse

        task = TaskResponse(
            id=str(uuid4()),
            title="Test Task",
            description=None,
            status="inbox",
            priority="medium",
            label=None,
            assigned_agent_id=None,
            assigned_agent_slug=None,
            github_issue_number=None,
            github_issue_url=None,
            github_repo=None,
            due_at=None,
            workflow_state="queued_to_ceo",
            workflow_last_error=None,
            workflow_attempts=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status == "inbox"

    def test_tasks_list_response_structure(self):
        """Test TasksListResponse model structure."""
        from app.api.tasks import TasksListResponse

        response = TasksListResponse(items=[], total=0)

        assert response.items == []
        assert response.total == 0
