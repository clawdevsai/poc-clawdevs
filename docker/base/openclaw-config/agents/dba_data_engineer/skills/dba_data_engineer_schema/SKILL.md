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
name: dba_data_engineer_schema
description: Skill DBA/DataEngineer for schema, migrations, query optimization and LGPD compliance
---

# DBA_DataEngineer Skills

Use this document as a single skill to guide schema design, migrations and optimization.

---

## Create Schema / Migration

Workflow:
1. Read TASK-XXX.md and US-XXX.md to understand the required data model.
2. Search the web for engines and standards for the domain (e.g. time-series, documents, relational).
3. Design schema with ERD in Markdown/Mermaid.
4. Identify personal data → document data map LGPD.
5. Create up + down migration with project tools.
6. Test migration in dev: `migrate up` + validate data + `migrate down` + validate rollback.
7. Document estimated storage cost.
8. Persist artifacts in `/data/openclaw/backlog/database/`.
9. Report to the Architect with evidence (migration status, ERD, LGPD map).

---

## Optimize Query

Workflow:
1. Capture EXPLAIN PLAN from the problematic query (before).
2. Identify: full table scan, missing index, N+1, inefficient subquery.
3. Propose and apply optimization (index, rewriting, spot denormalization).
4. Capture EXPLAIN PLAN after + p95 latency benchmark.
5. Check that there is no regression in related queries.
6. Document decision in ADR if it is a change in structure.
7. Report to Dev_Backend and Architect with evidence.

---

## 4-hour appointment (Required)

1. Every 4h (offset :30), check GitHub for open issues with label `dba`.
2. If there is an eligible issue, start execution.
3. If there is none, register standby and close the cycle without unnecessary processing.