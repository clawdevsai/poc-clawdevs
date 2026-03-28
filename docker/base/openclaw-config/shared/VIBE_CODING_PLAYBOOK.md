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

# VIBE CODING PLAYBOOK

ClawDevs AI should optimize for speed with observable quality.
The goal is to deliver a small, demonstrable and reversible slice quickly, then harden it with testing, contracts and observability.

## Principles
- Prioritize a short flow: idea -> spec -> vertical slice -> demo -> refinement.
- Always keep the user seeing real progress with each cycle.
- Prefer small, reversible changes with a clear scope.
- Avoid overengineering, but do not compromise on testing, security and traceability.
- Everything that goes into production needs to have acceptance, rollback and validation criteria.

## Recommended loop
1. Define the visible result in a sentence.
2. Write the minimum SPEC with observable behavior.
3. Deliver a functional vertical slice.
4. Validate with demo and human feedback.
5. Add tests, logs, metrics and hardening.
6. Repeat until the flow closes.

## What characterizes a good iteration
- Shows business or operation value quickly.
- Can be tested in minutes, not days.
- There is a clear path to entry, exit and error.
- Does not block further evolution.
- Leaves traceability to the next person or agent.

## Rules to avoid bad vibecoding
- Do not replace specifications with improvisation.
- Do not accumulate invisible refactoring without demonstrable delivery.
- Do not leave an implicit integration contract.
- Do not add abstractions without real need.
- Do not promote to "ready" without minimal testing and checking NFRs.

## Expected artifacts
- BRIEF
- SPEC
- US
- TASK
- demo notes
- tests
- observability

## Minimum quality per iteration
- Demonstrable behavior.
- Objective acceptance criteria.
- Testing evidence.
- Known risk and mitigation.
- Rollback or reversal path.