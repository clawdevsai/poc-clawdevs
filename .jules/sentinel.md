## 2026-03-31 - [Broken Function Level Authorization]
**Vulnerability:** Administrative and infrastructure endpoints were using 'CurrentUser' instead of 'AdminUser', allowing any authenticated user to trigger syncs, modify repositories, or view cluster info.
**Learning:** Sensitive global operations were missing role-based checks beyond simple authentication.
**Prevention:** Use 'AdminUser' dependency for any endpoint that modifies global state or exposes infrastructure details.
