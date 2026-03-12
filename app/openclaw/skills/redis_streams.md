---
name: redis-streams
description: "Operate Redis stream transitions with consistent envelope metadata (run_id, trace_id, attempt) and deterministic state movement."
---

# Redis Streams Skill

Preserve event contract quality across pipeline stages.

Checklist:
- Keep `issue_id`, `run_id`, `trace_id`, and `attempt`.
- Ack only after successful role outcome handling.
- Requeue or fallback using explicit reason fields.
- Ensure stream name and issue state remain aligned.
