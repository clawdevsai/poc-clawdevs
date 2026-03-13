# Delegate To PO

Use this skill when the user asks for execution planning, backlog shaping, prioritization, scope definition, acceptance criteria, or delivery tracking.

Workflow:
1. Summarize the user's request in business terms.
2. Build a short operational brief:
   - objective
   - desired outcome
   - constraints
   - deadline
   - references collected by the CEO
   - relevant links or files
3. Tell the PO to write the deliverables inside `/data/openclaw/backlog`.
4. Use `sessions_spawn` with `agentId: "po"` for a new thread or `sessions_send` for a follow-up.
5. After the PO completes, read the generated files and rewrite the result for the stakeholder.
