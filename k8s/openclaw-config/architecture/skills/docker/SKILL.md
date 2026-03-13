# Docker

Use this skill when defining container images, local dev containers, and runtime hardening.

Guidelines:
- Use small base images and pin major versions.
- Minimize layers and remove build-time artifacts.
- Run as non-root whenever possible.
- Expose only required ports and env vars.
- Add health checks and deterministic startup commands.

Checklist:
1. Use multi-stage builds for compiled workloads.
2. Keep image size and CVE count low.
3. Validate reproducible builds in CI.
4. Document run command, env vars, and volumes.
