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

# SDD FULL CYCLE EXAMPLE

This document shows a complete cycle using the repository's templates.
The example initiative is internal: reinforce the use of SDD in all agents and make the flow repeatable.

##Constitution
- Specification comes before implementation.
- The SPEC is the source of truth for intended behavior.
- Clarification happens before planning.
- Tasks must trace back to SPEC, BRIEF and the approved scope.

## Brief
###Title
- Standardize the SDD flow for internal ClawDevs AI and for delivered projects.

### Context
- Today the system already has agents, prompts, checklists and templates.
- There is a lack of a complete and repeatable example to guide new initiatives.

###Goal
- Make the SDD flow operable by any agent without ambiguity.

### Scope
- Includes:
  - templates for BRIEF, SPEC, CLARIFY, PLAN, TASK and VALIDATE
  - checklist SDD
  - operational prompts by role
  - alignment of agents to the same contract
- Does not include:
  - full agent rewrite
  - stack change
  - new external services

### Success metrics
- New agent can follow the flow without additional instructions.
- Each initiative has BRIEF -> SPEC -> PLAN -> TASK -> VALIDATE traceability.

## Spec
### Behavior
- Upon receiving an initiative, the CEO generates an initial BRIEF and SPEC.
- If there is ambiguity, the flow enters CLARIFY before PLAN.
- PO refines the SPEC into FEATURE and USER STORY.
- The Architect converts it into PLAN, TASK and technical validation.
- Dev_Backend implements exactly what was specified.

###Contracts
- BRIEF defines context, objective and scope.
- SPEC defines observable behavior, contracts, NFRs and acceptance criteria.
- CLARIFY records doubts, decisions and assumptions.
- PLAN defines architecture, phases, risks and validation.
- TASK defines executable and testable work.
- VALIDATE ends with evidence and decision.

### Acceptance criteria
1. Given a new initiative, when the CEO starts the flow, then there is BRIEF and initial SPEC.
2. Given an ambiguity, when the flow encounters a gap, then there is CLARIFY before PLAN.
3. Given a ready TASK, when the Dev_Backend executes, then the result is traceable to the SPEC.

## Clarify
### Ambiguities
- What is the best way to display templates to the team?
- Does the checklist need to be a hard gate or a strong guide?

### Decisions
- Expose everything in the README and via `make` to reduce friction.
- Treat the checklist as a readiness gate.

### Assumptions
- The team prefers short commands and lean artifacts.

## Plan
### Architecture
- `container/base/openclaw-config/shared/` stores the official templates.
- `container/base/openclaw-container.yaml` copies the files to the agents' workspaces.
- `container/base/kustomization.yaml` exposes the files in configMap.
- `README.md` becomes the flow input port.
- `Makefile` offers shortcuts to open artifacts.### Phases
1. Create templates and convention documents.
2. Copy artifacts to agents in bootstrap.
3. Expose operation shortcuts.
4. Validate rendering and consistency.

### Risks
- Risk: the flow becomes just documentation.
- Mitigation: maintain operational prompts and mandatory checklist.

##Tasks
1. Create standard templates and operation documents.
2. Integrate templates with bootstrap and configMap.
3. Update README and Makefile.
4. Validate customization and contract consistency.

## Validate
###Checks
- [x] Templates exist and are referenced.
- [x] Agents receive files in bootstrap.
- [x] README points out the flow and shortcuts.
- [x] Makefile exposes support commands.
- [x] `docker-compose kustomize container` renders successfully.

### Decision
- Status: approved for internal use as a reference.
- Notes: this example serves as a template for new initiatives.