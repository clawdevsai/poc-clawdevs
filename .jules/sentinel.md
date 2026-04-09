## 2026-04-08 - BFLA in Administrative Sync and Missing Auth in Sub-Routers

**Vulnerability:** Several administrative and information-gathering endpoints were exposed without authentication or with insufficient authorization (BFLA). Specifically, the `sync_agents_admin` endpoint was accessible to any authenticated user, and entire routers for health, governance, and RAG were public.

**Learning:** When using FastAPI `APIRouter`, it's easy to assume that if the router is included in `main.py`, it inherits global dependencies. However, if dependencies are not explicitly added to the router or the individual endpoints, they remain public. Furthermore, endpoints that trigger system-wide state changes (like syncing) must be strictly gated with `AdminUser`.

**Prevention:**
1. Always verify the `dependencies` argument in `APIRouter` or `app.include_router`.
2. Audit all POST/PATCH/DELETE endpoints for Broken Function Level Authorization (BFLA).
3. Use a dedicated security audit test suite (`test_security_audit.py`) that specifically checks for `401` and `403` responses on all sensitive paths.
