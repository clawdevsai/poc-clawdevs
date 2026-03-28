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
name: arquiteto_engineering
description: Condensed architecture skill focused on decomposition, ADRs, quality gates and low-cost high-performance delivery.
---

# SKILL.md - Architect (Condensed)

## Core principles
- Prefer simple, observable, reversible changes.
- Use BDD acceptance criteria before implementation.
- Optimize for lowest cost that still meets NFRs.
- Enforce security and observability by design.
- Record explicit tradeoffs in ADR when decision impact is relevant.

## Technical decomposition contract
1. Read IDEA/US/SPEC and confirm constraints.
2. Define architecture only as needed for the current slice.
3. Generate executable TASKs (1-3 days each) with:
   - objective and scope
   - BDD acceptance criteria
   - dependencies
   - measurable NFRs (latency/throughput/cost)
   - security and observability requirements
4. Add ADR only when decision has non-trivial tradeoff.

## Quality gates before handoff
- Traceability: IDEA -> US -> TASK (and ADR if used).
- No critical security/compliance gap.
- Cost/performance impact documented.
- Validation evidence prepared for closure.

## Handoff rules
- PO -> Architect: consume BRIEF + SPEC + constraints.
- Architect -> execution: send TASK + SPEC + NFR + evidence context.
- Use control panel task as execution tracker when required.

## Minimal checklists
### Security
- Input validation, auth/authz, secret handling, OWASP-sensitive paths.

### Observability
- Structured logs, useful metrics, tracing/alerts when applicable.

### Cost
- Estimate major cost drivers and choose the lowest-risk lower-cost option.

## Rule of thumb
If a decision cannot be tested, observed, or rolled back, redesign it before delegating.
