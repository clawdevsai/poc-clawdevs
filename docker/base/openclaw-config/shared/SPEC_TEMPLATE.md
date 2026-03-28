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

# SPEC TEMPLATE

Use this model to describe external behavior before coding.
The objective is to reduce ambiguity, align humans and agents and maintain traceability between BRIEF, SPEC, US and TASK.

## 1. Context
- Problem we are solving
- Who is affected
- Because it matters now

## 2. Objective
- Expected result in one sentence
- Business or operational value

## 3. No goals
- What is explicitly out of scope

## 4. Functional scope
- Main streams
- Relevant alternative flows
- Expected error cases

## 5. Behavior
Describe in domain language and, when useful, in Given/When/Then format.

### Stream 1
- Given:
- When:
- Then:

### Stream 2
- Given:
- When:
- Then:

## 6. Contracts
- Entrances and exits
- Validation rules
- Preconditions and postconditions
- Invariants
- Integrations and limits between systems
- Status or sequence, if applicable

## 7. Non-functional requirements
- Performance
- Cost
- Security
- Observability
- Compliance
- Availability and resilience

## 8. Data
- Data created, read, updated and removed
- Classification of sensitive data
- Retention and audit

## 9. Tests and acceptance criteria
- Validation scenarios
- Objective acceptance criteria
- Signs of failure

## 10. Rollout
- Delivery plan
- Migration, if any
- Rollback, if necessary

## 11. Risks and decisions
- Known risks
- Decisions made
- Assumptions adopted

## 12. Traceability
- BRIEF:
- SPEC:
- US:
- TASK:
- Issues:

## Usage rule
- Keep the spec complete but concise.
- Prefer observable behavior over vague descriptions.
- Redo the spec before refactoring the implementation when the behavior changes.