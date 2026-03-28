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

#TASK

## Related artifacts
- BRIEF: `BRIEF.md`
- SPEC: `SPEC.md`
- Clarify: `CLARIFY.md`
- Plan: `PLAN.md`

## Objective
- Publish and operationalize the SDD flow as ClawDevs AI standard.

## Scope
- Includes:
  - official templates
  - operational prompts
  - checklist SDD
  - complete example
- Does not include:
  - gateway architecture change
  - stack change
  - agent runtime rewrite

## Acceptance criteria
1. Given a new agent, when it starts, it then finds the main SDD artifacts.
2. Given a new initiative, when it opens, then there is a clear path to BRIEF -> SPEC -> CLARIFY -> PLAN -> TASK -> VALIDATE.
3. Given the README, when someone opens the repo, then the flow becomes evident in a few seconds.

## Implementation steps
1. Publish shared templates and contracts.
2. Distribute files to agent workspaces.
3. Update README and Makefile.
4. Validate Kustomize rendering.

## Tests
- Unit: N/A
- Integration: `docker-compose kustomize container`
- Validation: reading prompts and shortcuts

## NFRs
- Performance: zero impact on runtime.
- Cost: no material increase in cost.
- Security: no secrets or credentials.
- Observability: traceable docs in markdown.

## Done when
- The flow is ready for internal use and for projects.