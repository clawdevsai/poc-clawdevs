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
Tests for Kubernetes client.
"""

from unittest.mock import patch, MagicMock
import logging


class TestK8sClient:
    """Test get_k8s_clients function."""

    def test_get_k8s_clients_success(self):
        """Test getting k8s clients when available."""
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

    def test_get_k8s_clients_fallback_to_kubeconfig(self):
        """Test fallback to kubeconfig when incluster fails."""
        with patch("app.services.k8s_client.kubernetes") as mock_k8s:
            mock_core = MagicMock()
            mock_apps = MagicMock()
            mock_k8s.client.CoreV1Api.return_value = mock_core
            mock_k8s.client.AppsV1Api.return_value = mock_apps
            mock_k8s.config.load_incluster_config = MagicMock(
                side_effect=Exception("No incluster config")
            )
            mock_k8s.config.load_kube_config = MagicMock()

            core, apps = __import__(
                "app.services.k8s_client", fromlist=["get_k8s_clients"]
            ).get_k8s_clients()

            assert core is not None
            assert apps is not None

    def test_get_k8s_clients_not_available(self):
        """Test when k8s is not available."""
        with patch("app.services.k8s_client.kubernetes") as mock_k8s:
            mock_k8s.client.CoreV1Api.side_effect = Exception("K8s not available")
            mock_k8s.config.load_incluster_config = MagicMock(
                side_effect=Exception("No config")
            )
            mock_k8s.config.load_kube_config = MagicMock(
                side_effect=Exception("No kubeconfig")
            )

            core, apps = __import__(
                "app.services.k8s_client", fromlist=["get_k8s_clients"]
            ).get_k8s_clients()

            assert core is None
            assert apps is None


class TestListPods:
    """Test list_pods function."""

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
        mock_pod.metadata.creation_timestamp = MagicMock()
        mock_pod.metadata.creation_timestamp.isoformat.return_value = (
            "2024-01-01T00:00:00"
        )
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

    def test_list_pods_empty(self):
        """Test list_pods when no pods exist."""
        from app.services.k8s_client import list_pods

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_pods_list = MagicMock()
            mock_pods_list.items = []
            mock_core.list_namespaced_pod.return_value = mock_pods_list
            mock_get_clients.return_value = (mock_core, None)

            pods = list_pods(namespace="default")
            assert pods == []

    def test_list_pods_error_handling(self):
        """Test list_pods error handling."""
        from app.services.k8s_client import list_pods

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_core.list_namespaced_pod.side_effect = Exception("API error")
            mock_get_clients.return_value = (mock_core, None)

            pods = list_pods(namespace="default")
            assert pods == []


class TestListEvents:
    """Test list_events function."""

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
        mock_event.last_timestamp = MagicMock()
        mock_event.last_timestamp.isoformat.return_value = "2024-01-01T00:00:00"

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_events_list = MagicMock()
            mock_events_list.items = [mock_event]
            mock_core.list_namespaced_event.return_value = mock_events_list
            mock_get_clients.return_value = (mock_core, None)

            events = list_events(namespace="default")
            assert len(events) == 1
            assert events[0]["name"] == "test-event"

    def test_list_events_empty(self):
        """Test list_events when no events exist."""
        from app.services.k8s_client import list_events

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_events_list = MagicMock()
            mock_events_list.items = []
            mock_core.list_namespaced_event.return_value = mock_events_list
            mock_get_clients.return_value = (mock_core, None)

            events = list_events(namespace="default")
            assert events == []


class TestListPvcs:
    """Test list_pvcs function."""

    def test_list_pvcs_no_core(self):
        """Test list_pvcs when k8s client is not available."""
        from app.services.k8s_client import list_pvcs

        with patch(
            "app.services.k8s_client.get_k8s_clients", return_value=(None, None)
        ):
            pvcs = list_pvcs(namespace="default")
            assert pvcs == []

    def test_list_pvcs_with_pvcs(self):
        """Test list_pvcs when PVCs exist."""
        from app.services.k8s_client import list_pvcs

        mock_pvc = MagicMock()
        mock_pvc.metadata.name = "test-pvc"
        mock_pvc.status.phase = "Bound"
        mock_pvc.status.capacity = {"storage": "10Gi"}
        mock_pvc.spec.access_modes = ["ReadWriteOnce"]
        mock_pvc.spec.storage_class_name = "standard"

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_pvcs_list = MagicMock()
            mock_pvcs_list.items = [mock_pvc]
            mock_core.list_namespaced_persistent_volume_claim.return_value = (
                mock_pvcs_list
            )
            mock_get_clients.return_value = (mock_core, None)

            pvcs = list_pvcs(namespace="default")
            assert len(pvcs) == 1
            assert pvcs[0]["name"] == "test-pvc"

    def test_list_pvcs_empty(self):
        """Test list_pvcs when no PVCs exist."""
        from app.services.k8s_client import list_pvcs

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_pvcs_list = MagicMock()
            mock_pvcs_list.items = []
            mock_core.list_namespaced_persistent_volume_claim.return_value = (
                mock_pvcs_list
            )
            mock_get_clients.return_value = (mock_core, None)

            pvcs = list_pvcs(namespace="default")
            assert pvcs == []

    def test_list_pvcs_error_handling(self):
        """Test list_pvcs error handling."""
        from app.services.k8s_client import list_pvcs

        with patch("app.services.k8s_client.get_k8s_clients") as mock_get_clients:
            mock_core = MagicMock()
            mock_core.list_namespaced_persistent_volume_claim.side_effect = Exception(
                "API error"
            )
            mock_get_clients.return_value = (mock_core, None)

            pvcs = list_pvcs(namespace="default")
            assert pvcs == []


class TestLogging:
    """Test logging in k8s client."""

    def test_logger_exists(self):
        """Test that logger is configured."""
        from app.services.k8s_client import logger

        assert logger is not None
        assert isinstance(logger, logging.Logger)
