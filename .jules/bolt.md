# Bolt ⚡ Performance Journal

## 2026-04-04 - Optimized Session Synchronization Pattern
**Learning:** Periodic synchronization tasks that bridge filesystem-based runtimes (OpenClaw) and databases are prone to N+1 query bottlenecks and redundant disk I/O. Fetching metadata for all entities and performing a single batch database lookup via `IN` clauses significantly reduces latency. Additionally, comparing source timestamps (`updatedAt`) with database timestamps (`last_active_at`) before invoking expensive operations (like reading JSONL transcript files) provides massive speedups (60x in benchmarks) by skipping unchanged records.
**Action:** Always implement a "collect-batch-compare" pattern in sync services to minimize database round-trips and avoid redundant processing of immutable or unchanged historical data.
