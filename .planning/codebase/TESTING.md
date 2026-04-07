# Testing Map

## Backend Testing

## Framework and Setup
- Primary framework: `pytest` (+ `pytest-asyncio`, `pytest-cov`).
- Config source: `control-panel/backend/pyproject.toml`.
- Async test mode is enabled (`asyncio_mode = "auto"`).

## Test Suite Organization
- API endpoint tests: `tests/test_api/test_*.py` (auth, tasks, sessions, metrics, memory, chat, ws, settings, crons, etc.).
- Core tests: `tests/test_core/*` (config/auth/database/main).
- Service tests: `tests/test_services/*` (sync, orchestration, container/openclaw clients, failure detection, retrieval).
- Model tests: `tests/test_models/*`.
- Integration tests: `tests/integration/*` (autonomy full flow, failure/escalation).

## Backend Coverage Characteristics
- Broad domain coverage across transport, service, and model layers.
- Specialized tests exist for semantic optimization, context metrics, and parallelism gate.
- Helper scripts for test/coverage auditing are present under `control-panel/backend/scripts/`.

## Frontend Testing

## Framework and Setup
- Primary framework: Cypress (`cypress.config.ts`).
- Base URL: `http://localhost:3000`.
- Spec pattern: `cypress/e2e/**/*.cy.ts`.
- Retries enabled in run mode.

## Current E2E Specs Identified
- `control-panel/frontend/cypress/e2e/login.cy.ts`
- `control-panel/frontend/cypress/e2e/chat.cy.ts`

## Frontend Coverage Characteristics
- Current E2E scope confirms critical auth and chat paths.
- No large unit/component test suite was observed in `src/` test file patterns; quality signal is currently weighted toward E2E + TypeScript strictness + lint.

## End-to-End System Validation
- Stack-level health behavior is operationally validated by startup scripts (`wait_for_health` and `wait_for_running`) and service health checks in Docker runs.
- `make` commands and docs indicate regular workflow around backend migrations, panel health, and OpenClaw integration.

## Testing Gaps to Watch
- Frontend feature breadth currently exceeds observed Cypress coverage count (many pages/components vs few E2E specs).
- Realtime flows (WS channels and monitoring panels) likely need additional deterministic E2E scenarios.
- Cross-container contract tests (frontend rewrite -> backend -> openclaw) should be kept explicit due multi-service coupling.

