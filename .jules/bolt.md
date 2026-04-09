## 2026-04-09 - [N+1 Query and Smart Sync in session_sync]
**Learning:** The `sync_sessions` service was performing an O(N) database query for every session in the loop, leading to significant latency. Additionally, it was redundantly reading and parsing transcript JSONL files on every sync, even if the session hadn't changed.
**Action:** Use batch fetching (single query per agent) to eliminate N+1 queries. Implement a 'Smart Sync' check by comparing the source `updatedAt` with the DB `last_active_at` to skip expensive filesystem and database operations for unchanged records.
