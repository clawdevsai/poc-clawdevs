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

# BRIEF

##Title
- Operationalize SDD as ClawDevs AI standard

## Context
- The platform already has templates, checklists, prompts and SDD contracts.
- This remains to be consolidated as an official and repeatable operational flow for all agents.

## Goal
- Make any internal initiative follow the same SDD contract without relying on additional explanation.

## Scope
- Includes:
  - use of Constitution, BRIEF, SPEC, CLARIFY, PLAN, TASK and VALIDATE
  - use of operational prompts and templates
  - alignment of agents to the shared contract
- Does not include:
  - stack change
  - main runtime change
  - functional rewriting of agents

##Constraints
- Needs to work on local Windows / Docker Desktop / Kubernetes.
- Needs to be documented and replicable.
- Need to keep operating costs low.

## Success metrics
- Every agent can locate the flow in less than 1 minute.
- Every new initiative goes through the SDD checklist before execution.
- The same contract applies to internal platforms and projects.

## Risks
- Risk: becoming unused documentation.
- Mitigation: make prompts and templates the normal path of operation.

## Assumptions
- The team accepts using markdown files as an operational contract.

## Next step
- Produce the operational behavior SPEC.