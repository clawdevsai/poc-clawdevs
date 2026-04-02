# Phase 2: Memory + Orchestration Loop - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-02
**Phase:** 2-memory-orchestration-loop
**Areas discussed:** Orchestration Loop Shape, Handoff Contracts, Parallelism Gate, Memory Model + Lifecycle

---

## Orchestration Loop Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal | plan → execute → review → consolidate | |
| Extended | plan → execute → review → fix → consolidate | |
| Detailed | plan → execute → self-review → peer-review → consolidate | ✓ |

**User's choice:** Detailed pipeline with self-review and peer-review.
**Notes:** Execute failures trigger replan/restart; review checks outputs + evidence; consolidate updates memory/state.

---

## Handoff Contracts

| Option | Description | Selected |
|--------|-------------|----------|
| Simple JSON | Minimal required fields | ✓ |
| Formal schema | JSON Schema/Pydantic with strict validation | |
| Heuristic | Flexible/heuristic validation | |

**User's choice:** Simple JSON contracts with consistency validation.
**Notes:** Validation includes types, required fields, and consistency rules; invalid contracts trigger replan.

---

## Parallelism Gate

| Option | Description | Selected |
|--------|-------------|----------|
| Plan size | Number of steps/tasks | |
| Cost/latency | Tokens + time | ✓ |
| Task type | Research vs execution | |

**User's choice:** Gate by cost/latency with adaptive threshold; manual override via runtime flag.
**Notes:** Threshold adapts based on historical performance.

---

## Memory Model + Lifecycle

| Option | Description | Selected |
|--------|-------------|----------|
| Snapshot | Per-agent document w/ versions | |
| Event sourcing | Append-only entries with indexes | ✓ |
| Hybrid | Snapshots + event log | |

**User's choice:** Event sourcing with policy+cache access layer, hybrid size/time lifecycle triggers, semantic merge.
**Notes:** Merge resolution based on confidence/priority.

---

## the agent's Discretion

None.

## Deferred Ideas

None.
