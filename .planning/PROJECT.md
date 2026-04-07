# ClawDevs AI Panel UI Modernization (Mosaic)

## What This Is

This project modernizes the existing `control-panel/frontend` experience in a brownfield codebase. The goal is to adopt the visual/system patterns from Cruip's Tailwind dashboard template (Mosaic) while preserving current application capabilities, routes, and backend integrations.

The current panel already runs on Next.js App Router, Tailwind CSS v4, and chart components; this initiative upgrades visual consistency and dashboard UX without changing the product domain.

## Core Value

Operators can monitor and manage AI workflows quickly from a consistent, fast, and reliable dashboard interface without losing existing functionality.

## Requirements

### Validated

- ✓ Multi-route operational panel exists and is actively used (`agents`, `chat`, `sessions`, `tasks`, `monitoring`, `settings`) — baseline from existing codebase
- ✓ Next.js + Tailwind + React stack is established and deployable in current environment
- ✓ Chart-driven monitoring UI already exists (dashboard and monitoring components)

### Active

- [ ] Upgrade frontend from `next@16.2.0` to `next@16.2.2` with no route regressions
- [ ] Keep Tailwind CSS aligned with `v4.2.x` and official setup for Next.js
- [ ] Integrate Mosaic-inspired dashboard shell (sidebar/header/cards/tables/forms) into current app layout
- [ ] Replace or adapt current dashboard and monitoring visual blocks with template-consistent components
- [ ] Integrate chart patterns from the dashboard template while preserving current business metrics/data sources
- [ ] Ensure responsive behavior (desktop/mobile) and preserve current auth/session UX flows

### Out of Scope

- Backend API redesign or data-model changes — this initiative is frontend/UI focused
- Introducing new product modules unrelated to dashboard modernization
- Migrating away from Next.js App Router or replacing current frontend framework

## Context

- Repository root: `C:/Users/Administrator/Workspace/lukeware/clawdevs-ai`
- Frontend target: `control-panel/frontend`
- Current frontend stack includes `next@16.2.0`, `tailwindcss@4.2.2`, `@tailwindcss/postcss@4.2.2`, `recharts`
- Existing dashboard and monitoring components are in:
  - `control-panel/frontend/src/components/dashboard`
  - `control-panel/frontend/src/components/monitoring`
- Existing layout composition is in:
  - `control-panel/frontend/src/components/layout`
  - `control-panel/frontend/src/app/layout.tsx`
- Codebase map was generated before initialization under `.planning/codebase/`

## Constraints

- **Tech Stack**: Keep Next.js + React + Tailwind 4.x and existing frontend architecture
- **Compatibility**: Preserve current route map and backend API contracts
- **Quality**: Avoid regressions in existing task/chat/session/monitoring flows
- **Security**: No secret leakage from `.env` or runtime configs during migration
- **Incremental Delivery**: Execute in phased steps to keep deployability throughout

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use Cruip Mosaic as UI baseline for dashboard modernization | User requested explicit alignment with template and demo look-and-feel | — Pending |
| Keep migration inside existing `control-panel/frontend` app | Brownfield system already has routes, auth, and integrations to preserve | — Pending |
| Maintain Tailwind v4 approach and adapt template patterns to current component boundaries | Reduces rewrite risk and keeps existing design/runtime stack | — Pending |
| Upgrade Next.js to `16.2.2` as part of modernization scope | Matches requested runtime target and keeps dependency baseline explicit | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check -> still the right priority?
3. Audit Out of Scope -> reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-07 after initialization*
