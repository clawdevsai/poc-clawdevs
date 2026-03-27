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

logger = logging.getLogger(__name__)

try:
    import kubernetes  # type: ignore
except Exception:  # pragma: no cover
    kubernetes = None


def get_k8s_clients():
    try:
        if kubernetes is None:
            raise RuntimeError("kubernetes package not available")
        client = kubernetes.client
        k8s_config = kubernetes.config
        try:
            k8s_config.load_incluster_config()
        except Exception:
            k8s_config.load_kube_config()
        return client.CoreV1Api(), client.AppsV1Api()
    except Exception as e:
        logger.warning(f"Kubernetes client not available: {e}")
        return None, None


def list_pods(namespace: str = "default") -> list:
    core, _ = get_k8s_clients()
    if core is None:
        return []
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
                "ready": all(
                    c.ready for c in (p.status.container_statuses or [])
                ) if p.status.container_statuses else False,
                "age": p.metadata.creation_timestamp.isoformat() if p.metadata.creation_timestamp else None,
                "node": p.spec.node_name,
            }
            for p in pods.items
        ]
    except Exception as e:
        logger.error(f"Error listing pods: {e}")
        return []


def list_events(namespace: str = "default", limit: int = 50) -> list:
    core, _ = get_k8s_clients()
    if core is None:
        return []
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
                "last_timestamp": e.last_timestamp.isoformat() if e.last_timestamp else None,
            }
            for e in sorted(
                events.items,
                key=lambda x: x.last_timestamp or x.metadata.creation_timestamp,
                reverse=True,
            )
        ]
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return []


def list_pvcs(namespace: str = "default") -> list:
    core, _ = get_k8s_clients()
    if core is None:
        return []
    try:
        pvcs = core.list_namespaced_persistent_volume_claim(namespace=namespace)
        return [
            {
                "name": p.metadata.name,
                "status": p.status.phase,
                "capacity": p.status.capacity.get("storage") if p.status.capacity else None,
                "access_modes": p.spec.access_modes,
                "storage_class": p.spec.storage_class_name,
            }
            for p in pvcs.items
        ]
    except Exception as e:
        logger.error(f"Error listing PVCs: {e}")
        return []


def get_cluster_info(namespace: str = "default") -> dict:
    core, _ = get_k8s_clients()
    if core is None:
        return {"cluster_name": None, "namespace": namespace, "k8s_version": "unknown"}

    k8s_version = "unknown"
    cluster_name = None

    try:
        if kubernetes is not None:
            version_api = kubernetes.client.VersionApi()
            version_data = version_api.get_code()
            k8s_version = getattr(version_data, "git_version", None) or "unknown"
    except Exception as e:
        logger.warning(f"Error getting Kubernetes version: {e}")

    try:
        nodes = core.list_node(limit=1)
        if nodes.items:
            cluster_name = nodes.items[0].metadata.cluster_name
    except Exception as e:
        logger.warning(f"Error getting cluster name: {e}")

    return {
        "cluster_name": cluster_name,
        "namespace": namespace,
        "k8s_version": k8s_version,
    }
