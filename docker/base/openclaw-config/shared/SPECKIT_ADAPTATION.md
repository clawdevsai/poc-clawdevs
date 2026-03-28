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

# SPECKIT ADAPTATION

This repository does not use the official Spec Kit as a required dependency.
Instead, it takes the same mental model and adapts it to ClawDevs AI artifacts.

## Correspondence between Spec Kit and ClawDevs AI
- `constitution` -> `CONSTITUTION.md`
- `specify` -> `SPEC_TEMPLATE.md` and `backlog/specs/`
- `clarify` -> record of ambiguities, assumptions and SPEC revisions
- `plan` -> `ADR`, `TASK` and the Architect's technical plan
- `tasks` -> `TASK-XXX-<slug>.md`
- `analyze` -> validation of NFRs, risks, security and cost
- `implement` -> Dev_Backend executing the task

## Operational objective
- Maintain the spec-driven flow for both the ClawDevs AI platform and project deliveries.
- Preserve end-to-end traceability.
- Avoid "loose" code without a clear contract.

## How to use
- The CEO consolidates the demand in Brief + SPEC.
- PO refines the SPEC and creates User Stories.
- The Architect converts SPEC/US into a technical plan and tasks.
- Dev_Backend strictly implements what is specified.