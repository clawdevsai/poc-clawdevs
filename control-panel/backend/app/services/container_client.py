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

import logging
from datetime import datetime, UTC
from urllib import error as url_error
from urllib import request as url_request

logger = logging.getLogger(__name__)

try:
    import kubernetes
except Exception:  # pragma: no cover
    kubernetes = None

DOCKER_STACK_SERVICES = [
    {"name": "clawdevs-openclaw", "url": "http://openclaw:18789/healthz"},
    {"name": "clawdevs-panel-backend", "url": "http://panel-backend:8000/healthz"},
    {"name": "clawdevs-panel-frontend", "url": "http://panel-frontend:3000/"},
    {"name": "clawdevs-ollama", "url": "http://ollama:11434/api/tags"},
    {"name": "clawdevs-searxng", "url": "http://searxng:8080/healthz"},
    {"name": "clawdevs-searxng-proxy", "url": "http://searxng-proxy:18080/healthz"},
]

DOCKER_STACK_STATE_ONLY = [
    "clawdevs-postgres",
    "clawdevs-redis",
    "clawdevs-panel-worker",
    "clawdevs-token-init",
]

DOCKER_STACK_VOLUMES = [
    "openclaw-data",
    "ollama-data",
    "postgres-data",
    "panel-token",
]


def _http_probe_ok(url: str, timeout_seconds: int = 2) -> bool:
    try:
        req = url_request.Request(url=url, method="GET")
        with url_request.urlopen(req, timeout=timeout_seconds) as response:
            return 200 <= response.status < 400
    except (url_error.URLError, url_error.HTTPError, TimeoutError, ValueError):
        return False


def _fallback_compose_containers() -> list[dict]:
    now_iso = datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z"
    containers: list[dict] = []

    for service in DOCKER_STACK_SERVICES:
        healthy = _http_probe_ok(service["url"])
        containers.append(
            {
                "name": service["name"],
                "namespace": "docker-run",
                "status": "Running" if healthy else "Degraded",
                "restarts": 0,
                "ready": healthy,
                "age": now_iso,
                "node": "local-docker",
            }
        )

    for name in DOCKER_STACK_STATE_ONLY:
        containers.append(
            {
                "name": name,
                "namespace": "docker-run",
                "status": "Running",
                "restarts": 0,
                "ready": True,
                "age": now_iso,
                "node": "local-docker",
            }
        )

    return containers


def _fallback_compose_events() -> list[dict]:
    now_iso = datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z"
    events: list[dict] = []
    for service in DOCKER_STACK_SERVICES:
        healthy = _http_probe_ok(service["url"])
        events.append(
            {
                "name": f"{service['name']}.health",
                "type": "Normal" if healthy else "Warning",
                "reason": "HealthProbe",
                "message": (
                    f"Service {service['name']} responding on {service['url']}"
                    if healthy
                    else f"Service {service['name']} not responding on {service['url']}"
                ),
                "involved_object": service["name"],
                "count": 1,
                "last_timestamp": now_iso,
            }
        )
    return events


def _fallback_compose_pvcs() -> list[dict]:
    return [
        {
            "name": volume_name,
            "status": "Bound",
            "capacity": "managed-by-docker",
            "access_modes": ["ReadWriteOnce"],
            "storage_class": "docker-volume",
            "namespace": "docker-run",
            "age": "—",
        }
        for volume_name in DOCKER_STACK_VOLUMES
    ]


def get_container_clients():
    """Get container management clients (deprecated kubernetes fallback (docker run))."""
    try:
        if kubernetes is None:
            logger.warning("Container management requires kubernetes package")
            return None, None
        client = kubernetes.client
        config_manager = kubernetes.config
        try:
            config_manager.load_incluster_config()
        except Exception:
            config_manager.load_kube_config()
        return client.CoreV1Api(), client.AppsV1Api()
    except Exception as e:
        logger.warning(f"Container client not available: {e}")
        return None, None


def list_containers(namespace: str = "default") -> list:
    """List containers (containers as fallback)."""
    core, _ = get_container_clients()
    if core is None:
        return _fallback_compose_containers()
    try:
        pods = core.list_namespaced_pod(namespace=namespace)
        return [
            {
                "name": p.metadata.name,
                "namespace": p.metadata.namespace,
                "status": p.status.phase or "Unknown",
                "restarts": sum(
                    c.restart_count for c in (p.status.container_statuses or [])
                ),
                "ready": (
                    all(c.ready for c in (p.status.container_statuses or []))
                    if p.status.container_statuses
                    else False
                ),
                "age": (
                    p.metadata.creation_timestamp.isoformat()
                    if p.metadata.creation_timestamp
                    else None
                ),
                "node": p.spec.node_name,
            }
            for p in pods.items
        ]
    except Exception as e:
        logger.error(f"Error listing containers: {e}")
        return _fallback_compose_containers()


def list_events(namespace: str = "default", limit: int = 50) -> list:
    """List container events."""
    core, _ = get_container_clients()
    if core is None:
        return _fallback_compose_events()
    try:
        events = core.list_namespaced_event(
            namespace=namespace,
            limit=limit,
        )
        return [
            {
                "name": e.metadata.name,
                "type": e.type,
                "reason": e.reason,
                "message": e.message,
                "involved_object": e.involved_object.name,
                "count": e.count,
                "last_timestamp": (
                    e.last_timestamp.isoformat() if e.last_timestamp else None
                ),
            }
            for e in sorted(
                events.items,
                key=lambda x: x.last_timestamp or x.metadata.creation_timestamp,
                reverse=True,
            )
        ]
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return _fallback_compose_events()


def list_pvcs(namespace: str = "default") -> list:
    """List persistent volume claims."""
    core, _ = get_container_clients()
    if core is None:
        return _fallback_compose_pvcs()
    try:
        pvcs = core.list_namespaced_persistent_volume_claim(namespace=namespace)
        return [
            {
                "name": p.metadata.name,
                "status": p.status.phase,
                "capacity": (
                    p.status.capacity.get("storage") if p.status.capacity else None
                ),
                "access_modes": p.spec.access_modes,
                "storage_class": p.spec.storage_class_name,
            }
            for p in pvcs.items
        ]
    except Exception as e:
        logger.error(f"Error listing PVCs: {e}")
        return _fallback_compose_pvcs()


def get_cluster_info(namespace: str = "default") -> dict:
    """Get container cluster information."""
    core, _ = get_container_clients()
    if core is None:
        return {
            "cluster_name": "docker-run",
            "namespace": "docker-run",
            "version": "local",
        }

    version = "unknown"
    cluster_name = None

    try:
        if kubernetes is not None:
            version_api = kubernetes.client.VersionApi()
            version_data = version_api.get_code()
            version = getattr(version_data, "git_version", None) or "unknown"
    except Exception as e:
        logger.warning(f"Error getting container version: {e}")

    try:
        nodes = core.list_node(limit=1)
        if nodes.items:
            cluster_name = nodes.items[0].metadata.cluster_name
    except Exception as e:
        logger.warning(f"Error getting cluster name: {e}")

    return {
        "cluster_name": cluster_name or "kubernetes",
        "namespace": namespace,
        "version": version,
    }


# Deprecated: maintained for backwards compatibility
get_container_clients = get_container_clients
list_pods = list_containers
