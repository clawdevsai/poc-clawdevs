Expected output schema for DBA.

Return a concise JSON object with:
- `status`: `approved` or `blocked`
- `summary`: short database review conclusion
- `db_risks`: key findings (migrations, indexes, locks, regressions)
- `decision`: `approve_for_merge` or `return_to_developer`
- `next_action`: `event:devops` when approved, otherwise `task:backlog`

