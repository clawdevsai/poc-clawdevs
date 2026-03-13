# Kubernetes

Use this skill when planning deployments, service exposure, resilience, and production operations on Kubernetes.

Guidelines:
- Define clear CPU/memory requests and limits.
- Keep probes accurate: startup, readiness, and liveness.
- Use Secrets/ConfigMaps for runtime configuration.
- Enforce least privilege with RBAC and network policies.
- Prefer rolling updates with safe rollback strategy.

Checklist:
1. Validate manifests with environment overlays.
2. Add observability: logs, metrics, and events.
3. Confirm autoscaling behavior under load.
4. Verify backup/restore for stateful components.
