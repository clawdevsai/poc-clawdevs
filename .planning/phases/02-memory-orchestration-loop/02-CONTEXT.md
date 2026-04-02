# Phase 2: Memory + Orchestration Loop - Context

**Gathered:** 2026-04-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a deterministic coordination loop with validated handoffs, gated parallelism, and a unified persistent memory layer with lifecycle and versioned merge rules.

</domain>

<decisions>
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project & Requirements
- `.planning/PROJECT.md` — core value, constraints, and project guardrails
- `.planning/REQUIREMENTS.md` — orchestration and memory requirements (ORCH-01..03, MEM-01..03)
- `.planning/ROADMAP.md` — phase goals and success criteria

### Codebase Context Maps
- `.planning/codebase/ARCHITECTURE.md` — system layers and data flow
- `.planning/codebase/STACK.md` — runtime/framework constraints
- `.planning/codebase/STRUCTURE.md` — where orchestration/memory code should live
- `.planning/codebase/CONVENTIONS.md` — error handling/logging expectations

### Internal Docs (partially outdated, but must be considered)
- `docs/` — internal documentation to consider during refactor

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Backend service layer exists in `control-panel/backend/app/services` for orchestration and memory logic.
- Background task runners live in `control-panel/backend/app/tasks` for coordination loops.

### Established Patterns
- FastAPI + SQLModel services with async patterns.
- API routers in `control-panel/backend/app/api` with Pydantic validation.

### Integration Points
- WebSocket metrics flow already wired in `control-panel/backend/app/api/ws.py` and `control-panel/frontend/src/lib/ws.ts`.
- Frontend API proxy in `control-panel/frontend/src/app/api/[...slug]/route.ts`.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-memory-orchestration-loop*
*Context gathered: 2026-04-02*
