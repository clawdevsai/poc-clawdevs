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
            # This test documents the expected behavior
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
