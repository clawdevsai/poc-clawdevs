## 2026-04-03 - Optimize session synchronization (Smart Sync)
**Learning:** The session synchronization service was performing O(N) database queries (N+1 problem) and O(N) file I/O operations (reading transcript files to count messages) on every sync, even for unchanged sessions.
**Action:** Implemented a batch fetch for all existing sessions at the start of the sync and added a timestamp-based check to skip redundant file processing for unchanged records.
