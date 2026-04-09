# Concerns Map

## Version Alignment Risks
- User requested `nextjs 16.2.2`; current frontend uses `next@16.2.0`.
- Tailwind already exists at `4.2.2`; upgrade path should avoid unnecessary churn.

## Template Integration Risks
- The Cruip Mosaic template may assume a fresh app structure and custom tokens.
- Existing layout contracts in `src/components/layout/*` may conflict with imported template shells.
- Direct copy-paste of template pages can break current route/navigation expectations.

## Styling and Theme Risks
- Existing styles in `src/app/globals.css` may collide with template globals.
- Utility class collisions are possible when merging old dashboard and new template markup.

## Data and Chart Risks
- Existing chart components in `src/components/dashboard/usage-chart.tsx` and `src/components/monitoring/*chart*.tsx` may use current data schemas not matching template demo mocks.
- Need to separate visual migration from API/data migration to reduce breakage.

## Repo Hygiene Risks
- Frontend contains nested `.git` and large generated folders (`.next`, `node_modules`) locally.
- Mapping and future commits should avoid generated artifacts.

## Security/Operational Risks
- Multiple `.env` files exist (`.env`, `.env.local`); avoid leaking values into docs/commits.
- Dockerized runtime and service dependencies mean frontend changes should still be verified via existing stack commands.

## Recommended Mitigation
- Phase work into: layout shell migration, chart/widget replacement, data binding hardening, regression tests.
- Keep API contracts stable in first pass; move quickly with visual parity first.
