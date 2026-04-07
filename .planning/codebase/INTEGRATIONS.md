# Integrations Map

## Internal Service Integrations

## Frontend -> Backend API
- Frontend routes API traffic through Next rewrites:
  - `/api/:path*` -> `http://clawdevs-panel-backend:8000/:path*`
  - `/api/ws/:path*` -> `http://clawdevs-panel-backend:8000/ws/:path*`
- Browser clients default to same-origin `/api` (see `src/lib/api-base-url.ts`).
- Axios client injects `Authorization: Bearer <panel_token>` from localStorage.

## Frontend -> Backend WebSockets
- `src/lib/ws.ts` connects to `/ws/<channel>` (`dashboard`, `agents`, `approvals`, `cluster`, `crons`, `context-mode-metrics`).
- Auth token is sent in the first frame (`{type:"auth", token}`), not query params.

## Backend -> Data Stores
- PostgreSQL via `PANEL_DATABASE_URL` / `database_url` (async SQLModel engine).
- Redis via `PANEL_REDIS_URL` / `redis_url` (queue/cache related services and workers).
- Alembic migrations run at backend startup (`run_migrations()`).

## Backend -> OpenClaw Gateway
- Backend uses `PANEL_OPENCLAW_GATEWAY_URL` (default `http://openclaw:18789`) and token envs.
- Endpoints/services include sessions/tasks/chat/governance/context-mode flows that depend on OpenClaw state.

## Backend/OpenClaw -> Ollama
- OpenClaw container receives `OLLAMA_BASE_URL=http://ollama:11434`.
- Backend settings include `ollama_base_url` and semantic optimization flags.

## Search Integration
- SearXNG + SearXNG Proxy are first-class stack services.
- Proxy URL exposed by env defaults: `SEARXNG_BASE_URL=http://searxng-proxy:18080`.

## Worker Integration
- Panel worker container runs on same network and shares:
  - DB URL to postgres
  - Redis URL to redis
  - read-only OpenClaw data volume (`/data/openclaw:ro`)
- Used for background jobs and sync/orchestration tasks.

## Token Bootstrap Integration
- `clawdevs-token-init` waits for backend health and writes panel token material into shared `panel-token` volume.
- OpenClaw mounts `panel-token` read-only.

## External Integrations

## GitHub
- Env variables used: `GIT_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN`, `GIT_ORG`.
- Available to backend and worker containers; supports repository/task workflows.

## Telegram
- OpenClaw receives `TELEGRAM_BOT_TOKEN_CEO` and `TELEGRAM_CHAT_ID`.

## OpenRouter (Optional)
- Supported via `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`.
- Active only when provider is configured (`PROVEDOR_LLM` switch).

## Security and Auth Boundaries
- Panel auth uses JWT with backend verification in FastAPI dependencies (`get_current_user`, `require_admin`, agent permission checks).
- CORS allowed origins default to local frontend and container frontend hosts.
- OpenClaw gateway token and panel JWT are separate credentials.

