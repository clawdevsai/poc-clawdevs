# Concerns Map

## Security and Secrets
- Default secrets exist in code/config defaults (`secret_key`, admin password placeholder defaults). Safe for local dev, but risky if env override discipline slips.
- `.env.example` and startup docs emphasize real secret injection, but operational safety depends on strict environment hygiene.
- OpenClaw defaults include `OPENCLAW_SANDBOX_MODE=off` in env templates; this should remain intentional and tightly controlled.

## Operational Coupling
- Stack startup is script-driven with many inter-service dependencies (DB/Redis/backend/token-init/openclaw order).
- Failures in one core service (for example backend health or OpenClaw gateway) can cascade into degraded panel behavior.
- Orchestration is imperative shell, not declarative compose/k8s manifests in this repo root, increasing script maintenance burden.

## Runtime Complexity
- Multiple subsystems coexist: panel API/UI, worker queue, OpenClaw agents, Ollama inference, SearXNG search, token bootstrap.
- Feature flags for semantic optimization and orchestration parallelism add rollout flexibility but increase state-space and test permutations.

## Test Coverage Imbalance
- Backend has deep and broad test inventory.
- Frontend has comparatively few visible E2E specs (`login`, `chat`) relative to page/component footprint.
- Realtime monitoring/context-mode UX appears high-surface and may need stronger automated regression coverage.

## Data and Migration Risk
- Backend startup can run migrations automatically; convenient locally but needs careful controls in shared/prod-like environments.
- `allow_schema_create_all_fallback` exists and should remain disabled except for controlled scenarios to avoid silent schema drift.

## Dependency and Upgrade Risk
- Stack spans fast-moving ecosystems (Next 16/React 19/FastAPI/SQLAlchemy/Redis/Ollama/OpenClaw).
- Frequent image, Python, and Node dependency updates can introduce compatibility drift across containers.

## Environment Drift Risk
- Repo/worktree contains local runtime artifacts (`.venv`, `.mypy_cache`, `.next`, local logs, local node_modules trees) during development.
- If hygiene/ignore rules are bypassed, these can pollute diffs, reviews, and CI expectations.

## Observability and Failure Handling
- Health monitors and broadcasters are present, but production-grade alerting/escalation guarantees depend on external ops practices.
- Global exception handler normalizes 500 responses but can hide granular error context from callers unless logs are actively monitored.

