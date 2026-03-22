# ClawDevs AI — Control Panel Design

**Date:** 2026-03-22
**Status:** Approved
**Reference:** openclaw-mission-control (Opção A — melhorado)

---

## Sumário

Painel de controle customizado embutido dentro do cluster Kubernetes do ClawDevs AI. Baseado na arquitetura do openclaw-mission-control, melhorado em performance, visual e custo zero. Cobre observabilidade, gestão operacional e fluxo SDD completo.

---

## Stack — Versões Estáveis Validadas (Mar 2026)

### Backend
| Tecnologia | Versão |
|---|---|
| Python | 3.12 |
| FastAPI | 0.135.1 |
| SQLModel | 0.0.37 |
| Alembic | 1.18.4 |
| uv | 0.10.12 |

### Frontend
| Tecnologia | Versão |
|---|---|
| Next.js | 16.2.0 |
| React | 19.2.4 |
| Tailwind CSS | 4.2.2 |
| shadcn/ui | 4.1.0 |
| TanStack Query | 5.94.5 |
| TanStack Table | 8.21.3 |
| Orval | 8.5.3 |
| Recharts | 3.8.0 |

### Infraestrutura
| Tecnologia | Versão |
|---|---|
| PostgreSQL | 18.3 (`postgres:18-alpine`) |
| Redis | 8.6.1 (`redis:8-alpine`) |

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   frontend   │    │   backend    │    │  openclaw    │  │
│  │  Next.js 16  │───▶│  FastAPI     │───▶│  gateway     │  │
│  │  React 19    │    │  Python 3.12 │    │  :18789      │  │
│  │  :3000       │    │  :8000       │    └──────────────┘  │
│  └──────────────┘    └──────┬───────┘                       │
│                             │                               │
│              ┌──────────────┼──────────────┐                │
│              ▼              ▼              ▼                │
│     ┌──────────────┐ ┌──────────┐ ┌─────────────┐         │
│     │  PostgreSQL  │ │  Redis   │ │  K8s API    │         │
│     │  18          │ │  8       │ │  in-cluster  │         │
│     │  StatefulSet │ │  Deploy  │ └─────────────┘         │
│     └──────────────┘ └──────────┘                          │
│                                                             │
│  NodePort 31880 ──▶ frontend :3000                         │
│  NodePort 31881 ──▶ backend  :8000                         │
└─────────────────────────────────────────────────────────────┘
```

### Kubernetes Resources

| Recurso | Kind | CPU Request | RAM Request |
|---|---|---|---|
| `clawdevs-panel-backend` | Deployment (1 replica) | 250m | 512Mi |
| `clawdevs-panel-frontend` | Deployment (1 replica) | 100m | 256Mi |
| `clawdevs-panel-db` | StatefulSet + 10Gi PVC | 250m | 512Mi |
| `clawdevs-panel-redis` | Deployment | 100m | 128Mi |
| `clawdevs-panel-worker` | Deployment (background) | 100m | 256Mi |

**Total adicional:** ~800m CPU + ~1.7Gi RAM

---

## Banco de Dados

### Tabelas

```sql
users               -- usuários locais do painel (sem Clerk)
agents              -- 13 agentes + status, heartbeat, cron info
sessions            -- referências às sessões OpenClaw
approvals           -- fila de aprovações com rubric scores
tasks               -- work items (sync GitHub Issues)
sdd_artifacts       -- BRIEF/SPEC/CLARIFY/PLAN/TASK/VALIDATE
memory_entries      -- espelho estruturado do sistema de memória
cron_executions     -- histórico de execuções de cron jobs
activity_events     -- audit trail de todas as ações
metrics             -- métricas agregadas por agente/período
```

### Decisões de Design

- **JSONB** para `payload` e `rubric_scores` — flexível e indexável no PostgreSQL 18
- **`memory_entries`** espelha os arquivos MEMORY.md com busca fulltext via `tsvector`
- **`sdd_artifacts`** sincroniza com arquivos do backlog via filesystem watcher
- **`cron_executions`** é a base para analytics de confiabilidade dos agentes
- **Sem multi-tenancy** — cluster é single-org, sem overhead de `organization_id`
- **Auth local JWT** — sem Clerk, custo zero, bearer token por usuário

---

## Páginas e Features

| Rota | Feature |
|---|---|
| `/` | Dashboard — overview, métricas 24h, feed de atividade, grid de agentes |
| `/agents` | Lista dos 13 agentes com avatar, status, heartbeat, modelo |
| `/agents/[slug]` | Perfil: identidade, métricas, sessões, memória, cron, aprovações |
| `/sessions` | Browser paginado de sessões OpenClaw com busca fulltext |
| `/sessions/[id]` | Conversa completa renderizada em Markdown, timeline de tool calls |
| `/approvals` | Kanban: Pendente / Aprovado / Rejeitado, aprovar/rejeitar com justificativa |
| `/tasks` | Board + List de tasks (sync GitHub Issues), criar manualmente |
| `/sdd` | Browser de artefatos SDD com timeline BRIEF→SPEC→PLAN→TASK→VALIDATE |
| `/sdd/[id]` | Artefato completo, editor inline para BRIEF, histórico de versões |
| `/memory` | Viewer hierárquico: Global → Por Agente, busca fulltext, promoção manual |
| `/crons` | Grid de 9 crons: próxima execução, histórico, sparkline, trigger manual |
| `/cluster` | Status de pods/PVCs/events K8s, logs ao vivo via WebSocket |
| `/settings` | Auth, tokens, configurações do gateway, info do cluster |

---

## Realtime

| Canal | Tecnologia | Uso |
|---|---|---|
| Status dos agentes | WebSocket | heartbeat a cada 30s |
| Aprovações novas | WebSocket | push imediato |
| Logs ao vivo (cluster) | WebSocket streaming | pod logs |
| Memória nova | SSE | filesystem watcher |
| Cron execução | SSE | progresso em tempo real |

Reconexão automática no frontend com backoff exponencial.

---

## Integrações

| Integração | Protocolo | Auth | Direção |
|---|---|---|---|
| OpenClaw Gateway | HTTP + SSE | Bearer token existente | Backend → Gateway |
| Memória (PVC) | Filesystem watch (`watchdog`) | ReadOnly mount | Backend lê |
| GitHub Issues | REST API | GITHUB_TOKEN existente | Bidirecional |
| K8s API | HTTPS in-cluster | ServiceAccount | Backend lê |
| Redis | TCP | Password | Interno |
| Frontend ↔ Backend | WebSocket + REST | JWT local | Bidirecional |

### Fluxo de Aprovação (end-to-end)

1. Agente emite approval request via gateway
2. Backend worker poll `/v1/approvals` no gateway (30s)
3. Upsert na tabela `approvals`
4. Redis pub/sub → channel: `approvals`
5. WebSocket hub push → todos os clientes
6. Frontend: badge na nav incrementa, toast aparece
7. Usuário clica Aprovar/Rejeitar com justificativa
8. Backend POST `/v1/approvals/{id}/decide` no gateway
9. `activity_events` registra auditoria
10. WebSocket push atualiza fila em todos os clients

---

## Estrutura de Diretórios

```
clawdevs-ai/
├── control-panel/
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── alembic.ini
│   │   ├── migrations/versions/
│   │   └── app/
│   │       ├── main.py
│   │       ├── core/          (config, auth, database)
│   │       ├── models/        (10 models SQLModel)
│   │       ├── api/           (12 routers + ws hub)
│   │       └── services/      (openclaw, github, k8s, memory, cron)
│   └── frontend/
│       ├── Dockerfile
│       ├── package.json
│       ├── orval.config.ts
│       └── src/
│           ├── app/           (13 rotas App Router)
│           ├── components/    (ui + feature components)
│           ├── lib/           (api gerada Orval + ws client)
│           └── hooks/
└── k8s/base/control-panel/
    ├── kustomization.yaml
    ├── backend-deployment.yaml
    ├── frontend-deployment.yaml
    ├── postgres-statefulset.yaml
    ├── redis-deployment.yaml
    ├── worker-deployment.yaml
    ├── services.yaml
    ├── serviceaccount.yaml
    ├── clusterrole.yaml        (read pods/events/pvcs apenas)
    └── clusterrolebinding.yaml
```

---

## UI/UX — Identidade ClawDevs

- **Tema:** Dark-first, accent `#00FF9C` (verde neon ClawDevs)
- **Fontes:** `Geist` (corpo) + `Geist Mono` (código/logs) — zero custo
- **Avatares:** PNGs de `assets/` servidos como static assets
- **Layout:** Sidebar colapsável + header com breadcrumb
- **Densidade:** Compact por padrão, toggle para comfortable
- **Responsive:** Otimizado desktop, funcional mobile

---

## Vars de Ambiente Adicionais (`k8s/.env`)

```bash
PANEL_SECRET_KEY=        # JWT signing key
PANEL_ADMIN_USERNAME=    # usuário admin inicial
PANEL_ADMIN_PASSWORD=    # senha admin inicial
PANEL_DB_PASSWORD=       # senha PostgreSQL do painel
```

---

## Melhorias sobre openclaw-mission-control

| Aspecto | Mission Control | ClawDevs Panel |
|---|---|---|
| Auth | Clerk (pago) + local | JWT local apenas (zero custo) |
| Realtime | SSE only | WebSockets bidirecionais + SSE fallback |
| Next.js | 16.1.7 | 16.2.0 |
| Tailwind | v3.4.19 | v4.2.2 (10x mais rápido) |
| PostgreSQL | 16 | 18.3 |
| Redis | 7 | 8.6.1 |
| Deploy | Docker Compose | Kubernetes nativo |
| Features | Genérico (multi-org) | ClawDevs-specific (SDD, memória, crons, K8s) |
| UI/UX | Funcional neutro | Identidade ClawDevs (dark + verde neon) |
| Tipagem | Orval + geração manual | Orval automático no CI |
