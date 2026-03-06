# Relatório de Auditoria e Refatoração — ClawDevs AI

**Data**: 2026-03-06  
**Status**: Concluído  

---

## Passo 1 — Auditoria e Limpeza

### Código Morto Removido

| Item | Quantidade | Ação |
|------|-----------|------|
| Scripts duplicados na raiz `/scripts/` | 21 | Removidos (versões organizadas em subdirs permanecem) |
| Arquivos de teste em local incorreto | 2 | Movidos: `app/features/test_*.py` → `tests/` |
| Referências "Fase X" violando naming rules | 32 ocorrências em 21 arquivos | Removidas automaticamente |

**Scripts duplicados removidos da raiz** (cópias organizadas em subdirs mantidas):
- `ciso_local_scan.sh` → `scripts/ops/`
- `devops_compact_safe.sh` → `scripts/ops/`
- `first-aid-gpu.sh` → `scripts/ops/`
- `k8s-openclaw-secret-from-env.sh` → `scripts/openclaw/`
- `m4a_to_md.sh` → `scripts/transcription/`
- `ollama-ensure-cloud-auth.sh` → `scripts/openclaw/`
- `ollama-signin.sh` → `scripts/openclaw/`
- `owasp-pre-commit.sh` → `scripts/ops/`
- `redis-streams-init.sh` → `scripts/cluster/`
- `reset_agent_memory.sh` → `scripts/utils/`
- `run-openclaw-telegram-slack-ollama.sh` → `scripts/openclaw/`
- `run_validacao_finops_po.sh` → `scripts/utils/`
- `secrets-from-env.sh` → `scripts/cluster/`
- `slack-openclaw-check.sh` → `scripts/ops/`
- `test_github_access.sh` → `scripts/utils/`
- `test_github_create_issue.sh` → `scripts/ops/`
- `test_minikube_slot.sh` → `scripts/ops/`
- `unblock-degradation.sh` → `scripts/ops/`
- `up-all.sh` → `scripts/cluster/`
- `validate-token-rotation.sh` → `scripts/ops/`
- `validate_reverse_po_after_summary.sh` → `scripts/ops/`

---

## Passo 2 — Refatoração

### Arquivos Criados

| Arquivo | Motivo |
|---------|--------|
| `app/shared/redis_client.py` | Centraliza `get_redis()` duplicado em 7 módulos |
| `requirements.txt` | Dependências Python ausentes — bloqueador de CI/CD |
| `tests/__init__.py` | Estrutura de testes correta |

### Decisões Arquiteturais

**`get_redis()` centralizado**: A função foi definida 7 vezes em módulos diferentes (`orchestration.py`, `acefalo_redis.py`, `disjuntor_draft_rejected.py`, `gpu_lock.py`, `gateway_token_bucket.py`, `working_buffer_ttl.py`, `redis_buffer_writer.py`). Centralizar em `shared/redis_client.py` segue o princípio DRY e facilita mudanças de configuração (ex.: adicionar TLS ou connection pool).

**Remoção de "Fase X"**: A regra `.cursor/rules/naming-no-fase-phase.mdc` proíbe referências "Fase" ou "Phase" no código. Foram 32 ocorrências em docstrings — removidas sem impacto funcional.

**`requirements.txt`**: Indispensável para CI/CD (GitHub Actions, Docker build). Sem ele, é impossível reproduzir o ambiente em outro host.

---

## Passo 3 — Mission Control (novo admin-ui)

### Por que "Mission Control"?

> Nome escolhido por comunicar exatamente o papel do Diretor: supervisionar, coordenar e intervir em missões de desenvolvimento autônomo — como uma Central de Missões supervisiona uma operação espacial.

### O que mudou em relação ao kanban-ui

| Kanban UI (antes) | Mission Control (depois) |
|-------------------|--------------------------|
| Estados: New, Shortlisted, Interviewed | Estados: Backlog, Em Andamento, Em Revisão, QA, Concluído |
| "Senior Java Developer" (contratação) | Time de 9 agentes de IA |
| "Invite candidate" | Criação de tarefas para o time |
| Sem monitoramento de agentes | AgentGrid com 9 cards e heartbeat |
| Sem custo de tokens | TokenPanel com teto FinOps |
| Sem intervenção | InterventionModal completo |
| 6 componentes | 8 componentes + 4 libs |

### Novos endpoints na kanban-api

| Endpoint | Método | Função |
|----------|--------|--------|
| `/api/agents` | GET | Status de todos os 9 agentes |
| `/api/agents/<id>/heartbeat` | POST | Agentes registram presença |
| `/api/tokens` | GET | Uso de tokens por agente |
| `/api/tokens/<id>` | POST | Agentes registram uso |
| `/api/interventions` | GET | Histórico de intervenções |
| `/api/interventions` | POST | Diretor intervém em tarefa |

### Estrutura do Mission Control

```
mission-control/
├── app/
│   ├── globals.css         # Design dark, scrollbars, dots de status
│   ├── layout.tsx          # Metadata e HTML root
│   └── page.tsx            # Home: 3 views (Dashboard/Board/FinOps)
├── components/
│   ├── agents/
│   │   ├── AgentCard.tsx   # Card de agente com status, tarefa e tokens
│   │   └── AgentGrid.tsx   # Grid 3×3 dos 9 agentes, auto-refresh 15s
│   ├── tasks/
│   │   ├── TaskCard.tsx    # Card de tarefa com prioridade e intervenção
│   │   ├── MissionBoard.tsx # Kanban com 5 estados de dev workflow
│   │   └── InterventionModal.tsx # Modal de intervenção do Diretor
│   └── shared/
│       ├── StatusDot.tsx   # Indicador de status (active/idle/offline)
│       ├── TopBar.tsx      # Header com tabs e status de pipeline
│       └── ActivityFeed.tsx # Log de atividades em tempo real
├── lib/
│   ├── api.ts              # Cliente tipado para kanban-api
│   ├── useSSE.ts           # Hook para Server-Sent Events
│   └── constants.ts        # AGENT_META, estados, cores, ações
├── Dockerfile              # Build multi-stage para produção
├── next.config.mjs         # Proxy para kanban-api
└── README.md               # Documentação do painel
```

---

## Passo 4 — Documentação

### Arquivos Atualizados

| Arquivo | O que mudou |
|---------|------------|
| `README.md` | Reescrito: objetivo central, arquitetura, quickstart, estrutura de pastas, tabela de stack |
| `mission-control/README.md` | Criado: explica nomenclatura, funcionalidades, variáveis, deploy |
| `AUDIT_REPORT.md` | Este arquivo |

---

## Kanban UI (mantido)

O `kanban-ui/` original foi **mantido intacto** para não quebrar deploys existentes.  
O `mission-control/` substitui-o como painel oficial do Diretor.  
Para migrar: ajuste o `Makefile` target `kanban-image` para apontar para `mission-control/`.

---

## Próximas Ações Recomendadas

1. **Migrar `get_redis()` nos módulos existentes** para importar de `shared.redis_client` (mudança mecânica, baixo risco)
2. **Adicionar GitHub Actions** (`.github/workflows/test.yml`) para rodar `pytest tests/` em cada PR
3. **Deprecar `kanban-ui/`** após validar o Mission Control em staging
4. **Adicionar heartbeat** nos agentes Python (`POST /api/agents/{id}/heartbeat` a cada 60s)
5. **Adicionar registro de tokens** nos wrappers de chamada Ollama (`POST /api/tokens/{agent}`)
