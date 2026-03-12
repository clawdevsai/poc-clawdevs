# BOOT.md Template

Startup routine:
1. Confirm runtime context (issue_id, stream, run_id, trace_id).
2. Confirm role contract (profile, rules, skills, output schema).
3. Confirm gating constraints before acting (state machine, locks, budget).
4. Execute only allowed operations for this role.
5. Return structured output and handoff status.
