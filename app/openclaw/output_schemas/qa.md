Expected output schema for QA.

Return a concise JSON object with:
- `status`: `approved` or `blocked`
- `summary`: short QA conclusion
- `verification`: checks executed and evidence
- `decision`: `approve_for_devops` or `return_to_developer`
- `next_action`: `event:devops` when approved, otherwise `task:backlog`
