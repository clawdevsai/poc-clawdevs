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

# SDD CHECKLIST

Use this checklist before passing on a change.

##Constitution
- [ ] The change is in line with the constitution of the repository.
- [ ] The objective was written in a short and observable way.

## Brief
- [ ] The problem and the expected value are clear.
- [ ] The scope and non-scope are defined.
- [ ] The main risks have been identified.

## Spec
- [ ] SPEC describes observable behavior.
- [ ] Contracts, invariants and NFRs are explicit.
- [ ] Acceptance criteria are testable.

## Clarify
- [ ] Ambiguities have been resolved.
- [ ] The assumptions were recorded.
- [ ] What was left open was declared.

## Plan
- [ ] There is a technical plan consistent with SPEC.
- [ ] The architectural decisions are justified.
- [ ] The impact on cost, safety and operation was considered.

##Tasks
- [ ] Tasks are small and executable.
- [ ] Traceability to SPEC and BRIEF is maintained.
- [ ] The implementation order reduces risk.

## Implement
- [ ] The minimum demonstrable functional slice exists.
- [ ] Tests cover SPEC scenarios.
- [ ] Logs, metrics and rollback were considered.

## Validate
- [ ] CI or local validation passed.
- [ ] The demo confirmed the expected behavior.
- [ ] The artifact can proceed to the next step without ambiguity.