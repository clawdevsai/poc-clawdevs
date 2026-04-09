# Integrations Map

## Frontend to Backend
- Frontend API proxy route: `control-panel/frontend/src/app/api/[...slug]/route.ts`
- Frontend streaming route: `control-panel/frontend/src/app/openclaw/chat/stream/route.ts`
- HTTP client wrapper: `control-panel/frontend/src/lib/axios-instance.ts`
- API base URL resolver: `control-panel/frontend/src/lib/api-base-url.ts`
- Domain API helper example: `control-panel/frontend/src/lib/monitoring-api.ts`
- Real-time utility: `control-panel/frontend/src/lib/ws.ts`

## Backend Service Endpoints
- API modules under `control-panel/backend/app/api/*.py`
- Representative domains:
  - Auth: `app/api/auth.py`
  - Agents/session/task flows: `app/api/agents.py`, `app/api/sessions.py`, `app/api/tasks.py`
  - Chat and ws: `app/api/chat.py`, `app/api/ws.py`
  - Monitoring/metrics: `app/api/metrics.py`, `app/api/health.py`, `app/api/cluster.py`
  - Governance/SDD/context mode: `app/api/governance.py`, `app/api/sdd.py`, `app/api/context_mode*.py`

## Data and Infra Integrations
- PostgreSQL driver stack: `asyncpg`, `psycopg`, `sqlmodel`, `alembic`
- Vector extension support: `pgvector`
- Redis and async jobs: `redis[hiredis]`, `rq`, `rq-scheduler`
- Kubernetes client dependency: `kubernetes`

## Container and Platform Integrations
- Stack images and infra configs in `docker/`
- OpenClaw/Ollama services managed by root make targets (`make up-all`, `make logs`, etc.)
- Frontend and backend image definitions connected through compose-level scripts

## External-API Risk Areas
- Any provider keys and runtime secrets are likely sourced from `.env` files.
- Generated docs should avoid copying secret values from env/config artifacts.
