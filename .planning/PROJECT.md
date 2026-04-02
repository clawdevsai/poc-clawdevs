# ClawDevs AI

## What This Is

ClawDevs AI is a self-hostable multi-agent software development team built on OpenClaw, designed for CTOs who want autonomous delivery with minimal human intervention. It provides a control panel, agent orchestration, and memory/coordination infrastructure so agents can plan, execute, review, and consolidate work end-to-end.

## Core Value

Agents coordinate tasks end-to-end without human intervention while keeping cost and hardware usage low.

## Requirements

### Validated

- ✓ Control panel exists for monitoring agents, sessions, tasks, and activity — existing
- ✓ OpenClaw gateway/runtime bootstrap and configuration are present — existing
- ✓ Multi-agent workspaces and agent skills are organized in repo and bootstrap scripts — existing
- ✓ WORK-01/02/03 runtime foundation (sandbox, tool safety, Ollama-first) — validated in Phase 01

### Active

- [ ] Refactor agent communication to be correct, efficient, and deterministic across the full loop (plan → execute → review → consolidate)
- [ ] Align runtime configuration and workflows with OpenClaw v2026.4.1 best practices
- [ ] Ensure memory persistence + compaction + session policies produce stable long-running autonomy
- [ ] Provide measurable monitoring for autonomy (tokens, backlog, throughput, PRs, session continuity)
- [ ] Preserve installability on conventional machines with low hardware cost and low token usage (Ollama-first)

### Out of Scope

- New external integrations — explicitly excluded for this phase
- Major UI redesigns — not required for the refactor goals

## Context

- Existing brownfield system with Next.js control panel, FastAPI backend, and OpenClaw bootstrap/runtime.
- Internal OpenClaw configuration lives under `docker/base/openclaw-config/` and is partially out of date.
- Primary user is a CTO who needs reliable autonomous delivery with monitoring and light intervention.
- Refactor aims to improve multi-agent coordination while preserving low-cost operation and easy installation.

## Constraints

- **Integrations**: No new external integrations — keep scope internal
- **Cost**: Low token consumption and low hardware requirements are mandatory
- **Runtime**: Must support Ollama as the initial LLM provider
- **Compatibility**: Must remain installable on conventional machines
- **Docs**: Internal docs in `./docs` must be considered even if partially outdated

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Refactor entire coordination stack now (not partial) | Need full autonomy end-to-end | — Pending |
| Sequential plan execution | Reduce concurrency risk while refactoring | — Pending |
| YOLO planning mode | Faster iteration while refactoring | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-02 after Phase 01 completion*
