# Validação Fase 3 — Operações (030, 031, 127, 017 operacional)

**Objetivo:** Confirmar que o escopo da Fase 3 (Operações) está implementado e integrado no repositório.

Ref: [06-operacoes.md](../06-operacoes.md), [README.md](README.md) (Fase 3).

---

## Checklist por bloco

### 030 — Manual de primeiros socorros GPU

| Item | Entregável | Status |
|------|------------|--------|
| Doc dedicado | [docs/30-manual-primeiros-socorros-gpu.md](../30-manual-primeiros-socorros-gpu.md) — Fases 1–4, exceção à recuperação automática | OK |
| Script runbook | [scripts/first-aid-gpu.sh](../../scripts/first-aid-gpu.sh) — `--phase 1\|2\|3` ou interativo | OK |
| Referência 06 | Doc 06 mantém manual completo; 30 é referência canônica e script | OK |

### 031 — Prevenção e mitigação de riscos de infra

| Item | Entregável | Status |
|------|------------|--------|
| Doc riscos | [docs/31-prevencao-riscos-infra.md](../31-prevencao-riscos-infra.md) — tabela OOM GPU, lock, CPU, disco, custos API, deadlocks, persistência sandbox | OK |
| Ref segurança | Links para 05, 14, 06, 04 e 30 | OK |

### 127 — Disjuntor draft_rejected e autocura RAG

| Item | Entregável | Status |
|------|------------|--------|
| Script disjuntor | [scripts/disjuntor_draft_rejected.py](../../scripts/disjuntor_draft_rejected.py) — consumer group `disjuntor`, contagem por épico, 3 consecutivas → congelar, RAG health check, descongelar | OK |
| Script RAG health | [scripts/rag_health_check.py](../../scripts/rag_health_check.py) — determinístico: datas indexação vs main, estrutura pastas épico, `force_update` se conflito | OK |
| Redis init | [scripts/redis-streams-init.sh](../../scripts/redis-streams-init.sh) — consumer group **disjuntor** no stream `draft_rejected` | OK |
| Chaves Redis | `project:v1:orchestrator:draft_rejected_consecutive:{epic_id}`, `project:v1:orchestrator:epic_frozen:{epic_id}` | OK |

### 017 — Operacional (orçamento de degradação e desbloqueio)

| Item | Entregável | Status |
|------|------------|--------|
| Relatório degradação | Orquestrador escreve [docs/agents-devs/degradation-report-YYYY-MM-DD.md](../agents-devs/degradation-report-YYYY-MM-DD.md) ao pausar (DEGRADATION_REPORT_DIR) | OK |
| Script desbloqueio | [scripts/unblock-degradation.sh](../../scripts/unblock-degradation.sh) — DEL `orchestration:pause_degradation`; retomada só após comando explícito | OK |
| Orquestrador | [scripts/orchestrator_autonomy.py](../../scripts/orchestrator_autonomy.py) — gera relatório ao atingir threshold; chaves 44/phase2-config | OK |
| Doc 06/07 | Workflow de recuperação e comando de desbloqueio documentados em 06; 07 referência configurável | OK |

---

## Resumo

- **030:** Manual GPU em doc dedicado + script `first-aid-gpu.sh`.
- **031:** Tabela de riscos e mitigações em `31-prevencao-riscos-infra.md`.
- **127:** Disjuntor por épico (3 draft_rejected → congelar, RAG health check, descongelar); consumer group `disjuntor`; `rag_health_check.py` determinístico.
- **017:** Relatório de degradação automático ao pausar; `unblock-degradation.sh` para retomada explícita.

Próxima fase: **Fase 4** (Configuração / FinOps, etc.) conforme [README.md](README.md).
