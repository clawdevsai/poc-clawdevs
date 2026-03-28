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

# PLAN

## Goal
- Make the SDD stream the ClawDevs AI default operating path.

## Inputs
- BRIEF
- SPEC
- CLARIFY
- Constitution
- Checklist SDD

##Architecture
- `docker/base/openclaw-config/shared/` keeps the contracts.
- `docker/base/openclaw-container.yaml` distributes the artifacts to the workspaces.
- `docker/base/kustomization.yaml` exposes the files in configMap.
- `README.md` points to the official entry of the stream.
- `Makefile` offers shortcuts to templates and operational prompts.

## Alternatives considered
- Option: leave the flow only in the documentation.
- Tradeoff: Less work now, greater risk of inconsistent use.
- Rejected because: does not create operational habit.

## Phases
1. Consolidate templates, checklists and prompts.
2. Expose everything to agents via bootstrap.
3. Create a complete example to guide new initiatives.

## Risks
- Risk: duplication of artifacts and confusion of the source of truth.
- Mitigation: keep the package shared and the main documentation lean.

## Validation
- kustomize rendering.
- README check.
- Verification of Makefile shortcuts.

## Rollback
- Remove shortcuts and new references without affecting the agents' runtime.