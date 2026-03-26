"""
Test suite for Repositories API endpoints.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from uuid import uuid4


class TestListRepositories:
    """Test GET /api/repositories endpoint."""

    @pytest.mark.asyncio
    async def test_list_repositories_empty(self, client: AsyncClient):
        """Test listing repositories when none exist."""
        with patch('app.api.repositories.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.all.return_value = []
            mock_select.return_value.order_by.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.get("/api/repositories")
            assert response.status_code == 200
            data = response.json()
            assert data["items"] == []
            assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_repositories_with_repos(self, client: AsyncClient):
        """Test listing repositories when they exist."""
        mock_repo = MagicMock()
        mock_repo.id = uuid4()
        mock_repo.name = "test-repo"
        mock_repo.full_name = "org/test-repo"
        mock_repo.description = "Test description"
        mock_repo.default_branch = "main"
        mock_repo.is_active = True
        mock_repo.created_at = datetime.utcnow()
        mock_repo.updated_at = datetime.utcnow()
        
        with patch('app.api.repositories.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.all.return_value = [mock_repo]
            mock_select.return_value.order_by.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.get("/api/repositories")
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["name"] == "test-repo"
            assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_repositories_include_inactive(self, client: AsyncClient):
        """Test listing repositories with include_inactive flag."""
        with patch('app.api.repositories.select') as mock_select:
            mock_query = MagicMock()
            mock_query.where.return_value = mock_query
            mock_result = AsyncMock()
            mock_result.all.return_value = []
            mock_query.exec = AsyncMock(return_value=mock_result)
            mock_select.return_value.order_by.return_value = mock_query
            
            response = await client.get("/api/repositories?include_inactive=true")
            assert response.status_code == 200


class TestCreateRepository:
    """Test POST /api/repositories endpoint."""

    @pytest.mark.asyncio
    async def test_create_repository_success(self, client: AsyncClient):
        """Test creating a repository successfully."""
        request_body = {
            "name": "new-repo",
            "full_name": "org/new-repo",
            "description": "New repository",
            "default_branch": "main"
        }
        
        with patch('app.api.repositories.Repository') as mock_repo:
            mock_repo_instance = MagicMock()
            mock_repo.return_value = mock_repo_instance
            
            with patch('app.api.repositories.select') as mock_select:
                mock_result = AsyncMock()
                mock_result.first.return_value = None
                mock_select.return_value.where.return_value.exec = AsyncMock(return_value=mock_result)
                
                response = await client.post("/api/repositories", json=request_body)
                assert response.status_code == 201
                data = response.json()
                assert data["name"] == "new-repo"

    @pytest.mark.asyncio
    async def test_create_repository_conflict(self, client: AsyncClient):
        """Test creating a duplicate repository returns 409."""
        request_body = {
            "name": "existing-repo",
            "full_name": "org/existing-repo"
        }
        
        with patch('app.api.repositories.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.first.return_value = MagicMock()
            mock_select.return_value.where.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.post("/api/repositories", json=request_body)
            assert response.status_code == 409


class TestUpdateRepository:
    """Test PATCH /api/repositories/{repo_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_repository_not_found(self, client: AsyncClient):
        """Test updating a non-existent repository."""
        repo_id = str(uuid4())
        
        with patch('app.api.repositories.select') as mock_select:
            mock_result = AsyncMock()
            mock_result.first.return_value = None
            mock_select.return_value.where.return_value.exec = AsyncMock(return_value=mock_result)
            
            response = await client.patch(f"/api/repositories/{repo_id}", json={"name": "updated"})
            assert response.status_code == 404


class TestRepositoryResponseModels:
    """Test Repository response model structure."""

    def test_repository_response_structure(self):
        """Test RepositoryResponse model structure."""
        from app.api.repositories import RepositoryResponse
        
        repo = RepositoryResponse(
            id=str(uuid4()),
            name="test-repo",
            full_name="org/test-repo",
        )
        
        assert repo.id is not None
        assert repo.name == "test-repo"

    def test_repositories_list_response_structure(self):
        """Test RepositoriesListResponse model structure."""
        from app.api.repositories import RepositoriesListResponse
        
        response = RepositoriesListResponse(
            items=[],
            total=0
        )
        
        assert response.items == []
        assert response.total == 0
