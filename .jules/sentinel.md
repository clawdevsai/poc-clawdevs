## 2025-04-06 - [BFLA] Missing Authentication in Governance API
**Vulnerability:** The entire Governance API (policy validation, cost tracking, spending data) was publicly accessible without any authentication or authorization.
**Learning:** Router-level dependencies in FastAPI are the most effective way to ensure a consistent security posture across a large number of related endpoints.
**Prevention:** Always audit new API routers for missing authentication dependencies. Use `dependencies=[Depends(require_admin)]` or similar at the `APIRouter` level for administrative modules.
