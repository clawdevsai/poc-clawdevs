Expected output schema for CyberSec.

Return a concise JSON object with:
- `status`: `approved` or `blocked`
- `summary`: short security review conclusion
- `security_findings`: key vulnerabilities or hardening checks
- `decision`: `approve_for_merge` or `return_to_developer`
- `next_action`: `event:devops` when approved, otherwise `task:backlog`

