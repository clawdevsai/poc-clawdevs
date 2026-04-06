# Phase 3: Monitoring + Control Panel - Research

**Researched:** 2026-04-06
**Domain:** Monitoring UI + runtime control plane (Next.js + FastAPI)
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### UI Structure
- **D-01:** Dashboard uses tabs.
- **D-02:** Tabs: Sessions, Tasks, Agents, Metrics.
- **D-03:** List density is medium.
- **D-04:** Each tab shows 4 top cards: active sessions, tasks in progress, tokens consumed, failures.

### Metrics & Aggregations
- **D-05:** Default window: 30 minutes with selector (1h, 6h, 24h).
- **D-06:** Metrics must include MON-02 set: tokens consumed, backlog, tasks in progress, tasks completed.
- **D-07:** Aggregation default: average per task (where applicable).
- **D-08:** Updates in real time via WebSocket.

### Failure Observability
- **D-09:** Failure view shows message + stack trace + evidence (logs/diffs/tests).
- **D-10:** Default detail is summary with expand for more.
- **D-11:** Retention is configurable by CTO.

### Configuration Management
- **D-12:** CTO can change limits/flags, model/provider selection, and agent management (activate/deactivate, roles).
- **D-13:** Require confirmation/audit for: model changes, agent disable, threshold changes.

### Claude's Discretion
## Specific Ideas

No specific requirements — open to standard approaches.

### Deferred Ideas (OUT OF SCOPE)
## Deferred Ideas

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MON-01 | Control panel shows sessions for last 30 minutes + historical session list | Sessions API `/sessions` + model fields for `created_at/last_active_at/ended_at`; need new UI tab + time-window filter and default 30m |
| MON-02 | Control panel shows metrics: tokens consumed, backlog, tasks in progress, tasks completed | Metrics API `/metrics`, Task model `status`, Session `token_count`; need aggregation endpoints + WS updates |
| MON-03 | Control panel shows cycle time per task and throughput per team | Task `created_at/updated_at/status` + ActivityEvent timeline; add service/endpoint to compute cycle time + throughput by `label` or agent team |
| MON-04 | Control panel exposes failure observability (traces/logs with evidence) | Task failure fields + ActivityEvent payload + task contracts `evidence`; add endpoint + UI detail view |
| CTRL-01 | CTO can manage core runtime settings via control panel without recreating existing features | Settings are env-based today; need runtime config store + audited changes + UI controls |
</phase_requirements>

## Project Constraints (from CLAUDE.md)
- No new external integrations.
- Low token/hardware usage is mandatory.
- Ollama-first LLM provider.
- Must remain installable on conventional machines.
- Use `pnpm` for frontend; no `npm`/`yarn`.
- Use `uv` for backend; no `pip`.
- After backend schema changes, run `pnpm orval` to regenerate API clients.
- Model changes require Alembic migrations; migrations auto-run at backend startup.
- Consider `docs/` even if partially outdated.
- Makefile is the primary stack operator (no docker-compose).

## Summary

Phase 3 should extend the existing control-panel stack (Next.js App Router + FastAPI) with a dedicated monitoring dashboard that matches the locked tabbed UI structure and real-time updates via WebSocket. Core data already exists in models (Sessions, Tasks, ActivityEvent, Metric) and services (failure detection, health monitoring, context-mode metrics). The missing pieces are time-windowed aggregations (30m/1h/6h/24h), throughput/cycle-time computations, and a failure observability endpoint that surfaces evidence artifacts.

Runtime settings are currently environment-based (`app/core/config.py`) and only exposed read-only via `/settings/info` and `/settings/gateway-health`. Meeting CTRL-01 requires a persisted runtime configuration layer (DB table + service) and a controlled UI for modifying flags, limits, provider selection, and agent management with confirmation and audit history.

**Primary recommendation:** Add new backend monitoring endpoints (aggregations + failure details + settings CRUD with audit) and a new tabbed monitoring UI using existing React Query + WS patterns, keeping metrics computed in services and pushed via WS channel updates.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 16.2.0 (repo) / latest 16.2.2 | App Router UI | Existing frontend framework in control panel |
| React | 19.2.4 (repo) / latest 19.2.4 | UI runtime | Existing dependency |
| FastAPI | 0.135.1 (repo) / latest 0.135.3 | API services | Existing backend framework |
| SQLModel | 0.0.37 (repo) / latest 0.0.38 | ORM | Existing data layer |
| Uvicorn | 0.34.0 (repo) / latest 0.44.0 | ASGI server | Existing backend server |
| Alembic | 1.18.4 (repo) / latest 1.18.4 | DB migrations | Existing migrations |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tanstack/react-query | 5.94.5 (repo) / latest 5.96.2 | UI data caching | All control-panel API queries |
| Axios | 1.13.5 | HTTP client | Use existing `customInstance` |
| Recharts | 3.8.0 (repo) / latest 3.8.1 | Charts | Metrics charts |
| Radix UI | various | UI primitives | Tabs, dialogs, dropdowns |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| React Query | SWR | Would diverge from existing patterns |
| WS manager | SSE | WS is already used for live updates |

**Installation:**
```bash
cd control-panel/frontend && pnpm install
cd control-panel/backend && uv sync
```

**Version verification (latest + publish time):**
- Next 16.2.2 published 2026-04-01T00:14:36Z (npm time).
- React 19.2.4 published 2026-01-26T18:23:10Z (npm time).
- React Query 5.96.2 published 2026-04-03T10:24:08Z (npm time).
- Recharts 3.8.1 published 2026-03-25T12:12:20Z (npm time).
- FastAPI 0.135.3 uploaded 2026-04-01T16:23:59Z (PyPI JSON).
- SQLModel 0.0.38 uploaded 2026-04-02T21:03:56Z (PyPI JSON).
- Uvicorn 0.44.0 uploaded 2026-04-06T09:23:21Z (PyPI JSON).
- Alembic 1.18.4 uploaded 2026-02-10T16:00:49Z (PyPI JSON).

## Architecture Patterns

### Recommended Project Structure
```
control-panel/
├── backend/app/
│   ├── api/            # FastAPI routers (add monitoring + settings endpoints)
│   ├── services/       # Aggregations, failure observability, settings service
│   └── models/         # SQLModel tables (metrics, settings, audits)
└── frontend/src/
    ├── app/monitoring/ # Tabbed monitoring UI
    ├── components/     # Cards, tables, charts
    └── lib/            # API clients + ws manager
```

### Pattern 1: Aggregation Endpoint + WS Broadcast
**What:** Compute metrics in a service, expose via FastAPI router, and push refresh via WS channel.
**When to use:** Real-time dashboards (D-08).
**Example:**
```python
# Source: control-panel/backend/app/api/metrics.py
@router.get("/overview", response_model=OverviewMetrics)
async def overview_metrics(_: CurrentUser, session: Annotated[AsyncSession, Depends(get_session)]):
    ...
```

### Pattern 2: React Query + WS Invalidate
**What:** Subscribe to WS channel and invalidate queries on events.
**When to use:** Live updates for tabs/cards.
**Example:**
```tsx
// Source: control-panel/frontend/src/app/page.tsx
const unsubscribe = wsManager.subscribe("dashboard", () => {
  queryClient.invalidateQueries({ queryKey: ["metrics"] })
})
```

### Anti-Patterns to Avoid
- **Direct DB access from UI:** Always go through API routes.
- **Long-running queries in request handlers:** Precompute or limit time windows (30m/1h/6h/24h).
- **WebSocket auth in query params:** Use first-frame auth as in `api/ws.py`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Client caching | Manual cache | React Query | Existing app standard |
| WS reconnect | Custom WS logic | `src/lib/ws.ts` | Existing auth + channel patterns |
| Aggregation pagination | Custom paginator | SQLModel + `fastapi-pagination` | Existing dependency |

**Key insight:** The control panel already has consistent API + WS patterns; reuse them to avoid divergence.

## Common Pitfalls

### Pitfall 1: Timezone Drift in Metrics
**What goes wrong:** Metrics window boundaries are inconsistent across DB and UI.
**Why it happens:** Naive vs UTC datetimes.
**How to avoid:** Normalize to naive UTC (see `_to_naive_utc` in `metrics.py`).
**Warning signs:** Unexpected empty buckets in last-30m view.

### Pitfall 2: Session Sync Costs
**What goes wrong:** `/sessions` always calls `sync_sessions`, causing slow list calls.
**Why it happens:** Sync on each list request.
**How to avoid:** Cache or throttle sync for 30m view; reuse existing pagination.
**Warning signs:** List endpoint latency spikes.

### Pitfall 3: Settings Mutations Without Audit
**What goes wrong:** CTO changes are non-reproducible.
**Why it happens:** Only env-based settings exist today.
**How to avoid:** Persist settings + audit log + confirm flow (D-13).
**Warning signs:** Drift between runtime config and UI.

## Code Examples

### Sessions Listing
```python
# Source: control-panel/backend/app/api/sessions.py
@router.get("", response_model=SessionsListResponse)
async def list_sessions(...):
    await sync_sessions(session)
    ...
```

### WebSocket Channel Auth
```python
# Source: control-panel/backend/app/api/ws.py
@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Polling metrics | WS + query invalidation | Existing WS manager | Lower latency, fewer requests |

**Deprecated/outdated:**
- Direct metric computation in UI — should stay server-side.

## Open Questions

1. **Where to persist runtime settings?**
   - What we know: Settings are env-based today (`app/core/config.py`).
   - What's unclear: Desired storage (DB table vs config file).
   - Recommendation: Use DB table with audit log; keep env as defaults.

2. **Definition of “team” for throughput**
   - What we know: Tasks have `label` and `assigned_agent_id`.
   - What's unclear: Whether throughput groups by label, agent role, or team.
   - Recommendation: Use task `label` as team proxy unless specified.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | Frontend | ✓ | 22.21.1 | — |
| pnpm | Frontend | ⚠︎ | present but `pnpm --version` failed | Use Corepack or reinstall |
| Python | Backend | ✓ | 3.14.3 (project expects 3.12) | Install 3.12 |
| uv | Backend | ✓ | 0.11.2 | — |
| Docker | Stack services | ✓ | 29.3.1 | — |
| PostgreSQL client | DB inspection | ✗ | — | Use Docker service |
| Redis CLI | Queue inspection | ✗ | — | Use Docker service |

**Missing dependencies with no fallback:**
- None (Docker provides DB/Redis).

**Missing dependencies with fallback:**
- PostgreSQL client (`psql`) and `redis-cli` — use Docker containers.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Pytest 8.4.0 + pytest-asyncio 0.25.3 |
| Config file | `control-panel/backend/pyproject.toml` |
| Quick run command | `uv run pytest tests/test_api/test_metrics.py -x` |
| Full suite command | `uv run pytest tests/` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MON-01 | Sessions list + last 30m | integration | `uv run pytest tests/test_api/test_agents_sessions.py -x` | ✅ |
| MON-02 | Metrics tokens/backlog/tasks | integration | `uv run pytest tests/test_api/test_metrics.py -x` | ✅ (basic) |
| MON-03 | Cycle time + throughput | unit/integration | `uv run pytest tests/test_api/test_metrics.py -x` | ❌ Wave 0 |
| MON-04 | Failure traces/evidence | unit/integration | `uv run pytest tests/test_api/test_tasks.py -x` | ❌ Wave 0 |
| CTRL-01 | Runtime settings updates | integration | `uv run pytest tests/test_api/test_settings.py -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_api/test_metrics.py -x`
- **Per wave merge:** `uv run pytest tests/`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `control-panel/backend/tests/test_api/test_settings.py` — settings CRUD + audit
- [ ] `control-panel/backend/tests/test_api/test_metrics.py` — add MON-03/MON-04 cases

## Sources

### Primary (HIGH confidence)
- Repo sources: `control-panel/backend/app/api/*.py`, `control-panel/backend/app/models/*.py`, `control-panel/frontend/src/app/*`
- PyPI JSON: `https://pypi.org/pypi/fastapi/json`, `https://pypi.org/pypi/sqlmodel/json`, `https://pypi.org/pypi/uvicorn/json`, `https://pypi.org/pypi/alembic/json`

### Secondary (MEDIUM confidence)
- npm registry metadata via `npm view <pkg> time`

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM — versions verified; repo pins behind latest for some packages.
- Architecture: HIGH — based on existing repo patterns.
- Pitfalls: MEDIUM — derived from current implementation and operational patterns.

**Research date:** 2026-04-06  
**Valid until:** 2026-05-06
