# Stack Map

## Overview
ClawDevs AI is a Docker-orchestrated local platform that combines OpenClaw agent orchestration, Ollama local LLM inference, SearXNG search, and a Control Panel (FastAPI backend + Next.js frontend).

## Runtime Layers
- Container/runtime: Docker (driven by `Makefile` + `scripts/docker/*.sh`), custom network `clawdevs`.
- Orchestration style: imperative `docker run` scripts (`up-all.sh`, `run-openclaw.sh`), not `docker-compose`.
- Main services: PostgreSQL, Redis, Ollama, SearXNG, SearXNG Proxy, Panel Backend, Panel Worker, Panel Frontend, Token Init, OpenClaw.

## Backend Stack (`control-panel/backend`)
- Language/runtime: Python `>=3.12,<4.0`.
- Web/API: FastAPI, Uvicorn.
- Data/ORM: SQLModel + SQLAlchemy async, Alembic migrations, PostgreSQL (`asyncpg`, `psycopg[binary]`), `pgvector`.
- Queue/background: Redis, `rq`, `rq-scheduler`.
- Streaming/realtime: `sse-starlette`, WebSocket endpoints.
- Config/auth: `pydantic-settings`, JWT (`pyjwt[crypto]`), `passlib[bcrypt]`.
- Integration clients: `httpx`, `aiohttp`, `kubernetes`.
- Backend tooling: pytest/pytest-asyncio/pytest-cov, mypy, Alembic.

## Frontend Stack (`control-panel/frontend`)
- Language/runtime: TypeScript + React 19 + Next.js 16 (App Router).
- UI/tooling: Tailwind CSS 4, Radix UI primitives, class-variance-authority, lucide-react, recharts.
- Data/state: TanStack Query, Axios, React Table.
- API client generation: Orval (OpenAPI -> React Query client with custom Axios mutator).
- Build/lint: Next build pipeline, ESLint 9 (`eslint-config-next`), strict TypeScript.
- E2E testing: Cypress.

## AI/Agent Stack
- OpenClaw gateway container (`clawdevs-openclaw`) as orchestration/control plane for agents.
- Ollama container (`clawdevs-ollama`) for local inference; default semantic model in panel settings uses `phi4-mini-reasoning:latest`.
- Optional external LLM provider path via OpenRouter variables.

## Infra and Ops Tooling
- Build/release entrypoint: root `Makefile`.
- Image build contexts:
  - Backend: `docker/clawdevs-panel-backend/Dockerfile` from `control-panel/backend`.
  - Frontend: `docker/clawdevs-panel-frontend/Dockerfile` from `control-panel/frontend`.
  - OpenClaw and supporting services under `docker/`.
- Volumes: `openclaw-data`, `ollama-data`, `postgres-data`, `panel-token`.
- CI/workflows: `.github/workflows/*` for deployment validation and monitoring tasks.

