---
name: arquiteto_engineering
description: Condensed architecture skill focused on decomposition, ADRs, quality gates and low-cost high-performance delivery.
---

# SKILL.md - Architect (Condensed)

## Core principles
- Prefer simple, observable, reversible changes.
- Use BDD acceptance criteria before implementation.
- Optimize for lowest cost that still meets NFRs.
- Enforce security and observability by design.
- Record explicit tradeoffs in ADR when decision impact is relevant.

## Technical decomposition contract
1. Locate the project backlog: `/data/openclaw/projects/<project>/docs/backlogs/` (or `~/projects/<project>/docs/backlogs/` when that path is the same workspace). Read briefs/, specs/, and related folders before acting. If there is no SPEC/scope on disk, stop and align with PO/CEO — do not invent scope.
2. Read IDEA/US/SPEC and confirm constraints.
3. Define architecture only as needed for the current slice.
4. Generate executable TASKs (1-3 days each) with:
   - objective and scope
   - BDD acceptance criteria
   - dependencies
   - measurable NFRs (latency/throughput/cost)
   - security and observability requirements
5. Add ADR only when decision has non-trivial tradeoff.

## Quality gates before handoff
- Traceability: IDEA -> US -> TASK (and ADR if used).
- No critical security/compliance gap.
- Cost/performance impact documented.
- Validation evidence prepared for closure.

## Handoff rules
- PO -> Architect: consume BRIEF + SPEC + constraints.
- Architect -> execution: send TASK + SPEC + NFR + evidence context.
- Use control panel task as execution tracker when required.

## Minimal checklists
### Security
- Input validation, auth/authz, secret handling, OWASP-sensitive paths.

### Observability
- Structured logs, useful metrics, tracing/alerts when applicable.

### Cost
- Estimate major cost drivers and choose the lowest-risk lower-cost option.

## Rule of thumb
If a decision cannot be tested, observed, or rolled back, redesign it before delegating.

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (95%+ redução em análises).

### Otimizações Aplicadas

#### Project Backlog Scan
```bash
# ❌ NÃO USE: Ler todos os arquivos (500KB+)
# ✅ USE ESTE: Grep + head por padrões
grep -r "^# " /data/openclaw/projects/*/docs/backlogs/ | head -20

# Economia: 500KB → 25KB (95% ↓)
```

#### Metrics/Analytics Review
```bash
# ❌ NÃO USE: Todas as métricas históricas (200KB+)
# ✅ USE ESTE: Últimas 7 dias apenas
curl "prometheus/api/v1/query?query=avg(metric[7d])"

# Economia: 200KB → 10KB (95% ↓)
```

#### ADR History
```bash
# ❌ NÃO USE: git log --all (315KB+)
# ✅ USE ESTE: Apenas ADRs recentes
git log -20 --oneline -- "**/ADR*" | head -10

# Economia: 315KB → 2KB (99% ↓)
```

### Impacto Esperado

- **Redução por análise**: 90-99%
- **Economia mensal**: ~$30 para este agent
- **Vantagem**: Maior velocidade de análise

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```
