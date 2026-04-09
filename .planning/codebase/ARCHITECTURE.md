# Architecture Map

## High-Level Shape
- Multi-service repository with a control panel product split into:
  - Frontend app: `control-panel/frontend`
  - Backend API/service: `control-panel/backend`
- Operational infrastructure and build assets live in `docker/` and root scripts.

## Frontend Architecture
- Next.js App Router with route-per-feature structure in `src/app`.
- Shared UI elements in `src/components/ui`.
- Feature components grouped by domain in `src/components/{dashboard,monitoring,approvals,...}`.
- App shell/layout composition in:
  - `src/app/layout.tsx`
  - `src/components/layout/app-layout.tsx`
  - `src/components/layout/sidebar.tsx`
  - `src/components/layout/header.tsx`
- Data access concentrated under `src/lib/*`.

## Backend Architecture
- FastAPI service with module-per-domain routers under `app/api`.
- Core/config/service logic under `app/core` and `app/services` (by convention from tree).
- Entrypoint is expected in `app/main.py` (`__pycache__/main.cpython-312.pyc` confirms).
- Migrations directory present: `control-panel/backend/migrations`.

## Data and Flow
- Frontend server routes forward/proxy requests to backend/openclaw endpoints.
- Backend exposes REST and websocket-style endpoints for sessions, chat, tasks, and monitoring.
- Redis/RQ pair supports asynchronous execution paths.

## Implication for Dashboard Template Migration
- Landing/dashboard area likely centered on:
  - `src/app/page.tsx`
  - `src/components/dashboard/*`
- Existing monitoring charts (`src/components/monitoring/*chart*.tsx`) suggest chart abstractions already present.
