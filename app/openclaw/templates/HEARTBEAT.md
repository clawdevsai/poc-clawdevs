# HEARTBEAT.md Template

Heartbeat behavior:
- If there is no actionable work, report `HEARTBEAT_OK`.
- Do not revive stale tasks without new trigger.
- For active work, report only current state, blocker, and next check.
- Keep heartbeat output short and deterministic.
