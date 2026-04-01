# Context Mode Agent Helpers

Guia de otimização de context-mode para todos os agents OpenClaw.

## Visão Geral

Cada agent executa ferramentas (`npm`, `git`, `kubectl`, `docker`, etc) que produzem outputs grandes. O context-mode comprime automaticamente outputs > 5KB em **95-98% de compressão**.

Para **maximizar** a compressão, aplique os padrões abaixo em cada skill.

---

## Padrões de Otimização por Ferramenta

### 1. NPM (Node Package Manager)

**Problem**: `npm list` = 142KB → 97.9% compressão

**Padrão Otimizado**:
```bash
# ❌ ANTES: Retorna árvore completa
npm list

# ✅ DEPOIS: Apenas dependências diretas
npm list --depth=0

# ✅ Ou com filtro
npm list --depth=0 | grep -E "^├|^└|^$"
```

**Aplicar em**:
- `dev_backend_implementation`
- `dev_frontend_implementation`
- `dev_mobile_implementation`
- `devops_sre_operations` (para validações)

---

### 2. GIT (Version Control)

**Problem**: `git log` = 315KB → 99.4% compressão

**Padrão Otimizado**:
```bash
# ❌ ANTES: Todos os commits com diffs completos
git log --all

# ✅ DEPOIS: Últimos 20 commits, oneline
git log -20 --oneline

# ✅ Ou com filtro por tempo
git log --since="24 hours ago" --oneline

# ✅ Para status
git status -s  # Short format, não full
```

**Aplicar em**:
- `dev_backend_implementation`
- `dev_frontend_implementation`
- `dev_mobile_implementation`
- `security_engineer_analysis`

---

### 3. KUBECTL (Kubernetes)

**Problem**: `kubectl logs` = 500KB → 98% compressão

**Padrão Otimizado**:
```bash
# ❌ ANTES: Logs completos
kubectl logs -n production pod-name

# ✅ DEPOIS: Últimas 100 linhas, apenas erros
kubectl logs -n production pod-name --tail=100 | grep -E "ERROR|CRITICAL|Exception"

# ✅ Ou com filtro de tempo
kubectl logs -n production pod-name --since=10m

# ✅ Para múltiplos pods
kubectl logs -n production -l app=myapp --tail=50 --timestamps=false
```

**Aplicar em**:
- `devops_sre_operations`
- `database_healer_repair` (logs de DB)

---

### 4. DOCKER (Container Management)

**Problem**: `docker ps -a` = 120KB → 95.8% compressão

**Padrão Otimizado**:
```bash
# ❌ ANTES: Todos os campos, histórico completo
docker ps -a

# ✅ DEPOIS: Apenas containers ativos, campos essenciais
docker ps --format="{{.ID}} {{.Status}} {{.Names}}"

# ✅ Com filtros
docker ps --format="{{.ID}} {{.Status}} {{.Names}}" --filter "status=running"

# ✅ Para logs
docker logs container-name --tail=50 --timestamps=false
```

**Aplicar em**:
- `devops_sre_operations`
- `database_healer_repair`
- `agent_reviver_recovery`

---

### 5. POSTGRES/MySQL (Database)

**Problem**: `SELECT *` em tabelas grandes = 500KB+ → 98%+ compressão

**Padrão Otimizado**:
```sql
-- ❌ ANTES: Dump completo
pg_dump database_name

-- ✅ DEPOIS: Estrutura apenas
pg_dump -s database_name

-- ✅ Ou tabelas específicas
pg_dump -t table_name -n public database_name

-- ✅ Para queries
SELECT column1, column2 FROM table LIMIT 100;  -- Limite resultados
SELECT COUNT(*) FROM table;  -- Contar vs listar todos
```

**Aplicar em**:
- `dba_data_engineer_operations`
- `database_healer_repair`
- `memory_curator_promotion`

---

### 6. PROMETHEUS/METRICS (Monitoring)

**Problem**: Todas as métricas = 200KB+ → 95%+ compressão

**Padrão Otimizado**:
```bash
# ❌ ANTES: Todas as métricas
curl prometheus:9090/api/v1/query_range?query=...

# ✅ DEPOIS: Período curto, apenas métricas importantes
curl "prometheus:9090/api/v1/query?query=up&time=now"

# ✅ Com agregação
curl "prometheus:9090/api/v1/query?query=sum(rate(requests[5m]))"
```

**Aplicar em**:
- `devops_sre_operations`
- `arquiteto_analysis`

---

### 7. GH CLI (GitHub)

**Problem**: `gh pr list` = 280KB → 98.2% compressão

**Padrão Otimizado**:
```bash
# ❌ ANTES: Todos os campos
gh pr list

# ✅ DEPOIS: Apenas campos necessários
gh pr list --json title,number,state --limit 10

# ✅ Com filtro de status
gh pr list --state open --json title,number,author

# ✅ Para issues
gh issue list --limit 20 --json number,title,state
```

**Aplicar em**:
- `dev_backend_implementation`
- `dev_frontend_implementation`
- `qa_engineer_validation`
- `po_product_roadmap`

---

## Estratégia de Implementação por Agent

### **Tier 1: Máximo Impacto** (Semana 1)
Agents que executam ferramentas pesadas frequentemente:

1. **dev_backend_implementation** → NPM + GIT (principal dev)
2. **devops_sre_operations** → KUBECTL + DOCKER + PROMETHEUS
3. **memory_curator_promotion** → DATABASE queries
4. **database_healer_repair** → POSTGRESQL + DOCKER logs

### **Tier 2: Impacto Alto** (Semana 1-2)
2. **dev_frontend_implementation** → NPM + GIT
3. **dev_mobile_implementation** → NPM + GIT
4. **dba_data_engineer_operations** → DATABASE heavy
5. **qa_engineer_validation** → GH CLI + Database queries

### **Tier 3: Impacto Médio** (Semana 2)
6. **security_engineer_analysis** → GIT + Database queries
7. **arquiteto_analysis** → Prometheus metrics
8. **agent_reviver_recovery** → DOCKER logs
9. **ceo_orchestration** → Aggregated queries
10. **po_product_roadmap** → GH CLI queries

### **Tier 4: Impacto Baixo** (Semana 2-3)
11. **final_consolidation** → Aggregated reports
12. **ux_designer_implementation** → File listings
13. **agent_reviver** → Fallback agent (lower volume)

---

## Como Aplicar em Cada Skill

### Adicionar na Seção "Quality Gates" do SKILL.md:

```markdown
## Context Mode Optimization

Este skill foi otimizado para **context-mode compression**:

### Ferramentas Otimizadas
- **npm list** → Use `npm list --depth=0`
- **git log** → Use `git log -20 --oneline`
- **kubectl logs** → Filtre por `grep ERROR`
- **docker ps** → Use `--format` customizado

### Impacto Esperado
- Redução de tokens por execução: ~70-95%
- Economia mensal: ~$40 por agent (15 agents = $600+)
- Sem perda de informação: Outputs otimizados retornam dados essenciais

### Verificar Compressão
Confira `/api/context-mode/metrics` para validar que esta skill está contribuindo para a compressão.
```

---

## Métricas Esperadas

Após implementação completa em todos os 15 agents:

| Métrica | Antes | Depois | Economia |
|---------|-------|--------|----------|
| Tokens/hora | 529K | 13K | **97%** ↓ |
| Custo/mês | $576 | $14 | **$562 ↓** |
| Avg compression ratio | 1.0 | 0.025 | **97.5% salvo** |
| Per-operation reduction | - | 70-99% | **95% avg** |

---

## Checklist de Implementação

Para cada agent (15 total):

- [ ] Identificar ferramentas usadas (npm, git, kubectl, etc)
- [ ] Aplicar padrões otimizados no SKILL.md
- [ ] Atualizar exemplos com comandos otimizados
- [ ] Testar execução com primeiro ciclo
- [ ] Validar no `/api/context-mode/metrics`
- [ ] Documento os resultados no REFACTORING_ANALYSIS.md

---

## Recursos

- **Hook**: `/control-panel/backend/app/hooks/tool_executed.py`
- **API**: `GET /api/context-mode/metrics` e `/api/context-mode/status`
- **Config**: `/docker/base/openclaw-config/shared/CONTEXT_MODE_HOOKS_CONFIG.yaml`
- **Suporte**: Veja `CONTEXT_MODE_README.md`
