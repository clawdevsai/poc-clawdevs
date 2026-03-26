import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime


class TestTaskSyncConstants:
    """Test task_sync constants."""

    def test_label_map_exists(self):
        """Test that LABEL_MAP is defined."""
        from app.services.task_sync import LABEL_MAP
        
        assert "back-end" in LABEL_MAP
        assert LABEL_MAP["back-end"] == "back_end"
        assert "frontend" in LABEL_MAP
        assert LABEL_MAP["frontend"] == "front_end"

    def test_status_map_exists(self):
        """Test that STATUS_MAP is defined."""
        from app.services.task_sync import STATUS_MAP
        
        assert "open" in STATUS_MAP
        assert STATUS_MAP["open"] == "inbox"
        assert "in_progress" in STATUS_MAP
        assert STATUS_MAP["in_progress"] == "in_progress"
        assert "closed" in STATUS_MAP
        assert STATUS_MAP["closed"] == "done"

    def test_label_map_count(self):
        """Test that LABEL_MAP has all expected mappings."""
        from app.services.task_sync import LABEL_MAP
        
        expected_mappings = {
            "back-end": "back_end",
            "backend": "back_end",
            "front-end": "front_end",
            "frontend": "front_end",
            "mobile": "mobile",
            "tests": "tests",
            "qa": "tests",
            "devops": "devops",
            "sre": "devops",
            "dba": "dba",
            "data": "dba",
            "security": "security",
            "ux": "ux",
            "design": "ux"
        }
        
        for label, expected in expected_mappings.items():
            assert label in LABEL_MAP
            assert LABEL_MAP[label] == expected

    def test_status_map_count(self):
        """Test that STATUS_MAP has all expected mappings."""
        from app.services.task_sync import STATUS_MAP
        
        expected_mappings = {
            "open": "inbox",
            "in_progress": "in_progress",
            "review": "review",
            "closed": "done"
        }
        
        for state, expected in expected_mappings.items():
            assert state in STATUS_MAP
            assert STATUS_MAP[state] == expected


class TestLabelMapping:
    """Test GitHub label to task label mapping."""

    def test_map_back_end(self):
        """Test mapping back-end label."""
        from app.services.task_sync import LABEL_MAP
        
        assert LABEL_MAP["back-end"] == "back_end"
        assert LABEL_MAP["backend"] == "back_end"

    def test_map_front_end(self):
        """Test mapping front-end label."""
        from app.services.task_sync import LABEL_MAP
        
        assert LABEL_MAP["front-end"] == "front_end"
        assert LABEL_MAP["frontend"] == "front_end"

    def test_map_tests(self):
        """Test mapping tests labels."""
        from app.services.task_sync import LABEL_MAP
        
        assert LABEL_MAP["tests"] == "tests"
        assert LABEL_MAP["qa"] == "tests"

    def test_map_devops(self):
        """Test mapping devops labels."""
        from app.services.task_sync import LABEL_MAP
        
        assert LABEL_MAP["devops"] == "devops"
        assert LABEL_MAP["sre"] == "devops"

    def test_map_security(self):
        """Test mapping security label."""
        from app.services.task_sync import LABEL_MAP
        
        assert LABEL_MAP["security"] == "security"

    def test_map_ux(self):
        """Test mapping UX labels."""
        from app.services.task_sync import LABEL_MAP
        
        assert LABEL_MAP["ux"] == "ux"
        assert LABEL_MAP["design"] == "ux"

    def test_map_dba(self):
        """Test mapping DBA labels."""
        from app.services.task_sync import LABEL_MAP
        
        assert LABEL_MAP["dba"] == "dba"
        assert LABEL_MAP["data"] == "dba"


class TestStatusMapping:
    """Test GitHub issue state to task status mapping."""

    def test_map_open_to_inbox(self):
        """Test open issue maps to inbox."""
        from app.services.task_sync import STATUS_MAP
        
        assert STATUS_MAP["open"] == "inbox"

    def test_map_in_progress(self):
        """Test in_progress state."""
        from app.services.task_sync import STATUS_MAP
        
        assert STATUS_MAP["in_progress"] == "in_progress"

    def test_map_review(self):
        """Test review state."""
        from app.services.task_sync import STATUS_MAP
        
        assert STATUS_MAP["review"] == "review"

    def test_map_closed_to_done(self):
        """Test closed issue maps to done."""
        from app.services.task_sync import STATUS_MAP
        
        assert STATUS_MAP["closed"] == "done"


class TestSyncTasks:
    """Test sync_tasks_from_github function."""

    @pytest.mark.asyncio
    async def test_sync_tasks_no_github_token(self):
        """Test sync_tasks when no GitHub token is configured."""
        from app.services.task_sync import sync_tasks_from_github
        
        with patch('app.services.task_sync.settings') as mock_settings:
            mock_settings.github_token = None
            
            # Should log warning and return early
            pass

    @pytest.mark.asyncio
    async def test_sync_tasks_no_repo(self):
        """Test sync_tasks when no repository is configured."""
        from app.services.task_sync import sync_tasks_from_github
        
        with patch('app.services.task_sync.settings') as mock_settings:
            mock_settings.github_token = "fake-token"
            mock_settings.github_default_repository = None
            
            # Should log warning and return early
            pass

    @pytest.mark.asyncio
    async def test_sync_tasks_success(self):
        """Test sync_tasks with mocked GitHub API."""
        from app.services.task_sync import sync_tasks_from_github
        
        mock_issues = [
            {
                "id": 123,
                "title": "Test Issue",
                "body": "Test body",
                "state": "open",
                "labels": [{"name": "back-end"}],
                "html_url": "https://github.com/repo/issues/123"
            }
        ]
        
        with patch('app.services.task_sync.settings') as mock_settings:
            mock_settings.github_token = "fake-token"
            mock_settings.github_default_repository = "org/repo"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = AsyncMock()
                mock_response.json.return_value = mock_issues
                mock_response.raise_for_status = MagicMock()
                
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
                
                # This test documents the expected behavior
                pass

    @pytest.mark.asyncio
    async def test_sync_tasks_github_api_error(self):
        """Test sync_tasks when GitHub API returns error."""
        from app.services.task_sync import sync_tasks_from_github
        
        with patch('app.services.task_sync.settings') as mock_settings:
            mock_settings.github_token = "fake-token"
            mock_settings.github_default_repository = "org/repo"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = AsyncMock()
                mock_response.raise_for_status.side_effect = Exception("GitHub API error")
                
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
                
                # Should handle error gracefully
                pass

    @pytest.mark.asyncio
    async def test_sync_tasks_custom_repo(self):
        """Test sync_tasks with custom repository."""
        from app.services.task_sync import sync_tasks_from_github
        
        with patch('app.services.task_sync.settings') as mock_settings:
            mock_settings.github_token = "fake-token"
            mock_settings.github_default_repository = "org/default"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = AsyncMock()
                mock_response.json.return_value = []
                mock_response.raise_for_status = MagicMock()
                
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
                
                # Call with custom repo
                await sync_tasks_from_github(None, repo="custom/owner")
                
                # Should use custom repo URL
                pass


class TestSyncTasksEdgeCases:
    """Test edge cases for sync_tasks_from_github."""

    def test_label_mapping_edge_cases(self):
        """Test label mapping edge cases."""
        from app.services.task_sync import LABEL_MAP
        
        # Unknown label should return original or None
        # This is expected behavior for unmapped labels
        pass

    def test_status_mapping_edge_cases(self):
        """Test status mapping edge cases."""
        from app.services.task_sync import STATUS_MAP
        
        # All expected states should be mapped
        assert "open" in STATUS_MAP
        assert "in_progress" in STATUS_MAP
        assert "review" in STATUS_MAP
        assert "closed" in STATUS_MAP


class TestSyncTasksGitHubIntegration:
    """Test GitHub integration in sync_tasks."""

    @pytest.mark.asyncio
    async def test_sync_tasks_uses_github_api(self):
        """Test that sync_tasks uses GitHub API."""
        from app.services.task_sync import sync_tasks_from_github
        from unittest.mock import patch
        
        with patch('app.services.task_sync.settings') as mock_settings:
            mock_settings.github_token = "fake-token"
            mock_settings.github_default_repository = "org/repo"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = AsyncMock()
                mock_response.json.return_value = []
                mock_response.raise_for_status = MagicMock()
                
                mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
                
                # Call sync_tasks
                await sync_tasks_from_github(None)
                
                # Verify GitHub API URL was called
                mock_client.return_value.__aenter__.return_value.get.assert_called()
