# Phase 2: Memory + Orchestration Loop - Research

**Researched:** 2026-04-02  
**Domain:** Orchestration loop, handoff contracts, parallelism gating, persistent memory lifecycle  
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### Orchestration Loop Shape
- **D-01:** Use a detailed pipeline: `plan → execute → self-review → peer-review → consolidate`.
- **D-02:** On execute failure, automatically replan and restart the cycle.
- **D-03:** Review validates outputs against contracts plus evidence (logs/diffs/tests), not cost.
- **D-04:** Consolidate aggregates result + summary and updates memory/state.

### Handoff Contracts
- **D-05:** Contracts are simple JSON schemas with minimal required fields.
- **D-06:** Validation enforces types, required fields, and consistency rules.
- **D-07:** Invalid contract → reject and trigger replan.

### Parallelism Gate
- **D-08:** Gate based on estimated cost/latency (tokens + time).
- **D-09:** Complexity threshold is adaptive (learns from history).
- **D-10:** Manual override is allowed via runtime flag.

### Memory Model + Lifecycle
- **D-11:** Memory storage is append-only event sourcing.
- **D-12:** Unified access layer includes policy enforcement plus per-agent local cache.
- **D-13:** Lifecycle triggers are hybrid: size + time.
- **D-14:** Versioning uses semantic merge with confidence/priority resolution.

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
| ORCH-01 | System runs a deterministic plan → execute → review → consolidate loop for each task | Existing `task_orchestration.py` + `task_workflow.py` show RQ-driven workflow; decisions define the exact loop steps |
| ORCH-02 | Agent handoffs use explicit contracts (inputs/outputs) and are validated | FastAPI/Pydantic patterns + JSON-schema decision for contracts |
| ORCH-03 | Parallelism is gated (default sequential; parallel only when complexity threshold allows) | RQ + Redis supports gated dispatch; add policy gate in orchestration service |
| MEM-01 | Each agent has persistent memory storage with a unified access layer | File-backed `MEMORY.md` + `MemoryEntry` model + `memory_sync.py` and `memory_indexing.py` |
| MEM-02 | Memory compaction lifecycle is enforced (create → compress → summarize → archive) | `adaptive_compressor.py`, `summarizer.py`, compaction policy doc |
| MEM-03 | Memory entries support versioning/merge rules to prevent divergence | Compaction policy + Memory Curator conflict resolution + append-only event sourcing decision |
</phase_requirements>

## Project Constraints (from CLAUDE.md)
- No new external integrations — keep scope internal.
- Low token consumption and low hardware requirements are mandatory.
- Must support Ollama as the initial LLM provider.
- Must remain installable on conventional machines.
- Internal docs in `docs/` must be considered even if partially outdated.
- Frontend package manager: use `pnpm` only.
- Backend package manager: use `uv` only.
- After backend schema changes, run `pnpm orval` in frontend.
- Model changes require Alembic migrations (auto-run on backend startup).
- README/docs are in Portuguese; code in English.

## Summary

The codebase already has the scaffolding to implement this phase without new external integrations: an RQ/Redis queue for orchestration, SQLModel models for task and memory metadata, file-based memory in `/data/openclaw/memory`, and services for memory sync/indexing, compression, and summarization. Phase 2 should formalize the deterministic loop and contracts, align orchestration state with `Task.workflow_state`, and enforce the memory lifecycle described in `docs/compaction-policy.md`.

The memory domain is split between filesystem truth (`MEMORY.md` per agent + `SHARED_MEMORY.md`) and database entries for UI (`MemoryEntry`). The compaction policy and Memory Curator doc clarify lifecycle triggers, required evidence logs, and conflict resolution paths. These should be codified in services and tasks, using append-only event sourcing and explicit merge/version metadata per decision.

**Primary recommendation:** Implement the loop and memory lifecycle in the backend service/task layers, reusing existing RQ orchestration, MemoryEntry model, and compaction/summarizer services, with explicit JSON-schema contracts enforced by Pydantic.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.135.1 | API + request validation | Existing backend framework |
| SQLModel | 0.0.37 | ORM + models (Task/MemoryEntry) | Existing data layer |
| Redis + RQ | redis[hiredis] >=6.0.0, rq 2.6.0 | Orchestration queue + workers | Current workflow engine |
| PostgreSQL + pgvector | pgvector >=0.3.0 | Memory persistence + embeddings | Existing DB strategy |
| Pydantic (via FastAPI) | bundled | Contract validation | Already used for API schemas |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sqlite3 FTS5 | stdlib | Memory indexing | `memory_indexing.py` |
| Ollama client | internal | Summarization/compression | `adaptive_compressor.py`, `summarizer.py` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| RQ | Celery | Not aligned with current stack; adds infra |
| Pydantic contracts | jsonschema lib | Adds new dependency; no gain vs Pydantic |

**Installation:**
```bash
uv sync
pnpm install
```

**Version verification:** Not run against registries; versions reflect current repo pins.

## Architecture Patterns

### Recommended Project Structure
```
control-panel/backend/app/
├── api/            # FastAPI routers
├── models/         # SQLModel entities
├── services/       # Orchestration + memory logic
├── tasks/          # RQ job entrypoints
└── hooks/          # Cross-cutting policies
```

### Pattern 1: Deterministic Orchestration Loop
**What:** CEO-driven task pipeline with explicit workflow states and activity logging.  
**When to use:** All task execution and handoffs.  
**Example:**
```python
# Source: control-panel/backend/app/tasks/task_orchestration.py
task.workflow_attempts += 1
task.workflow_state = WORKFLOW_PROCESSING_BY_CEO
await log_task_event(..., event_type="task.sent_to_ceo", ...)
```

### Pattern 2: Memory Sync + Indexing
**What:** Filesystem memory is authoritative; DB mirrors for UI.  
**When to use:** Read/write agent memory and shared memory.  
**Example:**
```python
# Source: control-panel/backend/app/services/memory_sync.py
memory_file = base_path / slug / "MEMORY.md"
...
db_session.add(MemoryEntry(..., entry_type="active", ...))
```

### Anti-Patterns to Avoid
- **Writing memory only to DB:** The system expects `/data/openclaw/memory` as source of truth.
- **Non-idempotent RQ jobs:** Orchestration jobs are retried; must be safe to re-run.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Job orchestration | Custom in-process scheduler | RQ + Redis | Already integrated, supports retries |
| Contract validation | Custom JSON validation | Pydantic models + schema | Consistent with FastAPI |
| Memory search | Manual grep-only | `memory_indexing.py` (FTS5) | Faster, cached search |

**Key insight:** The repo already provides queueing, memory sync, and summarization primitives—extend them rather than adding new subsystems.

## Common Pitfalls

### Pitfall 1: Skipping compaction evidence
**What goes wrong:** Compaction runs but no structured log/sha evidence is persisted, violating policy.  
**Why it happens:** Compaction policy requires logging (`compaction_completed`, hashes).  
**How to avoid:** Emit required log entries and file hash after compaction.  
**Warning signs:** No `compaction_completed` entries in structured logs.

### Pitfall 2: Contract validation mismatch
**What goes wrong:** Handoffs succeed with malformed payloads.  
**Why it happens:** Schema checks not enforced on every hop.  
**How to avoid:** Validate contract before dispatch and before accept; reject on invalid.  
**Warning signs:** Missing required fields in activity events.

## Code Examples

### Enqueue Orchestration Job
```python
# Source: control-panel/backend/app/services/task_workflow.py
queue.enqueue(
    "app.tasks.task_orchestration.process_task_via_ceo",
    str(task_id),
    job_id=job_id,
    retry=Retry(max=3, interval=[30, 120, 300]),
)
```

### Memory File → DB Sync
```python
# Source: control-panel/backend/app/services/memory_sync.py
content = memory_file.read_text(encoding="utf-8").strip()
db_session.add(MemoryEntry(agent_slug=slug, body=content, entry_type="active"))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Ad-hoc memory files only | File + DB mirror + indexing | 2026 (current codebase) | Enables UI + search |

**Deprecated/outdated:**
- None explicitly documented.

## Open Questions

1. **Where should contract schemas live?**
   - What we know: Handoffs are JSON schemas with minimal fields (decision).
   - What's unclear: Central registry vs per-agent schemas.
   - Recommendation: Define a shared schema module in `app/models` or `app/services/contracts`.

2. **How to compute adaptive complexity threshold?**
   - What we know: Threshold is adaptive and based on cost/latency.
   - What's unclear: Exact formula and storage (DB vs memory).
   - Recommendation: Store metrics in DB and start with simple rolling averages.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Backend | ✓ | 3.12.10 | — |
| Node | Frontend tooling | ✓ | v22.21.1 | — |
| pnpm | Frontend installs | ✓ | (version not reported) | — |
| uv | Backend installs | ✓ | 0.11.2 | — |
| Docker | Local stack | ✓ | 29.3.1 | — |
| redis-cli | Redis checks | ✗ | — | Use app logs/health endpoints |
| psql | Postgres checks | ✗ | — | Use app logs/health endpoints |

**Missing dependencies with no fallback:**
- None.

**Missing dependencies with fallback:**
- `redis-cli`, `psql` — diagnostics can use service logs/metrics.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Pytest 8.4.0; Cypress 15.13.0 (frontend) |
| Config file | none detected |
| Quick run command | `uv run pytest -q` |
| Full suite command | `uv run pytest` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|------------------|--------------|
| ORCH-01 | Deterministic loop per task | unit/integration | `uv run pytest -q` | ❌ Wave 0 |
| ORCH-02 | Contract validation | unit | `uv run pytest -q` | ❌ Wave 0 |
| ORCH-03 | Parallelism gating | unit | `uv run pytest -q` | ❌ Wave 0 |
| MEM-01 | Unified memory access | integration | `uv run pytest -q` | ❌ Wave 0 |
| MEM-02 | Compaction lifecycle | integration | `uv run pytest -q` | ❌ Wave 0 |
| MEM-03 | Merge/version rules | unit | `uv run pytest -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest -q`
- **Per wave merge:** `uv run pytest`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `control-panel/backend/tests/test_orchestration_loop.py` — covers ORCH-01..03
- [ ] `control-panel/backend/tests/test_memory_lifecycle.py` — covers MEM-01..03
- [ ] Test config (e.g., `pytest.ini`) — none detected

## Sources

### Primary (HIGH confidence)
- `docs/compaction-policy.md` — compaction lifecycle and evidence requirements
- `docs/agentes/memory_curator.md` — shared memory ownership and conflict resolution
- `control-panel/backend/app/services/task_workflow.py` — RQ orchestration enqueue pattern
- `control-panel/backend/app/tasks/task_orchestration.py` — workflow loop entrypoint
- `control-panel/backend/app/services/memory_sync.py` — filesystem → DB memory sync
- `control-panel/backend/app/models/memory_entry.py` — memory schema

### Secondary (MEDIUM confidence)
- `.planning/codebase/ARCHITECTURE.md` — layer mapping and locations
- `.planning/codebase/STACK.md` — stack versions
- `.planning/codebase/STRUCTURE.md` — directory layout

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM — based on repo pins, not registry verification
- Architecture: HIGH — based on codebase maps + existing services
- Pitfalls: MEDIUM — based on docs + observed patterns

**Research date:** 2026-04-02  
**Valid until:** 2026-05-02
