# Phase 04 Regression Checklist (Plan 04-03)

Date: 2026-04-09  
Owner: Codex executor  
Scope: Final compatibility closure for migrated login/dashboard/monitoring flows

## Gate 5A - Automated Checks

| Gate | Command | Expected | Status | Evidence |
| --- | --- | --- | --- | --- |
| 5A-01 | `pnpm typecheck` | TypeScript without errors | PASS | `tsc --noEmit` completed (0 errors) |
| 5A-02 | `pnpm build` | Production build succeeds | PASS | `next build` completed; static/dynamic routes generated |
| 5A-03 | `pnpm cy:run --spec cypress/e2e/login.cy.ts` | Login/session smoke green | PASS | 13 passing, 0 failing |
| 5A-04 | `pnpm cy:run --spec cypress/e2e/navigation-shell.cy.ts` | Shell navigation smoke green | PASS | 2 passing, 0 failing |
| 5A-05 | `pnpm cy:run --spec cypress/e2e/dashboard-data-bindings.cy.ts` | Dashboard/monitoring bindings smoke green | PASS | 2 passing, 0 failing |

## Manual Short Checklist (Login/Dashboard/Monitoring)

| Area | Validation Criteria | Status | Evidence |
| --- | --- | --- | --- |
| Login | Successful login stores `panel_token`; invalid credentials show error; protected page 401/403 clears session and redirects to `/login` | PENDING HUMAN CHECK | Automated parity covered by `login.cy.ts`; manual UX confirmation pending |
| Dashboard | KPI cards render with live bindings and no layout break in desktop/mobile | PENDING HUMAN CHECK | Automated parity covered by `dashboard-data-bindings.cy.ts` + `navigation-shell.cy.ts`; manual visual confirmation pending |
| Monitoring | `/monitoring` navigation works from shell and core telemetry cards/charts load | PENDING HUMAN CHECK | Automated parity covered by `navigation-shell.cy.ts` + `dashboard-data-bindings.cy.ts`; manual visual confirmation pending |

## Backend Contract Preservation Checklist

- [x] No new backend endpoint required for migrated flows.
- [x] No new required request payload field introduced by frontend changes.
- [x] Existing contract remains: `/auth/login`, `/agents`, `/approvals`, `/sessions`, `/tasks`, `/activity-events`, `/metrics*`, `/api/health/*`.
- [x] Compatibility confirmed by route wiring:
  - frontend client calls reviewed in `src/lib/monitoring-api.ts` and `src/app/page.tsx`
  - backend routers confirmed in `backend/app/main.py` and `backend/app/api/health.py`

## Notes

- One flake in mobile sidebar visibility was auto-fixed in `navigation-shell.cy.ts` by targeting visible links and scrolling before click.
- Cypress warning about `allowCypressEnv` remains out of scope for this plan and is tracked as residual risk.
