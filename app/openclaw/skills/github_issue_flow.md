---
name: github-issue-flow
description: "Create and synchronize runtime backlog items with GitHub Issues, preserving traceability between issue_id, title, summary, and priority."
---

# GitHub Issue Flow Skill

Ensure each runtime issue is mirrored in GitHub with deterministic metadata.

Checklist:
- Generate stable issue title and summary.
- Persist runtime issue payload in Redis before sync.
- Create GitHub issue idempotently and persist mapping keys.
- Publish handoff event only after state transition is recorded.
