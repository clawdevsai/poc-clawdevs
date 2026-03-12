Expected output schema for Architect-review.

Return a concise JSON object with:
- `status`: `approved` or `blocked`
- `summary`: short final decision rationale
- `decision`: `approve_merge` or `request_final_correction`
- `next_action`: `event:devops` when approved, otherwise `task:backlog`

