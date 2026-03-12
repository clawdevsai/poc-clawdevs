# AGENTS.md Template

Agent runtime checklist:
- Read current objective, constraints, and available tools.
- Validate expected input and output contract for the current role.
- Use minimal toolset required for the task.
- Emit status transitions that are traceable in pipeline events.
- On failure, report root cause and safe fallback path.

Coordination:
- Keep role boundaries clear.
- Do not claim ownership of steps outside assigned role.
- Handoff only when artifacts are complete enough for the next role.
