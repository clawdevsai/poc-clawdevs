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

# TOOLS.md - DBA_DataEngineer

## available_tools
- `read(path)`: read schemas, migrations, TASKs and project artifacts.
- `write(path, content)`: writing migrations, schemas, data maps and reports.
- `exec(command)`: execute database commands, migrations and performance analysis.
- `exec("gh <args>")`: update issues/PRs and check CI status.
- `exec("curl -s -H 'Authorization: Bearer $PANEL_TOKEN' '$PANEL_API_URL/tasks?status=inbox&label=dba&page_size=20'")`: Task queue poll in the control panel.
- `exec("curl -s -X PATCH -H 'Authorization: Bearer $PANEL_TOKEN' -H 'Content-Type: application/json' -d '<json>' $PANEL_API_URL/tasks/<id>")`: Update task status.
- `exec("curl -s -X POST -H 'Authorization: Bearer $PANEL_TOKEN' -H 'Content-Type: application/json' -d '<json>' $PANEL_API_URL/tasks")`: Create new task (sub-tasks, bugs found, etc.).
- `git(args...)`: commit/branch/merge without destructive commands.
- `sessions_spawn(agentId, mode, label)`: create session with Architect, Dev_Backend or DevOps_SRE.
- `sessions_send(session_id, message)`: report result or request context.
- `sessions_list()`: list active sessions.
- `exec("web-search '<query>'")`: search the internet via SearxNG (aggregates Google, Bing, DuckDuckGo). Returns up to 10 results. Example: `web-search "postgresql index optimization 2025"`
- `exec("web-read '<url>'")`: read any web page as clean markdown via Jina Reader. Example: `web-read "https://www.postgresql.org/docs/current/indexes.html"`

## usage_rules
- `read/write` only on `/data/openclaw/**`.
- Block destructive commands without explicit TASK.
- GitHub commands must use `exec('gh ... --repo "$ACTIVE_GIT_REPOSITORY"')`.
- Validate `active_repository.env` before taking any action.
- `sessions_spawn` allowed for: `arquiteto`, `dev_backend`, `devops_sre`.
- Control panel queue poll 1x per hour:
  - example: `curl -s -H "Authorization: Bearer $PANEL_TOKEN" "$PANEL_API_URL/tasks?status=inbox&label=dba&page_size=20"`
- When picking up a task: `PATCH /tasks/<id>` with `{"status":"in_progress"}` immediately.
- At the end: `PATCH /tasks/<id>` with `{"status":"done"}`.
- Process `dba` label only. TASK_GIT_REPO = field `github_repo` of the task.
- Internet: full access allowed for technical research, bank CVEs, benchmarks and skills updating.

## github_permissions
- **Type:** `read+write`
- **Own label:** `dba` — automatically created at boot if it doesn't exist:
  `gh label create "dba" --color "#0052cc" --description "Database tasks — routed to DBA_DataEngineer" --repo "$ACTIVE_GIT_REPOSITORY" 2>/dev/null || true`
- **Allowed operations:** `gh pr`, `gh label`, `gh workflow`, `gh run view` (`--repo "$TASK_GIT_REPO"` only)
- **Prohibited:** `gh issue create`, `gh issue edit`, `gh issue close` — use control panel API
- **Active repo:** use `$TASK_GIT_REPO` (field `github_repo` of the task) instead of `$ACTIVE_GIT_REPOSITORY`

## autonomia_de_pesquisa_e_aprendizado
- Full internet access permission for research, updating skills and discovering better alternatives.
- Use `exec("web-search '...'")` and `exec("web-read '...'")` freely to:
  - compare managed services engines and costs (RDS, PlanetScale, Neon, Supabase, etc.)
  - check CVEs and security advisories in bank engines in use
  - search query and index optimization techniques
  - read official documentation on LGPD, GDPR and data regulations
  - learn emerging data engineering and streaming patterns
- Cite source and date of information in the artifacts produced.

## main_commands
### PostgreSQL
- `psql -c "EXPLAIN ANALYZE <query>"` — performance analysis
- `psql -c "\d <tabela>"` — table structure
### Migration Tools
- Flyway: `flyway migrate`, `flyway info`, `flyway undo`
- Alembic: `alembic upgrade head`, `alembic downgrade -1`, `alembic revision`
- Prisma: `npx prisma migrate deploy`, `npx prisma db push`, `npx prisma studio`
- Liquibase: `liquibase update`, `liquibase rollback`, `liquibase status`
### MongoDB
- `mongosh --eval "db.collection.explain('executionStats').find({})"` — analysis
### Redis
- `redis-cli info memory`, `redis-cli --latency`## rate_limits
- `exec`: 60 commands/hour
- `gh`: 50 req/hour
- `sessions_spawn`: 10/hour
- `web-search`: 60 queries/hour

## inter_agent_sessions

Communication between agents via persistent session:

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