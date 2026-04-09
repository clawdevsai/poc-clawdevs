# Conventions Map

## Frontend Conventions
- TypeScript-first React codebase in `control-panel/frontend/src`.
- App Router pages in `src/app/**/page.tsx`.
- Shared UI atoms in `src/components/ui/*`.
- Domain grouping pattern in `src/components/{dashboard,monitoring,approvals,...}`.
- Utility helpers centralized in `src/lib`.
- Styling stack assumes Tailwind utility classes plus helper libs (`clsx`, `tailwind-merge`).

## Backend Conventions
- Router modules segmented by capability in `control-panel/backend/app/api/*.py`.
- Test module naming follows `test_*.py` under `control-panel/backend/tests`.
- Async endpoints and service logic aligned with FastAPI + AnyIO stack.
- Migrations managed in `control-panel/backend/migrations`.

## Naming and Organization Patterns
- Feature-based naming for page routes (`chat`, `tasks`, `sessions`, `monitoring`).
- UI component names are descriptive and usually noun-based (`stats-card.tsx`, `usage-chart.tsx`).
- API files map 1:1 to domain concepts (`approvals.py`, `repositories.py`, `settings.py`).

## Tooling and Quality Hints
- Frontend scripts emphasize type-safety (`npm/pnpm run lint` wired to `tsc --noEmit`).
- Backend typing checks indicated by mypy cache and config in `pyproject.toml`.
- Cypress and pytest are both present and already used.

## Migration-Specific Convention Guidance
- Reuse existing route/component boundaries instead of collapsing everything into one page.
- Keep chart data plumbing consistent with existing abstractions in `src/components/dashboard` and `src/components/monitoring`.
- Preserve `src/components/layout/*` composition contracts while replacing visuals.
