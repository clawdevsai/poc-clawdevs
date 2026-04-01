---
name: memory_curator_promotion
description: Memory curation skill for promoting cross-agent standards and memory health reporting
---

# SKILL.md - Memory_Curator

## Skill: promote_cross_agent_patterns

**Trigger**: Daily Cron at 2am or explicit call by Architect

**Steps**:
1. Read all `/data/openclaw/memory/<id>/MEMORY.md` from active agents
2. Extract `## Active Patterns` section from each file
3. Use LLM to group semantically similar patterns between agents
4. For groups with ≥3 different agents: promote to SHARED_MEMORY.md
5. Update MEMORY.md of source agents (move to Archived)
6. Log result at `/data/openclaw/backlog/status/memory-curator.log`

**Expected input format in MEMORY.md**:
```
- [PATTERN] <descrição> | Descoberto: YYYY-MM-DD | Fonte: <task-id>
```

**Output format in SHARED_MEMORY.md**:
```
- [GLOBAL] <descrição consolidada> | Promovido: YYYY-MM-DD | Origem: <agente1>, <agente2>, <agente3>
```

**Archiving format in agents' MEMORY.md**:
```
- [ARCHIVED] <descrição original> | Arquivado: YYYY-MM-DD | Motivo: Promovido para SHARED_MEMORY
```

## Skill: report_memory_health

**Trigger**: At the end of each promotion cycle

**Output**: Log structured in `/data/openclaw/backlog/status/memory-curator.log` with:
- Timestamp ISO8601
- Agents processed
- Total patterns collected
- Promoted patterns (N new + N updated)
- Archived patterns
- Errors

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (90-98% redução ao indexar/buscar memórias).

### Otimizações Aplicadas

#### Database Queries (Memory Lookups)
```bash
# ❌ NÃO USE: Carregar 300KB de memórias completas
SELECT * FROM memories WHERE agent_id = ?;

# ✅ USE ESTE: Usar ctx_index + ctx_search
ctx_index("/data/openclaw/memories/")
results = ctx_search("PostgreSQL connection pool issues")  # Apenas snippets relevantes

# Economia: 300KB → 20KB (93% ↓)
# Tokens salvos: ~1350 por lookup
```

#### Memory File Scans
```bash
# ❌ NÃO USE: Ler toda MEMORY.md de cada agent (50+ arquivos × 5KB)
for f in /data/openclaw/memory/*/MEMORY.md; do cat $f; done

# ✅ USE ESTE: Usar grep + head para apenas patterns
for f in /data/openclaw/memory/*/MEMORY.md; do grep "^\- \[PATTERN\]" $f | head -5; done

# Economia: 250KB → 25KB (90% ↓)
```

### Impacto Esperado

- **Redução de tokens por ciclo**: 90-93%
- **Economia mensal**: ~$50 (índexação semanal)
- **Resultado**: Memoria mais rápida, busca inteligente

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```
