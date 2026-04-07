# Architecture Map

## System Shape
The platform is a multi-container local stack with two main planes:
- Agent plane: OpenClaw + Ollama + SearXNG.
- Control plane: Panel Backend (FastAPI) + Panel Frontend (Next.js) + Panel Worker.

The root `Makefile` and `scripts/docker/*.sh` orchestrate build/startup, network/volumes, and service lifecycles.

## Backend Architecture (`control-panel/backend/app`)

## Entry and Lifecycle
- `app/main.py` builds FastAPI app with `lifespan`.
- Startup sequence:
  1. run DB migrations (`run_migrations`)
  2. bootstrap admin user
  3. sync/bootstrap agents
  4. start health monitor loop (feature-flagged)
  5. start context-mode metrics broadcaster

## Layering
- API layer: `app/api/*` routers grouped by domain (`auth`, `agents`, `approvals`, `sessions`, `tasks`, `memory`, `metrics`, `settings`, `context_mode`, etc.).
- Core layer: `app/core/*` for config, auth primitives, DB setup/session.
- Model layer: `app/models/*` SQLModel entities.
- Service layer: `app/services/*` business logic/integration clients (OpenClaw/Ollama/memory/governance/orchestration/health).
- Task/background layer: `app/tasks/*` and worker-linked orchestration routines.
- Hook layer: `app/hooks/*` cross-cutting behavior around tool/semantic events.

## Cross-Cutting Patterns
- Dependency injection with FastAPI `Depends` and typed aliases (`CurrentUser`, `AdminUser`).
- Central global exception handler for 500 responses.
- CORS middleware from settings.
- JWT auth + role checks + optional per-agent authorization table.

## Frontend Architecture (`control-panel/frontend/src`)

## App Router Composition
- Root layout (`src/app/layout.tsx`) wraps all pages with shared `Providers`.
- Providers include React Query client and Tooltip provider.
- Route folders map dashboard sections: `agents`, `approvals`, `chat`, `cluster`, `crons`, `memory`, `monitoring`, `sessions`, `settings`, `tasks`, `sdd`.

## UI and Data Access Layers
- UI components split by domain under `src/components/*` plus shared primitives in `src/components/ui`.
- API/client utilities in `src/lib/*`:
  - generated OpenAPI clients (`src/lib/api/*`),
  - Axios auth handling,
  - WebSocket manager,
  - query client setup,
  - API/WS base URL resolution.

## Realtime and Monitoring
- Frontend subscribes to channelized WebSocket streams.
- Backend exposes WS routes and context-mode metrics endpoints for monitoring panels.

## Runtime Deployment Topology
- Services run in one Docker network (`clawdevs`).
- Critical startup dependencies:
  - Postgres/Redis before panel backend and worker.
  - Backend health before token-init.
  - OpenClaw starts after core stack from `run-openclaw.sh`.
- Persistent state flows through named volumes, especially `openclaw-data` and `panel-token`.

