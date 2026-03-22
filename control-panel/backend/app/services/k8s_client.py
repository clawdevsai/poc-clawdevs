from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_k8s_clients():
    try:
        from kubernetes import client, config as k8s_config
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
