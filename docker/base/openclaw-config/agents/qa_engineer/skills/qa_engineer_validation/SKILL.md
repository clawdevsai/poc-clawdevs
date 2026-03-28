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
name: qa_engineer_validation
description: Condensed QA validation skill for BDD, e2e validation, and evidence-based PASS/FAIL reporting.
---

# QA Validation (Condensed)

## Core cycle
1. Read SPEC + TASK.
2. Map BDD scenarios to tests.
3. Run tests and collect evidence.
4. Report PASS/FAIL.
5. On 3rd retry failure, escalate to Architect.

## PASS criteria
- All required scenarios executed.
- No critical failures.
- Evidence attached (logs/report/screenshots/traces).

## FAIL criteria
- List exact failing scenarios and error messages.
- Include reproduction/evidence path.
- Provide next action for dev agent.

## Default tools
- Web e2e: Playwright/Cypress
- Mobile e2e: Detox/Maestro
- Contract: Pact
- Load: k6
- Security baseline: dependency + secret checks

## Guardrails
- Never approve without evidence.
- Never skip BDD scenario validation.
- Never modify production code.
