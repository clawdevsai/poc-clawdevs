# Stack Map

## Monorepo Context
- Root workspace: `C:/Users/Administrator/Workspace/lukeware/clawdevs-ai`
- Main product modules: `control-panel/frontend` and `control-panel/backend`
- Infra and runtime orchestration: `docker/` plus root `Makefile`

## Frontend Stack
- Framework: `next@16.2.0` with App Router (`control-panel/frontend/src/app`)
- React: `react@19.2.4`, `react-dom@19.2.4`
- Language/tooling: TypeScript (`tsconfig.json`), ESLint (`eslint-config-next`)
- Styling: `tailwindcss@4.2.2`, `@tailwindcss/postcss@4.2.2`, `postcss@8.5.3`
- UI primitives: Radix packages (`@radix-ui/*`), `shadcn`, `lucide-react`
- Data/UI libs: `@tanstack/react-query`, `@tanstack/react-table`, `recharts`
- Networking: `axios`
- E2E tests: Cypress (`cypress.config.ts`, `cypress/e2e/*.cy.ts`)

## Backend Stack
- Runtime: Python `>=3.12,<4.0` (see `control-panel/backend/pyproject.toml`)
- API: FastAPI (`fastapi==0.135.1`), ASGI server `uvicorn[standard]==0.34.0`
- ORM/data: `sqlmodel`, `alembic`, `asyncpg`, `psycopg`, `pgvector`
- Queue/cache: `redis[hiredis]`, `rq`, `rq-scheduler`
- Auth/security helpers: `passlib[bcrypt]`, `pyjwt[crypto]`
- Async/HTTP: `httpx`, `aiohttp`, `anyio`, `trio`
- Test tooling: `pytest`, `pytest-asyncio`, `pytest-cov`

## Build and Delivery
- Docker images under `docker/clawdevs-*`
- Orchestration commands via root `Makefile`
- Frontend container build file: `control-panel/frontend/Dockerfile`
- Backend container build file: `docker/clawdevs-panel-backend/Dockerfile`

## Notes for Requested Work
- Tailwind v4 is already present in frontend dependencies.
- Current Next version is `16.2.0`; user target mentions `16.2.2`.
