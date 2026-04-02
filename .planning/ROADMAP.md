## Phases
- [ ] **Phase 1: Runtime Foundation & Sandbox** - Agents can run in a constrained, Ollama-first runtime with enforced workspace and tool safety
- [ ] **Phase 2: Memory + Orchestration Loop** - Tasks run through a deterministic coordination loop with validated handoffs and governed parallelism
- [ ] **Phase 3: Monitoring + Control Panel** - CTO can observe system health and manage runtime settings via the control panel
- [ ] **Phase 4: Evaluation Regression Suite** - Coordination regressions are detectable through a minimal runnable suite

## Phase Details
### Phase 1: Runtime Foundation & Sandbox
**Goal**: Agents can run in a constrained, Ollama-first runtime with enforced workspace and tool safety
**Depends on**: Nothing (first phase)
**Requirements**: WORK-01, WORK-02, WORK-03
**Success Criteria** (what must be TRUE):
  1. Agents operate inside a workspace sandbox with artifact tracking
  2. Tool execution is blocked unless it is on the allowlist and within safety limits
  3. Runtime runs Ollama-first with controlled fallback and no new external integrations
**Plans**: TBD

### Phase 2: Memory + Orchestration Loop
**Goal**: Tasks run through a deterministic coordination loop with validated handoffs and governed parallelism
**Depends on**: Phase 1
**Requirements**: ORCH-01, ORCH-02, ORCH-03, MEM-01, MEM-02, MEM-03
**Success Criteria** (what must be TRUE):
  1. Each task runs a deterministic plan → execute → review → consolidate loop
  2. Agent handoffs require explicit input/output contracts and are rejected when invalid
  3. Parallelism defaults to sequential and only enables after a complexity threshold is met
  4. Agents can read/write persistent memory via a unified access layer
  5. Memory lifecycle enforces create → compress → summarize → archive with versioned merge rules
**Plans**: TBD

### Phase 3: Monitoring + Control Panel
**Goal**: CTO can observe system health and manage runtime settings via the control panel
**Depends on**: Phase 2
**Requirements**: MON-01, MON-02, MON-03, MON-04, CTRL-01
**Success Criteria** (what must be TRUE):
  1. Control panel shows last 30 minutes of sessions plus historical session list
  2. Control panel shows tokens consumed, backlog, tasks in progress, and tasks completed
  3. Control panel shows cycle time per task and throughput per team
  4. Control panel exposes failure traces/logs with evidence
  5. CTO can change core runtime settings without recreating existing features
**Plans**: TBD
**UI hint**: yes

### Phase 4: Evaluation Regression Suite
**Goal**: Coordination regressions are detectable through a minimal runnable suite
**Depends on**: Phase 3
**Requirements**: EVAL-01
**Success Criteria** (what must be TRUE):
  1. A minimal regression suite for critical coordination scenarios runs on demand and reports pass/fail
**Plans**: TBD

## Progress
| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Runtime Foundation & Sandbox | 0/0 | Not started | - |
| 2. Memory + Orchestration Loop | 0/0 | Not started | - |
| 3. Monitoring + Control Panel | 0/0 | Not started | - |
| 4. Evaluation Regression Suite | 0/0 | Not started | - |
