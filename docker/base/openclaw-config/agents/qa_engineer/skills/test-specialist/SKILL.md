---
name: test-specialist
description: Condensed testing skill for JS/TS covering unit/integration/e2e, bug analysis, and coverage improvement.
---

# Test Specialist (Condensed)

## Scope
- Operate only inside `/data/openclaw/projects`.
- Read `/data/openclaw` only when session rules require context.

## Core workflow
1. Reproduce issue or confirm feature behavior.
2. Write/adjust tests (unit/integration/e2e) for expected behavior.
3. Run tests and collect evidence.
4. Report PASS/FAIL with exact failing scenarios.
5. Propose minimal fix direction when failures indicate root cause.

## Mandatory practices
- Use clear AAA structure in tests.
- Cover happy path, edge cases and error paths.
- Keep tests independent and deterministic.
- Prefer behavior assertions over implementation details.
- Do not approve without evidence.

## Coverage and gaps
- Identify untested critical paths first (API/services/domain logic).
- Raise priority for low coverage in security/financial/auth flows.
- Keep project target at or above required threshold (default 80% if unspecified).

## Debugging protocol
- Reproduce -> isolate -> root cause -> fix -> validate non-regression.
- On flaky tests, retry and document flakiness clearly.
- On third repeated failure, escalate with evidence and suspected cause.

## Security and reliability checks in tests
- Validate auth/permission boundaries.
- Validate input sanitization and unsafe payload handling.
- Validate basic performance constraints for critical operations.

## Deliverable format
- PASS/FAIL header
- Scenario-by-scenario outcome
- Evidence paths (logs/screenshots/traces)
- Residual risks and next action

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (95%+ redução em test reports).

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```
