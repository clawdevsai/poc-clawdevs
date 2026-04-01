# BOLT'S JOURNAL - CRITICAL LEARNINGS ONLY

## 2024-05-22 - [Optimizing Background Synchronization Loops]
**Learning:** Background synchronization services (like `sync_sessions`) called frequently by the dashboard can easily become bottlenecks due to N+1 queries and redundant Disk I/O if they process all records every time.
**Action:** Always implement a "smart sync" pattern: (1) Batch fetch all existing records into a lookup map at the start. (2) Use timestamp comparisons (e.g., `updatedAt` vs `last_active_at`) to skip expensive processing like file parsing or message counting for unchanged records.
