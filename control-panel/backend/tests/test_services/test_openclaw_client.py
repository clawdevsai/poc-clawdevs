import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime


class TestK8sClients:
    """Test k8s_client functions (with mocking)."""

    def test_get_k8s_clients_no_cluster(self):
        """Test get_k8s_clients when no cluster config is available."""
        with patch('app.services.k8s_client.kubernetes') as mock_k8s:
            mock_k8s.client = MagicMock()
            mock_k8s.config = MagicMock()
            mock_k8s.config.load_incluster_config.side_effect = Exception("No config")
            mock_k8s.config.load_kube_config.side_effect = Exception("No kubeconfig")
            
            core, apps = __import__('app.services.k8s_client', fromlist=['get_k8s_clients']).get_k8s_clients()
            
            # Should return None, None when k8s is not available
            assert core is None
            assert apps is None

    def test_list_pods_no_core(self):
        """Test list_pods when k8s client is not available."""
        from app.services.k8s_client import list_pods
        
        # Mock get_k8s_clients to return None
        with patch('app.services.k8s_client.get_k8s_clients', return_value=(None, None)):
            pods = list_pods(namespace="default")
            assert pods == []

    def test_list_events_no_core(self):
        """Test list_events when k8s client is not available."""
        from app.services.k8s_client import list_events
        
        with patch('app.services.k8s_client.get_k8s_clients', return_value=(None, None)):
            events = list_events(namespace="default")
            assert events == []

    def test_list_pvcs_no_core(self):
        """Test list_pvcs when k8s client is not available."""
        from app.services.k8s_client import list_pvcs
        
        with patch('app.services.k8s_client.get_k8s_clients', return_value=(None, None)):
            pvcs = list_pvcs(namespace="default")
            assert pvcs == []


class TestOpenClawClient:
    """Test OpenClawClient class."""

    @pytest.mark.asyncio
    async def test_health_success(self):
        """Test health check returns True on success."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        # Mock httpx.AsyncClient
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_async_client.return_value = mock_instance
            
            result = await client.health()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_failure(self):
        """Test health check returns False on failure."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Connection error"))
            mock_async_client.return_value = mock_instance
            
            result = await client.health()
            assert result is False

    @pytest.mark.asyncio
    async def test_get_sessions_success(self):
        """Test get_sessions returns list on success."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "1"}, {"id": "2"}]}
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_async_client.return_value = mock_instance
            
            sessions = await client.get_sessions(limit=50)
            assert len(sessions) == 2
            assert sessions[0]["id"] == "1"

    @pytest.mark.asyncio
    async def test_get_sessions_failure(self):
        """Test get_sessions returns empty list on failure."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_async_client.return_value = mock_instance
            
            sessions = await client.get_sessions()
            assert sessions == []

    @pytest.mark.asyncio
    async def test_get_session_success(self):
        """Test get_session returns dict on success."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "session-123"}
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_async_client.return_value = mock_instance
            
            session = await client.get_session("session-123")
            assert session["id"] == "session-123"

    @pytest.mark.asyncio
    async def test_get_session_not_found(self):
        """Test get_session returns None when not found."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_async_client.return_value = mock_instance
            
            session = await client.get_session("non-existent")
            assert session is None

    @pytest.mark.asyncio
    async def test_get_approvals_success(self):
        """Test get_approvals returns list on success."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "approval-1"}]}
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_async_client.return_value = mock_instance
            
            approvals = await client.get_approvals(status="pending")
            assert len(approvals) == 1

    @pytest.mark.asyncio
    async def test_decide_approval_success(self):
        """Test decide_approval returns dict on success."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "approval-1", "decision": "approved"}
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            mock_async_client.return_value = mock_instance
            
            result = await client.decide_approval(
                approval_id="approval-1",
                decision="approved",
                justification="Looks good"
            )
            assert result["decision"] == "approved"

    @pytest.mark.asyncio
    async def test_decide_approval_failure(self):
        """Test decide_approval returns None on failure."""
        from app.services.openclaw_client import OpenClawClient
        
        client = OpenClawClient()
        
        mock_response = MagicMock()
        mock_response.status_code = 403  # Forbidden
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            mock_async_client.return_value = mock_instance
            
            result = await client.decide_approval(
                approval_id="approval-1",
                decision="approved"
            )
            assert result is None


class TestOpenClawClientIntegration:
    """Test OpenClawClient with config mocking."""

    @pytest.mark.asyncio
    async def test_client_uses_config_url(self):
        """Test that client uses the configured base URL."""
        from app.services.openclaw_client import OpenClawClient
        from unittest.mock import patch
        
        # Mock settings
        with patch('app.services.openclaw_client.settings') as mock_settings:
            mock_settings.openclaw_gateway_url = "https://openclaw.example.com/"
            mock_settings.openclaw_gateway_token = "test-token"
            
            client = OpenClawClient()
            assert client.base_url == "https://openclaw.example.com"
            assert "test-token" in client.headers["Authorization"]
