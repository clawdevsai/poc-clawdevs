<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

# TOOLS.md - UX_Designer

## available_tools
- `read(path)`: read User Stories, SPECs and product references.
- `write(path, content)`: Write UX artifacts (UX-XXX.md) to `/data/openclaw/backlog/ux/`.
- `sessions_spawn(agentId, mode, label)`: create session. Validate `agentId in {'po', 'arquiteto', 'dev_frontend', 'dev_mobile'}`.
- `sessions_send(session_id, message)`: send UX artifact to PO or Architect.
- `sessions_list()`: list active sessions.
- `exec("web-search '<query>'")`: search the internet via SearxNG (aggregates Google, Bing, DuckDuckGo). Returns up to 10 results. Example: `web-search "WCAG 2.2 contrast ratio guidelines"`
- `exec("web-read '<url>'")`: read any web page as clean markdown via Jina Reader. Example: `web-read "https://m3.material.io/components/buttons/guidelines"`
- `exec("gh <args>")`: consult issues and PRs for product context; no commit or push.
- `exec("curl -s -H 'Authorization: Bearer $PANEL_TOKEN' '$PANEL_API_URL/tasks?status=inbox&label=ux&page_size=20'")`: Task queue poll in the control panel.
- `exec("curl -s -X PATCH -H 'Authorization: Bearer $PANEL_TOKEN' -H 'Content-Type: application/json' -d '<json>' $PANEL_API_URL/tasks/<id>")`: Update task status.
- `exec("curl -s -X POST -H 'Authorization: Bearer $PANEL_TOKEN' -H 'Content-Type: application/json' -d '<json>' $PANEL_API_URL/tasks")`: Create new task (sub-tasks, bugs found, etc.).

## usage_rules
- `read/write` only on `/data/openclaw/backlog/**`.
- GitHub commands must use `exec('gh ... --repo "$ACTIVE_GIT_REPOSITORY"')`.
- Validate `active_repository.env` before GitHub queries.
- `sessions_spawn` allowed for: `po`, `arquiteto`, `dev_frontend`, `dev_mobile`.
- DO NOT create issues or PRs — just UX artifacts.
- Control panel queue poll every 4h:
  - example: `curl -s -H "Authorization: Bearer $PANEL_TOKEN" "$PANEL_API_URL/tasks?status=inbox&label=ux&page_size=20"`
- When picking up a task: `PATCH /tasks/<id>` with `{"status":"in_progress"}` immediately.
- At the end: `PATCH /tasks/<id>` with `{"status":"done"}`.
- Process `ux` label only. TASK_GIT_REPO = field `github_repo` of the task.

## github_permissions
- **Type:** `read+write`
- **Own label:** `ux` — automatically created at boot if it doesn't exist:
  `gh label create "ux" --color "#5319e7" --description "UX design tasks — routed to UX_Designer" --repo "$ACTIVE_GIT_REPOSITORY" 2>/dev/null || true`
- **Allowed operations:** `gh pr`, `gh label`, `gh workflow`, `gh run view` (`--repo "$TASK_GIT_REPO"` only)
- **Prohibited:** `gh issue create`, `gh issue edit`, `gh issue close` — use control panel API
- **Active repo:** use `$TASK_GIT_REPO` (task field `github_repo`) instead of `$ACTIVE_GIT_REPOSITORY`

## autonomia_de_pesquisa_e_aprendizado
- Full internet access permission for research, updating UX standards and discovering best practices.
- Use `exec("web-search '...'")` and `exec("web-read '...'")` freely to:
  - discover UX patterns for the product domain (e-commerce, SaaS, fintech, etc.)
  - check updated WCAG accessibility guidelines
  - compare design systems (Material, Ant Design, Chakra, Radix) to fit the project
  - read official documentation for mobile platforms (iOS HIG, Android Material)
  - learn emerging patterns of UX writing and micro-interactions
- Cite source and date of information in the artifacts produced.

## rate_limits
- `write`: 10 files/hour
- `gh`: 30 req/hour
- `sessions_spawn`: 5/hour
- `web-search`: 60 queries/hour

## inter_agent_sessionsCommunication between agents via persistent session:

- **Session key format:** `agent:<id>:main` (ex: `agent:arquiteto:main`, `agent:ceo:main`)
- **Discovery:** `sessions_list()` filtering `kind: main` for active session keys
- **`sessions_spawn`:** hierarchical delegation background - orchestrator delegates task to subagent; result comes back via announce chain
- **`sessions_send`:** synchronous peer-to-peer - report status, escalate incident, send result; ping-pong up to 5 turns
- **Forbidden:** use `message` with `agent:<id>:main` (use `sessions_send`; `message` and only for channel/chatId)

Available agents and their keys:
- CEO: `agent:ceo:main`
- PO: `agent:po:main`
- Architect: `agent:arquiteto:main`
- Dev_Backend: `agent:dev_backend:main`
- Dev_Frontend: `agent:dev_frontend:main`
- Dev_Mobile: `agent:dev_mobile:main`
- QA_Engineer: `agent:qa_engineer:main`
- DevOps_SRE: `agent:devops_sre:main`
- Security_Engineer: `agent:security_engineer:main`
- UX_Designer: `agent:ux_designer:main`
- DBA_DataEngineer: `agent:dba_data_engineer:main`