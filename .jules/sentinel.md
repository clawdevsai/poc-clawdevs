## 2026-04-03 - Administrative Endpoints Missing Authorization
**Vulnerability:** Several administrative endpoints (infrastructure management, repository modification, manual cron triggers) were accessible to any authenticated user, not just admins.
**Learning:** FastAPI routes were using the `CurrentUser` dependency for endpoints that perform sensitive or global operations, leading to Broken Function Level Authorization (BFLA).
**Prevention:** Always use the `AdminUser` dependency for endpoints that expose infrastructure details (cluster info), trigger system-wide syncs (agent sync), or modify global resources (repositories, crons).
