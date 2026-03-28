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
