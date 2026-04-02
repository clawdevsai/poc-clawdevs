## 2025-05-15 - [Missing Authentication on Sensitive Endpoints]
**Vulnerability:** Multiple API endpoints (`/agents`, `/api/health/summary`, `/api/health/tasks/{id}`, `/api/health/failures`, `/api/health/escalations`) were exposed without any authentication requirements, potentially leaking system status, agent details, and task failures to unauthenticated users.
**Learning:** Inconsistency in applying `CurrentUser` dependency during rapid feature development can lead to security gaps, especially when some routers have prefixes and others don't.
**Prevention:** Always verify that every new API endpoint or router inclusion in `main.py` has an appropriate authentication/authorization dependency. Add automated security tests to check for `401 Unauthorized` on all sensitive paths.
