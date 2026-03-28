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
name: dev_backend_implementation
description: Condensed backend implementation skill for task execution, tests, CI evidence, and cost-performance focus.
---

# Dev Backend Implementation (Condensed)

## When to execute
- Scheduled queue cycle for `back_end` issues.
- Immediate handoff from Architect in shared session.

## Core flow
1. Read TASK + SPEC (+ ADR if relevant).
2. Implement only approved scope.
3. Add/update tests.
4. Run lint/test/build/security checks.
5. Report evidence to Architect.

## Required quality gates
- Security basics (validation/auth/secrets).
- Observable behavior aligned to SPEC.
- Coverage target >= 80% or task target.
- Explicit cost/performance tradeoff when relevant.

## Fallback commands
- Node: `npm ci && npm test && npm run lint && npm run build`
- Python: `pytest` + lint + build/check
- Go: `go test ./... && go vet ./...`
- Rust: `cargo test && cargo clippy`

## Guardrails
- Never bypass tests/security gates.
- Never commit secrets.
- Never use destructive git operations.
