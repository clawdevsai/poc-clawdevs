# Structure Map

## Repository Root
- `.github/workflows/` CI and deployment validation workflows.
- `assets/` static project avatars/media.
- `control-panel/` application code (backend + frontend).
- `docker/` Dockerfiles and runtime assets for each service.
- `scripts/docker/` shell orchestration scripts (start/stop/bootstrap helpers).
- `docs/` architecture/guides/operations/reference docs.
- `tests/` root-level tests (in addition to backend/frontend scoped tests).
- `Makefile` central operational interface.

## Control Panel Backend (`control-panel/backend`)
- `app/main.py` FastAPI entrypoint and router registration.
- `app/api/` HTTP and WebSocket router modules by feature area.
- `app/core/` settings/auth/database foundation.
- `app/models/` SQLModel entities.
- `app/services/` integration and domain logic.
- `app/tasks/` scheduled/background orchestration routines.
- `migrations/` Alembic migration scripts.
- `tests/` backend test suite (API, services, models, integration).
- `scripts/` backend analysis/validation helper scripts.
- `pyproject.toml` Python dependencies, test and mypy settings.

## Control Panel Frontend (`control-panel/frontend`)
- `src/app/` Next.js App Router pages/layout/providers.
- `src/components/` domain UI and shared visual primitives (`ui/`).
- `src/lib/` API clients, WS manager, utility functions, query client.
- `cypress/` E2E tests and support utilities.
- `next.config.ts` runtime rewrites to backend API/WS.
- `orval.config.ts` OpenAPI client generation config.
- `package.json` frontend scripts + dependencies.

## Docker and Runtime Assets
- `docker/clawdevs-*` per-service Dockerfiles/config (openclaw, ollama, panel backend/frontend/worker, redis, postgres, searxng, token init).
- `docker/base/bootstrap-scripts/` OpenClaw bootstrap flow and config setup.
- `scripts/docker/up-all.sh` primary stack bring-up sequence.
- `scripts/docker/run-openclaw.sh` OpenClaw-specific startup and wiring.

## Docs and Planning
- `docs/architecture`, `docs/operations`, `docs/guides`, `docs/reference`.
- `.planning/` project planning state and generated analysis artifacts.
- `.planning/codebase/` current codebase mapping output set.

## Naming and Module Organization Notes
- Backend uses feature-oriented router/module names (`test_api/test_<feature>.py`, `app/api/<feature>.py`).
- Frontend uses route-segment naming aligned with UI sections (`src/app/<feature>/page.tsx`).
- Service classes/utilities are grouped by operational concern (health, sync, optimization, governance, memory).

