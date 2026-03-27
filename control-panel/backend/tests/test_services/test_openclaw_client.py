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
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime


class TestK8sClients:
    """Test k8s_client functions (with mocking)."""

    def test_get_k8s_clients_no_cluster(self):
        """Test get_k8s_clients when no cluster config is available."""
        with patch("app.services.k8s_client.kubernetes") as mock_k8s:
            mock_k8s.client = MagicMock()
            mock_k8s.config = MagicMock()
            mock_k8s.config.load_incluster_config.side_effect = Exception("No config")
            mock_k8s.config.load_kube_config.side_effect = Exception("No kubeconfig")

            core, apps = __import__(
                "app.services.k8s_client", fromlist=["get_k8s_clients"]
            ).get_k8s_clients()

            assert core is None
            assert apps is None

    def test_get_k8s_clients_with_cluster(self):
        """Test get_k8s_clients when cluster config is available."""
        with patch("app.services.k8s_client.kubernetes") as mock_k8s:
            mock_core = MagicMock()
            mock_apps = MagicMock()
            mock_k8s.client.CoreV1Api.return_value = mock_core
            mock_k8s.client.AppsV1Api.return_value = mock_apps
            mock_k8s.config.load_incluster_config = MagicMock()

            core, apps = __import__(
                "app.services.k8s_client", fromlist=["get_k8s_clients"]
            ).get_k8s_clients()

            assert core is not None
            assert apps is not None

    def test_list_pods_no_core(self):
        """Test list_pods when k8s client is not available."""
        from app.services.k8s_client import list_pods

        with patch(
            "app.services.k8s_client.get_k8s_clients", return_value=(None, None)
        ):
            pods = list_pods(namespace="default")
            assert pods == []

    def test_list_pods_with_pods(self):
        """Test list_pods when pods exist."""
        from app.services.k8s_client import list_pods

        mock_pod = MagicMock()
        mock_pod.metadata.name = "test-pod"
        mock_pod.metadata.namespace = "default"
        mock_pod.status.phase = "Running"
        mock_pod.status.container_statuses = [MagicMock(restart_count=0, ready=True)]
        mock_pod.metadata.creation_timestamp = datetime.utcnow()
        mock_pod.spec.node_name = "node-1"

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_pods_list = MagicMock()
            mock_pods_list.items = [mock_pod]
            mock_core.list_namespaced_pod.return_value = mock_pods_list
            mock_get_clients.return_value = (mock_core, None)

            pods = list_pods(namespace="default")
            assert len(pods) == 1
            assert pods[0]["name"] == "test-pod"

    def test_list_events_no_core(self):
        """Test list_events when k8s client is not available."""
        from app.services.k8s_client import list_events

        with patch(
            "app.services.k8s_client.get_k8s_clients", return_value=(None, None)
        ):
            events = list_events(namespace="default")
            assert events == []

    def test_list_events_with_events(self):
        """Test list_events when events exist."""
        from app.services.k8s_client import list_events

        mock_event = MagicMock()
        mock_event.metadata.name = "test-event"
        mock_event.type = "Normal"
        mock_event.reason = "Scheduled"
        mock_event.message = "Successfully assigned"
        mock_event.involved_object.name = "test-pod"
        mock_event.count = 1
        mock_event.last_timestamp = datetime.utcnow()

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_events_list = MagicMock()
            mock_events_list.items = [mock_event]
            mock_core.list_namespaced_event.return_value = mock_events_list
            mock_get_clients.return_value = (mock_core, None)

            events = list_events(namespace="default")
            assert len(events) == 1
            assert events[0]["name"] == "test-event"

    def test_list_pvcs_no_core(self):
        """Test list_pvcs when k8s client is not available."""
        from app.services.k8s_client import list_pvcs

        with patch(
            "app.services.k8s_client.get_k8s_clients", return_value=(None, None)
        ):
            pvcs = list_pvcs(namespace="default")
            assert pvcs == []


class TestOpenClawClient:
    """Test OpenClawClient class."""

    @pytest.mark.asyncio
    async def test_health_success(self):
        """Test health check returns True on success."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            mock_async_client.return_value = mock_instance

            result = await client.health()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_failure(self):
        """Test health check returns False on failure."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Connection error")
            )
            mock_async_client.return_value = mock_instance

            result = await client.health()
            assert result is False

    @pytest.mark.asyncio
    async def test_health_connection_timeout(self):
        """Test health check with connection timeout."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                side_effect=TimeoutError("Connection timeout")
            )
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

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
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
        mock_response.status_code = 401

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            mock_async_client.return_value = mock_instance

            sessions = await client.get_sessions()
            assert sessions == []

    @pytest.mark.asyncio
    async def test_get_sessions_empty_response(self):
        """Test get_sessions with empty response."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
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

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
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

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            mock_async_client.return_value = mock_instance

            session = await client.get_session("non-existent")
            assert session is None

    @pytest.mark.asyncio
    async def test_get_sessions_error_handling(self):
        """Test get_sessions with error handling."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("API error")
            )
            mock_async_client.return_value = mock_instance

            sessions = await client.get_sessions()
            assert sessions == []

    @pytest.mark.asyncio
    async def test_get_approvals_success(self):
        """Test get_approvals returns list on success."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "approval-1"}]}

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            mock_async_client.return_value = mock_instance

            approvals = await client.get_approvals(status="pending")
            assert len(approvals) == 1

    @pytest.mark.asyncio
    async def test_get_approvals_failure(self):
        """Test get_approvals returns empty list on failure."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            mock_async_client.return_value = mock_instance

            approvals = await client.get_approvals()
            assert approvals == []

    @pytest.mark.asyncio
    async def test_decide_approval_success(self):
        """Test decide_approval returns dict on success."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "approval-1", "decision": "approved"}

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            mock_async_client.return_value = mock_instance

            result = await client.decide_approval(
                approval_id="approval-1",
                decision="approved",
                justification="Looks good",
            )
            assert result["decision"] == "approved"

    @pytest.mark.asyncio
    async def test_decide_approval_failure(self):
        """Test decide_approval returns None on failure."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        mock_response = MagicMock()
        mock_response.status_code = 403

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            mock_async_client.return_value = mock_instance

            result = await client.decide_approval(
                approval_id="approval-1", decision="approved"
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_decide_approval_internal_error(self):
        """Test decide_approval with internal server error."""
        from app.services.openclaw_client import OpenClawClient

        client = OpenClawClient()

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("Server error")
            )
            mock_async_client.return_value = mock_instance

            result = await client.decide_approval(
                approval_id="approval-1", decision="approved"
            )
            assert result is None


class TestOpenClawClientIntegration:
    """Test OpenClawClient with config mocking."""

    def test_client_uses_config_url(self):
        """Test that client uses the configured base URL."""
        from app.services.openclaw_client import OpenClawClient
        from unittest.mock import patch

        with patch("app.services.openclaw_client.settings") as mock_settings:
            mock_settings.openclaw_gateway_url = "https://openclaw.example.com/"
            mock_settings.openclaw_gateway_token = "test-token"

            client = OpenClawClient()
            assert client.base_url == "https://openclaw.example.com"
            assert "test-token" in client.headers["Authorization"]

    def test_client_default_url(self):
        """Test that client uses default URL when not configured."""
        from app.services.openclaw_client import OpenClawClient
        from unittest.mock import patch

        with patch("app.services.openclaw_client.settings") as mock_settings:
            mock_settings.openclaw_gateway_url = "http://clawdevs-ai:18789"
            mock_settings.openclaw_gateway_token = ""

            client = OpenClawClient()
            assert "clawdevs-ai" in client.base_url

    def test_client_without_token(self):
        """Test client without token."""
        from app.services.openclaw_client import OpenClawClient
        from unittest.mock import patch

        with patch("app.services.openclaw_client.settings") as mock_settings:
            mock_settings.openclaw_gateway_url = "https://openclaw.example.com/"
            mock_settings.openclaw_gateway_token = ""

            client = OpenClawClient()
            assert client.base_url == "https://openclaw.example.com"
            assert client.headers["Authorization"] == "Bearer "
