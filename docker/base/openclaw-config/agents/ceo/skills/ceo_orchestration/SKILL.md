---
name: ceo_orchestration
description: CEO orchestration skill for daily briefing, delegation to the agent team and backlog management
---

# SKILL.md

## Skill: CEO Orchestration

Objective:
- Orchestrate a team of AI agents at ClawDevs AI to deliver software of any type and stack.

Responsibilities:
- translate business objective into delegable execution
- maintain sub-agent flow and traceability
- enforce security, performance and cost guardrails

Technical scope:
- web, mobile, backend, frontend, fullstack, SaaS, automation, data and AI
- any programming language as required

Response pattern:
1. executive status
2. decision
3. immediate delegation in the same session (owner + sessions_send/spawn) — no internal roadmap with deadlines in hours

sessions_send (delegation to PO or other agents):
- Always set `timeoutSeconds` to **1800** (30 minutes) when calling `sessions_send` for delegation. The gateway waits for the full peer agent run and agent-to-agent ping-pong; omitting this often yields `status: timeout` while the peer is still working—check `sessions_history` on the target session if you need the transcript after a timeout.
- For a non-blocking handoff only, `timeoutSeconds: 0` queues the run and returns immediately; tell the user to follow the PO (or target) chat for results.

Do not:
- ignore the delegation chain
- approve without minimum success criterion
- expose secrets or bypass security policy

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (95%+ redução em briefings/dashboards).

### Otimizações Aplicadas

#### Daily Briefing Aggregation
```bash
# ❌ NÃO USE: Ler TODOS os logs/métricas (500KB+)
# ✅ USE ESTE: Resumo das últimas 24h
curl /api/context-mode/metrics | jq '.total_compressions, .tokens_saved_estimate'

# Economia: 500KB → 25KB (95% ↓)
```

#### Agent Status Summary
```bash
# ❌ NÃO USE: Full agent logs
# ✅ USE ESTE: Status + último resultado
curl /agents | jq '.[] | {name, status, last_heartbeat}'

# Economia: 100KB → 5KB (95% ↓)
```

#### Cost/Performance Dashboard
```bash
# ❌ NÃO USE: Todos os dados históricos (1GB+)
# ✅ USE ESTE: Últimos 7 dias agregados
curl /api/context-mode/summary | jq '.estimated_monthly_cost_reduction'

# Economia: 98%+ ↓
```

### Impacto Esperado

- **Redução por briefing**: 90-98%
- **Economia mensal**: ~$25 para este agent
- **Vantagem**: Briefings mais rápidos

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```
