# Conventions Map

## Backend Conventions

## Framework and Routing
- FastAPI routers are split per domain and included centrally in `app/main.py`.
- Route prefixes/tags are explicit and feature-scoped.
- DI patterns rely on `Depends` + typed aliases for current/admin user contexts.

## Data and Persistence
- SQLModel models grouped under `app/models`.
- Async DB access through shared async session factory in `app/core/database.py`.
- Schema evolution is Alembic-first; startup can run migrations automatically.

## Configuration and Env
- Config is centralized in `Settings(BaseSettings)` (`app/core/config.py`).
- Environment naming convention uses `PANEL_` prefix (`model_config.env_prefix`).
- Feature toggles and thresholds live in settings (health monitor, semantic optimization, orchestration gating).

## Auth and Authorization
- JWT bearer auth validated in `app/api/deps.py`.
- Role-based guard (`require_admin`) and per-agent permissions (`AgentPermission`) are standard patterns.

## Error Handling and Logging
- Global exception handler returns consistent HTTP 500 payload.
- Service/startup flows use structured logging around bootstrap and failure points.

## Type and Quality Tooling
- Type hints are standard in backend modules.
- mypy enabled with SQLAlchemy plugin and strictness warnings (unused ignores, redundant casts, return-any).
- pytest config defines centralized test paths and async mode.

## Frontend Conventions

## App Structure
- Next.js App Router with route folder per feature.
- Shared app wrappers live in `layout.tsx` and `providers.tsx`.
- Domain components are separated from generic UI primitives.

## Data and API Access
- API access goes through a shared Axios instance and generated Orval client code.
- Auth token lifecycle:
  - attach bearer token on request,
  - clear token and redirect to `/login` on 401/403.
- API/WS base URL resolution uses environment-aware helper functions.

## Type and Build Discipline
- TypeScript strict mode enabled (`strict: true`).
- Path aliasing via `@/*` to `src/*`.
- ESLint configured with Next.js defaults.

## UI and Styling
- Tailwind CSS 4 with utility-first class composition.
- Reusable primitives under `components/ui`, domain widgets in feature folders.

## Testing Conventions
- Backend tests grouped by layer/domain (`tests/test_api`, `tests/test_models`, `tests/test_services`, `tests/integration`).
- Frontend E2E tests located under `cypress/e2e/*.cy.ts`.

## Repository Hygiene Notes
- Local runtime/tool caches (`.venv`, `.mypy_cache`, `.next`, node_modules) exist in working tree and should remain excluded from committed artifacts.

