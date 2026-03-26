"""
Test suite for Repositories API endpoints.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Repository


class TestListRepositories:
    """Test GET /api/repositories endpoint."""

    @pytest.mark.asyncio
    async def test_list_repositories_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing repositories when none exist."""
        response = await client.get("/repositories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_repositories_with_repos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        """Test listing repositories when they exist."""
        repo = Repository(
            name="test-repo",
            full_name="org/test-repo",
            description="Test description",
            default_branch="main",
            is_active=True,
        )
        db_session.add(repo)
        await db_session.commit()

        response = await client.get("/repositories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "test-repo"
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_list_repositories_include_inactive(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        """Test listing repositories with include_inactive flag."""
        repo = Repository(
            name="inactive-repo",
            full_name="org/inactive-repo",
            description=None,
            default_branch="main",
            is_active=False,
        )
        db_session.add(repo)
        await db_session.commit()

        response = await client.get(
            "/repositories?include_inactive=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestCreateRepository:
    """Test POST /api/repositories endpoint."""

    @pytest.mark.asyncio
    async def test_create_repository_success(self, client: AsyncClient, auth_headers: dict):
        """Test creating a repository successfully."""
        request_body = {
            "name": "new-repo",
            "full_name": "org/new-repo",
            "description": "New repository",
            "default_branch": "main"
        }

        response = await client.post(
            "/repositories", json=request_body, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new-repo"
        assert data["full_name"] == "org/new-repo"

    @pytest.mark.asyncio
    async def test_create_repository_conflict(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers: dict,
    ):
        """Test creating a duplicate repository returns 409."""
        request_body = {
            "name": "existing-repo",
            "full_name": "org/existing-repo"
        }

        existing = Repository(
            name="existing-repo",
            full_name="org/existing-repo",
            description=None,
            default_branch="main",
            is_active=True,
        )
        db_session.add(existing)
        await db_session.commit()

        response = await client.post(
            "/repositories", json=request_body, headers=auth_headers
        )
        assert response.status_code == 409


class TestUpdateRepository:
    """Test PATCH /api/repositories/{repo_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_repository_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating a non-existent repository."""
        repo_id = str(uuid4())
        response = await client.patch(
            f"/repositories/{repo_id}",
            json={"name": "updated"},
            headers=auth_headers,
        )
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
            description=None,
            default_branch="main",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
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
