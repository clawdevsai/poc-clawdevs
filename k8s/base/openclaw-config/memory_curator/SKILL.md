---
name: memory_curator_promotion
description: Skill de curadoria de memória para promoção de padrões cross-agent e relatório de saúde da memória
---

# SKILL.md - Memory_Curator

## Skill: promote_cross_agent_patterns

**Gatilho**: Cron diário às 2h ou chamada explícita pelo Arquiteto

**Passos**:
1. Ler todos os `/data/openclaw/memory/<id>/MEMORY.md` dos agentes ativos
2. Extrair seção `## Active Patterns` de cada arquivo
3. Usar LLM para agrupar padrões semanticamente similares entre agentes
4. Para grupos com ≥3 agentes distintos: promover para SHARED_MEMORY.md
5. Atualizar MEMORY.md dos agentes de origem (mover para Archived)
6. Logar resultado em `/data/openclaw/backlog/status/memory-curator.log`

**Formato de entrada esperado nos MEMORY.md**:
```
- [PATTERN] <descrição> | Descoberto: YYYY-MM-DD | Fonte: <task-id>
```

**Formato de saída em SHARED_MEMORY.md**:
```
- [GLOBAL] <descrição consolidada> | Promovido: YYYY-MM-DD | Origem: <agente1>, <agente2>, <agente3>
```

**Formato de arquivamento nos MEMORY.md dos agentes**:
```
- [ARCHIVED] <descrição original> | Arquivado: YYYY-MM-DD | Motivo: Promovido para SHARED_MEMORY
```

## Skill: report_memory_health

**Gatilho**: Ao final de cada ciclo de promoção

**Saída**: Log estruturado em `/data/openclaw/backlog/status/memory-curator.log` com:
- Timestamp ISO8601
- Agentes processados
- Total de padrões coletados
- Padrões promovidos (N novos + N atualizados)
- Padrões arquivados
- Erros
