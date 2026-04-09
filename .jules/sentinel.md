## 2025-04-05 - Missing Authentication on Sensitive Endpoints
**Vulnerability:** Several sensitive API endpoints in `governance.py`, `health.py`, and `agents.py` were missing authentication/authorization dependencies, allowing unauthenticated access to system health, failure logs, and governance rules.
**Learning:** Endpoints added during rapid development cycles (like governance and health monitoring) can easily be overlooked when applying global security policies if they are not explicitly grouped or audited.
**Prevention:** Always verify that every new router and endpoint includes at least `CurrentUser` or `AdminUser` dependencies. Use automated integration tests to assert `401 Unauthorized` on all endpoints without a `panel_token`.
