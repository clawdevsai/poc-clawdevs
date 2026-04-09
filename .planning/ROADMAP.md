# Roadmap: ClawDevs AI Panel UI Modernization (Mosaic)

## Overview

This roadmap modernizes the existing control-panel frontend in incremental phases: first stabilize runtime and styling foundations, then migrate shell and dashboard UX to Mosaic-aligned patterns, and finally validate feature compatibility and rollout safety.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions when needed

- [x] **Phase 1: Runtime and Tailwind Baseline** - Upgrade runtime and lock styling foundation
- [ ] **Phase 2: Shell and Layout Migration** - Apply Mosaic layout patterns to global app chrome
- [ ] **Phase 3: Dashboard and Chart Modernization** - Migrate dashboard visuals and chart presentation
- [ ] **Phase 4: Compatibility and Rollout Hardening** - Preserve existing workflows and validate end-to-end behavior

## Phase Details

### Phase 1: Runtime and Tailwind Baseline
**Goal**: Establish stable technical baseline before visual migration
**Depends on**: Nothing (first phase)
**Requirements**: [PLAT-01, PLAT-02, QUAL-02]
**Success Criteria** (what must be TRUE):
1. Frontend builds and starts on `next@16.2.2` without regressions
2. Tailwind v4 utility pipeline works consistently in current app
3. Type-check and production build pass after baseline updates
**Plans**: 3 plans

Plans:
- [x] 01-01: Upgrade Next.js and aligned frontend dependencies safely
- [x] 01-02: Verify and normalize Tailwind/PostCSS setup against official guidance
- [x] 01-03: Run baseline quality checks (`type-check`, `build`) and fix breakages

### Phase 2: Shell and Layout Migration
**Goal**: Migrate shared application shell to Mosaic-style structure
**Depends on**: Phase 1
**Requirements**: [PLAT-03, UI-01, UI-02, UI-03]
**Success Criteria** (what must be TRUE):
1. Sidebar/header/content shell reflects target dashboard template style
2. Core routes remain reachable and usable from the updated navigation
3. Core layout is responsive across desktop and mobile breakpoints
**Plans**: 3 plans

Plans:
- [x] 02-01: Rework global app shell components (`layout`, `sidebar`, `header`)
- [x] 02-02: Align common UI primitives (cards/tables/badges/buttons/forms)
- [x] 02-03: Validate route navigation and responsive behavior after shell migration

### Phase 3: Dashboard and Chart Modernization
**Goal**: Modernize dashboard sections and chart experience with template consistency
**Depends on**: Phase 2
**Requirements**: [DASH-01, DASH-02, DASH-03]
**Success Criteria** (what must be TRUE):
1. Home dashboard uses Mosaic-like sections for KPI/stat/activity blocks
2. Chart widgets follow template-consistent styling and interaction patterns
3. Charts continue rendering real project data (not static demo-only output)
**Plans**: 3 plans

Plans:
- [x] 03-01: Refactor dashboard composition to template-inspired sections
- [x] 03-02: Adapt existing chart components to new visual contracts
- [x] 03-03: Validate metric/data bindings across dashboard and monitoring surfaces

### Phase 4: Compatibility and Rollout Hardening
**Goal**: Ensure no functional regressions and confidence to ship
**Depends on**: Phase 3
**Requirements**: [COMP-01, COMP-02, COMP-03, QUAL-01]
**Success Criteria** (what must be TRUE):
1. Existing feature pages remain functional under migrated shell/UI
2. Authentication/session behavior remains stable from user perspective
3. Cypress smoke path verifies login and dashboard navigation
4. No backend API contract change is required for migrated frontend flows
**Plans**: 3 plans

Plans:
- [ ] 04-01: Validate route-level feature compatibility (chat/tasks/sessions/monitoring/etc.)
- [ ] 04-02: Add or adjust Cypress smoke coverage for migrated entry flows
- [ ] 04-03: Final regression pass and release readiness checklist

## Progress

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 1. Runtime and Tailwind Baseline | 3/3 | Complete | 2026-04-07 |
| 2. Shell and Layout Migration | 0/3 | Not started | - |
| 3. Dashboard and Chart Modernization | 0/3 | Not started | - |
| 4. Compatibility and Rollout Hardening | 0/3 | Not started | - |
