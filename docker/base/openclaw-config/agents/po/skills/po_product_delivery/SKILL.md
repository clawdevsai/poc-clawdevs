---
name: po_product_delivery
description: Product delivery skill for backlog, user stories, sequencing and handoff to the Architect
---

# Product Delivery

Use this skill when an order requires backlog design, feature breakdown, delivery sequencing or acceptance criteria.

Exit checklist:
- problem statement
- target result
- idea file approved at `/data/openclaw/backlog/idea`
- user separate stories at `/data/openclaw/backlog/user_story`
- handoff for Architect with technical drawing and tasks
- tasks prioritized in `/data/openclaw/backlog/tasks`
- acceptance criteria
- risks and dependencies
- files generated in `/data/openclaw/backlog`

---

## User Story Template

Use this template when creating files in `/data/openclaw/backlog/user_story/US-XXX-<slug>.md`.

```md
# US-XXX - <Titulo curto>

## Contexto
<Contexto do problema, usuario e situacao atual.>

## Historia do usuario
Como <tipo de usuario>,
quero <acao ou capacidade>,
para <beneficio ou resultado>.

## Escopo
- Inclui: <itens dentro do escopo>
- Nao inclui: <itens fora do escopo>

## Criterios de aceitacao
1. <criterio testavel>
2. <criterio testavel>
3. <criterio testavel>

## Requisitos de UX (se aplicavel)
- <telas, componentes, fluxos>

## Analytics (se aplicavel)
- Eventos: <eventos a instrumentar>
- Funil: <etapas do funil>
- Experimentos: <A/B, feature flag, rollout>

## Dependencias
- <dependencia tecnica, negocio ou time>

## Riscos e mitigacoes
- <risco> -> <mitigacao>

## Metricas de sucesso
- <metrica> com alvo <valor>

## Notas
- <observacoes adicionais>
```

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (98%+ redução em backlog queries).

### Otimizações Aplicadas

#### GitHub Issues/PRs Query
```bash
# ❌ NÃO USE: gh issue list (retorna tudo)
# ✅ USE ESTE: Apenas campos necessários + assignees simplificado
# Nota: no --json é "assignees" (array). "--assignee" é só filtro, não campo JSON.
gh issue list --json number,title,assignees --limit 50 --jq '.[] | {number, title, assignees: ([.assignees[].login] // [])}'

# Economia: 280KB → 5KB (98% ↓)
```

#### Backlog File Scans
```bash
# ❌ NÃO USE: Ler TODOS os backlog arquivos (200KB+)
# ✅ USE ESTE: Listar apenas títulos
grep "^# " /data/openclaw/backlog/*/*.md | head -20

# Economia: 200KB → 10KB (95% ↓)
```

#### Analytics Data
```bash
# ❌ NÃO USE: Dump completo de eventos
# ✅ USE ESTE: Resumo da semana
curl /analytics/summary?period=7d

# Economia: 150KB → 10KB (93% ↓)
```

### Impacto Esperado

- **Redução por backlog review**: 93-98%
- **Economia mensal**: ~$20 para este agent
- **Vantagem**: Queries mais rápidas

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```
