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

---

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (90-98% redução ao executar queries).

### Otimizações Aplicadas

#### Database Queries (PostgreSQL/MySQL)
```sql
-- ❌ NÃO USE: SELECT * (500KB+ resultados)
SELECT * FROM large_table;

-- ✅ USE ESTE: Selecionar apenas colunas necessárias
SELECT id, name, status FROM large_table LIMIT 100;

-- ✅ Para EXPLAIN PLAN
EXPLAIN ANALYZE SELECT ... -- Retorna resumo, não dados
```

#### Migration Dumps
```bash
# ❌ NÃO USE: Dump completo
pg_dump database_name > backup.sql  # 1GB+

# ✅ USE ESTE: Estrutura apenas
pg_dump -s database_name > schema.sql  # 10KB

# ✅ Ou tabelas específicas
pg_dump -t table_name database_name
```

### Impacto Esperado

- **Redução de tokens por query**: 80-95%
- **Economia mensal**: ~$60 para este agent
- **Sem perda**: EXPLAIN PLAN + LIMIT resultam em dados suficientes

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```
