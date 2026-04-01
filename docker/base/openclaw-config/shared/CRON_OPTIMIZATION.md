# Cron Job Optimization - Phase 4 Task 2
**Data:** 2026-04-01
**Status:** Planejamento
**Objetivo:** Comprimir outputs de cron jobs de alto volume (70-90% economia)

---

## 📋 Visão Geral

### Problema
Cron jobs (cleanups, reports, analytics) geram outputs de **50-500KB** cada ciclo. Sem compress\u00e3o:
- `daily_cleanup`: ~50-100KB (5 execuções/semana)
- `memory_consolidation`: ~150-200KB (1 execução/dia)
- `cron_health_check`: ~50KB (3 execuções/dia)
- **Total mensal**: ~45-60MB de output não comprimido

Com context-mode compress\u00e3o: **70-90% redução** esperada.

### Escopo
| Componente | Baseline | Esperado | Economia |
|-----------|----------|----------|----------|
| Cron outputs | 200KB média | 20-60KB | 70-90% ↓ |
| Tokens/ciclo | 50K | 5K | 90% ↓ |
| Mensal | ~$3 | ~$0.30 | 90% ↓ |

---

## 🎯 Implementação

### Opção 1: Compress com Context-Mode CLI

```bash
# Em vercel.json, adicionar crons:
{
  "crons": [
    {
      "path": "/api/cron/daily-cleanup",
      "schedule": "0 3 * * *"
    },
    {
      "path": "/api/cron/memory-consolidation",
      "schedule": "0 2 * * *"
    }
  ]
}

# Em /api/cron/[name]/route.ts:
export async function GET(req: Request) {
  const output = await runCleanupProcess();

  // Compress com context-mode
  const compressed = await ctx_execute("shell", `echo "${output}" | npx context-mode execute --compress`);

  // Store compressed output
  return Response.json({ status: "ok", output: compressed });
}
```

### Opção 2: Batch Compression Service (Recomendado)

**File:** `app/services/cron_optimization.py`

```python
from app.services.cron_optimization import get_cron_optimization_service

async def run_cron_jobs():
    service = get_cron_optimization_service()

    # Executar múltiplos jobs e comprimir batch
    jobs = [
        {"name": "cleanup", "output": run_cleanup(), "type": "cleanup"},
        {"name": "report", "output": run_report(), "type": "report"},
        {"name": "health", "output": check_health(), "type": "analytics"}
    ]

    # Comprimir todos em uma única passagem
    result = await service.compress_batch(jobs)

    # result.overall_compression_ratio = 0.85 (85% comprimido)
    # result.total_compressed_bytes = 30KB (de 200KB original)
```

### Opção 3: Hook-Level Compression

**File:** `app/hooks/tool_executed.py`

Adicionar ao hook `tool.executed`:
```python
async def on_tool_executed(event):
    if event.get("tool_name") == "cron":
        output = event.get("output")

        # Se output > 10KB, comprimir automaticamente
        if len(output) > 10240:
            compressed = await compress_output(output, "cron")
            event["output"] = compressed
            event["compression_ratio"] = calculate_ratio(output, compressed)
```

---

## 📊 Padrões por Tipo de Job

### 1. Cleanup Jobs
```bash
# Antes (142KB):
$ npm run cleanup:full
[cleaning logs...]
[processing 10000 files...]
[deleting cache...]
done in 5.2s

# Depois com --summary-only (8KB, 94% redução):
$ npm run cleanup:summary-only
[✓] Cleaned 10000 files, freed 2GB
[✓] Cache cleared, freed 500MB
[✓] Logs archived, freed 1GB
```

**Implementação:**
```json
{
  "scripts": {
    "cleanup:full": "node scripts/cleanup.js",
    "cleanup:summary-only": "node scripts/cleanup.js --summary"
  }
}
```

### 2. Report Jobs
```bash
# Antes (315KB):
metrics: {...1000 lines...}

# Depois com aggregation (5KB, 98% redução):
- Total executions: 10,234
- Avg duration: 2.3s
- Success rate: 99.8%
- Top 5 slowest: [...]
```

### 3. Analytics/Health Checks
```bash
# Antes (200KB):
Pod 1: healthy
Pod 2: healthy
... x100 pods

# Depois (3KB, 98% redução):
- Healthy pods: 100/100
- Avg CPU: 45%
- Avg Memory: 62%
- Incidents: 0
```

---

## 🔧 Integração com Vercel

### Step 1: Update package.json
```json
{
  "dependencies": {
    "context-mode": "^1.0.0"
  }
}
```

### Step 2: Create /api/cron/[name]/route.ts
```typescript
import { CronOptimizationService } from '@/app/services/cron_optimization';

export async function GET(request: Request) {
  const service = CronOptimizationService.getInstance();

  // Execute cron
  const output = await executeCronJob('daily-cleanup');

  // Compress
  const result = await service.compress_cron_output(
    'daily-cleanup',
    output,
    'cleanup'
  );

  // Return compressed
  return Response.json(result);
}

// Vercel cron trigger
export const revalidate = 0; // No caching
export const runtime = 'nodejs';
```

### Step 3: Configure vercel.json
```json
{
  "crons": [
    {
      "path": "/api/cron/daily-cleanup",
      "schedule": "0 3 * * *"
    },
    {
      "path": "/api/cron/memory-consolidation",
      "schedule": "0 2 * * *"
    }
  ]
}
```

---

## 📈 Monitoramento

### Endpoint: `/api/context-mode/cron-metrics`

```json
{
  "status": "success",
  "total_cron_executions": 47,
  "total_bytes_processed": 9400,
  "total_bytes_compressed": 940,
  "average_compression_ratio": 0.90,
  "tokens_saved_estimate": 235,
  "estimated_monthly_savings": 0.24
}
```

### Dashboard
- Cron Executions (count/day)
- Compression Ratio (avg %)
- Tokens Saved (estimate/execution)
- Monthly Savings ($)

---

## ✅ Checklist de Implementação

- [ ] Add context-mode ao package.json
- [ ] Criar CronOptimizationService (cron_optimization.py)
- [ ] Criar /api/cron/[name] routes
- [ ] Configurar vercel.json crons
- [ ] Estender API para /context-mode/cron-metrics
- [ ] Adicionar testes unitários (test_cron_compression.py)
- [ ] Executar testes de integração
- [ ] Monitor em produção por 48h
- [ ] Validar economia vs baseline
- [ ] Documentar padrões por job type

---

## 🎯 Success Criteria

| Métrica | Target | Status |
|---------|--------|--------|
| Compression ratio | >70% | ✓ Esperado |
| Job execution time | <3s | ✓ Esperado |
| Fallback reliability | 100% | ✓ Esperado |
| Data loss | 0% | ✓ Esperado |
| Monthly savings | >$1 | ✓ Esperado |

---

## 📚 Referências

- Context-Mode: `CONTEXT_MODE_AGENT_HELPERS.md`
- Memory Indexing: `app/services/memory_indexing.py` (Task 1)
- Dashboard: `app/api/context_mode.py` (Task 3)
- Tests: `tests/integration/test_cron_compression.py` (Task 4)
