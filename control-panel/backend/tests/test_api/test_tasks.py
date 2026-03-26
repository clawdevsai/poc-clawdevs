"""
Test suite for Tasks API endpoints.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from uuid import uuid4


class TestListTasks:
    """Test GET /api/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, client: AsyncClient):
        """Test listing tasks when no tasks exist."""
        with patch('app.api.tasks.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.all.return_value = []
            mock_select.return_value.order_by.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.get("/api/tasks")
            assert response.status_code == 200
            data = response.json()
            assert data["items"] == []
            assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_tasks_with_tasks(self, client: AsyncClient):
        """Test listing tasks when tasks exist."""
        task_id = str(uuid4())
        
        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.title = "Test Task"
        mock_task.description = "Test description"
        mock_task.status = "inbox"
        mock_task.priority = "medium"
        mock_task.label = "back_end"
        mock_task.assigned_agent_id = None
        mock_task.github_issue_number = None
        mock_task.github_issue_url = None
        mock_task.github_repo = None
        mock_task.due_at = None
        mock_task.created_at = datetime.utcnow()
        mock_task.updated_at = datetime.utcnow()
        
        with patch('app.api.tasks.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.all.return_value = [mock_task]
            mock_select.return_value.order_by.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.get("/api/tasks")
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["title"] == "Test Task"
            assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_tasks_with_status_filter(self, client: AsyncClient):
        """Test listing tasks filtered by status."""
        with patch('app.api.tasks.select') as mock_select:
            mock_query = MagicMock()
            mock_query.where.return_value = mock_query
            mock_result = AsyncMock()
            mock_result.all.return_value = []
            mock_query.exec = AsyncMock(return_value=mock_result)
            mock_select.return_value.order_by.return_value = mock_query
            
            response = await client.get("/api/tasks?status=inbox")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_tasks_with_label_filter(self, client: AsyncClient):
        """Test listing tasks filtered by label."""
        with patch('app.api.tasks.select') as mock_select:
            mock_query = MagicMock()
            mock_query.where.return_value = mock_query
            mock_result = AsyncMock()
            mock_result.all.return_value = []
            mock_query.exec = AsyncMock(return_value=mock_result)
            mock_select.return_value.order_by.return_value = mock_query
            
            response = await client.get("/api/tasks?label=back_end")
            assert response.status_code == 200


class TestCreateTask:
    """Test POST /api/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, client: AsyncClient):
        """Test creating a task successfully."""
        request_body = {
            "title": "New Task",
            "description": "Task description",
            "priority": "high",
            "label": "back_end"
        }
        
        with patch('app.api.tasks.Task') as mock_task:
            mock_task_instance = MagicMock()
            mock_task.return_value = mock_task_instance
            
            with patch('app.api.tasks.uuid4') as mock_uuid:
                mock_uuid.return_value = uuid4()
                
                with patch('app.api.tasks.select') as mock_select:
                    mock_result = AsyncMock()
                    mock_result.all.return_value = []
                    mock_select.return_value.order_by.return_value.exec = AsyncMock(return_value=mock_result)
                    
                    response = await client.post("/api/tasks", json=request_body)
                    assert response.status_code == 201
                    data = response.json()
                    assert data["title"] == "New Task"

    @pytest.mark.asyncio
    async def test_create_task_with_agent(self, client: AsyncClient):
        """Test creating a task with assigned agent."""
        agent_id = str(uuid4())
        request_body = {
            "title": "Task with Agent",
            "assigned_agent_id": agent_id
        }
        
        with patch('app.api.tasks.Task') as mock_task:
            mock_task_instance = MagicMock()
            mock_task.return_value = mock_task_instance
            
            with patch('app.api.tasks.select') as mock_select:
                mock_result = AsyncMock()
                mock_result.all.return_value = []
                mock_select.return_value.order_by.return_value.exec = AsyncMock(return_value=mock_result)
                
                response = await client.post("/api/tasks", json=request_body)
                assert response.status_code == 201


class TestGetTask:
    """Test GET /api/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client: AsyncClient):
        """Test getting a non-existent task returns 404."""
        task_id = str(uuid4())
        
        response = await client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_task_success(self, client: AsyncClient):
        """Test getting an existing task."""
        task_id = str(uuid4())
        
        mock_task = MagicMock()
        mock_task.id = uuid4()
        mock_task.title = "Test Task"
        mock_task.description = "Test description"
        mock_task.status = "inbox"
        mock_task.priority = "medium"
        mock_task.created_at = datetime.utcnow()
        mock_task.updated_at = datetime.utcnow()
        
        with patch('app.api.tasks.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.first.return_value = mock_task
            mock_select.return_value.where.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Test Task"


class TestUpdateTask:
    """Test PATCH /api/tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_task_status(self, client: AsyncClient):
        """Test updating task status."""
        task_id = str(uuid4())
        
        with patch('app.api.tasks.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.first.return_value = None
            mock_select.return_value.where.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.patch(f"/api/tasks/{task_id}", json={"status": "in_progress"})
            assert response.status_code == 404  # Task not found

    @pytest.mark.asyncio
    async def test_update_task_priority(self, client: AsyncClient):
        """Test updating task priority."""
        task_id = str(uuid4())
        
        with patch('app.api.tasks.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.first.return_value = None
            mock_select.return_value.where.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.patch(f"/api/tasks/{task_id}", json={"priority": "high"})
            assert response.status_code == 404  # Task not found


class TestTasksResponseModels:
    """Test Tasks response model structure."""

    def test_task_response_structure(self):
        """Test TaskResponse model structure."""
        from app.api.tasks import TaskResponse
        
        task = TaskResponse(
            id=str(uuid4()),
            title="Test Task",
            status="inbox",
            priority="medium",
        )
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status == "inbox"

    def test_tasks_list_response_structure(self):
        """Test TasksListResponse model structure."""
        from app.api.tasks import TasksListResponse
        
        response = TasksListResponse(
            items=[],
            total=0
        )
        
        assert response.items == []
        assert response.total == 0
