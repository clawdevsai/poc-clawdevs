# Structure Map

## Repository Root
- `README.md` project-level operational instructions
- `Makefile` main workflow commands
- `docker/` service images and deployment plumbing
- `scripts/` automation/support scripts
- `control-panel/` product source

## Product Modules
- `control-panel/frontend`
  - `src/app` Next routes (e.g., `page.tsx`, `monitoring/page.tsx`, `tasks/page.tsx`)
  - `src/components` domain UI components
  - `src/lib` shared API/client helpers
  - `cypress/` e2e tests and fixtures
  - `next.config.ts`, `postcss.config.mjs`, `package.json`
- `control-panel/backend`
  - `app/api` FastAPI routers
  - `app/core` application core
  - `tests/` API/service/integration tests
  - `migrations/` Alembic migration files
  - `pyproject.toml`

## Frontend Domain Examples
- Dashboard: `src/components/dashboard/*`
- Monitoring: `src/components/monitoring/*`
- Layout/shell: `src/components/layout/*`
- Auth/entry route: `src/app/login/page.tsx`

## Backend Domain Examples
- Auth: `app/api/auth.py`
- Sessions/tasks/chat: `app/api/sessions.py`, `app/api/tasks.py`, `app/api/chat.py`
- Metrics/health: `app/api/metrics.py`, `app/api/health.py`
- Context mode features: `app/api/context_mode*.py`

## Mapping Scope for Upcoming Phase
- Primary integration surface for Tailwind dashboard template:
  - `control-panel/frontend/src/app`
  - `control-panel/frontend/src/components/dashboard`
  - Shared style and shell files (`globals.css`, layout components)
