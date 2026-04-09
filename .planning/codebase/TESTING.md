# Testing Map

## Frontend Testing
- E2E framework: Cypress
- Config: `control-panel/frontend/cypress.config.ts`
- Specs:
  - `control-panel/frontend/cypress/e2e/chat.cy.ts`
  - `control-panel/frontend/cypress/e2e/login.cy.ts`
- Fixtures:
  - `control-panel/frontend/cypress/fixtures/agents.json`
  - `control-panel/frontend/cypress/fixtures/chat-history.json`
  - `control-panel/frontend/cypress/fixtures/login.json`
  - `control-panel/frontend/cypress/fixtures/sessions.json`

## Backend Testing
- Framework: `pytest` (+ `pytest-asyncio`, `pytest-cov`)
- Root config in `control-panel/backend/pyproject.toml` (`testpaths = ["tests"]`)
- Test folders:
  - `control-panel/backend/tests/test_api`
  - `control-panel/backend/tests/services`
  - `control-panel/backend/tests/integration`

## Notable Backend Coverage Areas (by filename)
- Auth: `test_auth_endpoints.py`
- Chat/tasks/sessions: `test_chat.py`, `test_tasks.py`, `test_agents_sessions.py`
- Monitoring and health: `test_cluster_health.py`, `test_metrics.py`
- Context mode: `test_context_mode_semantic_optimization.py`
- End-to-end workflows: integration tests under `tests/integration`

## Practical Validation for Dashboard Migration
- Frontend:
  - Add/adjust Cypress smoke checks for dashboard render and navigation.
- Backend:
  - No immediate API contract changes expected if migration is visual-only.
  - If new widgets call new endpoints, extend `tests/test_api/*` accordingly.
