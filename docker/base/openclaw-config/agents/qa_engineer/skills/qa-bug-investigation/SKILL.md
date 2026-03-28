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
name: qa-bug-investigation
description: Condensed QA bug investigation flow with reproducible steps, root-cause isolation and regression-safe validation.
---

# QA Bug Investigation (Condensed)

## Scope
- Work only inside `/data/openclaw/projects`.

## Investigation flow
1. Reproduce with deterministic steps and expected vs actual behavior.
2. Isolate minimal failing case.
3. Confirm root cause with objective evidence.
4. Validate fix with failing-before/passing-after tests.
5. Run quick regression checks on adjacent scenarios.

## Output template
- Bug title/severity/environment
- Reproduction steps
- Expected vs actual
- Root cause + evidence
- Fix validation
- Remaining risk and follow-ups

## Flaky handling
- Run multiple attempts and report failure frequency.
- Treat unstable pass as inconclusive until stabilized.
