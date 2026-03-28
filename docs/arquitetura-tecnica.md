# Arquitetura Técnica - ClawDevsAI

**Documento:** Detalhes de Implementação
**Data:** 27 de março de 2026
**Nível:** Engenheiros e Arquitetos

---

## 1. Topologia de Rede e Componentes

### 1.1 Camada de Containerização

**Docker (Windows/Docker Desktop)**
```
┌─────────────────────────────────────────┐
│         Docker Desktop (Windows)         │
├─────────────────────────────────────────┤
│  Docker Cluster (v1.34.1)             │
│  ├─ CPUs: 2 (configurável)              │
│  ├─ Memory: 7168 MB (7 GB)              │
│  ├─ container Version: 1.34.1                 │
│  └─ GPU Support: NVIDIA Device Plugin   │
└─────────────────────────────────────────┘
```

**Configuração:**
- Profile: `clawdevs-ai`
- Context: `clawdevs-ai`
- Storage Classes: local-path, standard
- Add-ons: dashboard, metrics-server, storage-provisioner, nvidia-device-plugin

### 1.2 Containers e Serviços

```
Environment: default
│
├─ Container: openclaw-runtime
│  ├─ Image: clawdevsai/openclaw-runtime:latest
│  ├─ CPU: 2000m (solicitado), 4000m (limite)
│  ├─ Memory: 4Gi (solicitado), 8Gi (limite)
│  ├─ GPU: 1 (NVIDIA)
│  ├─ Volumes:
│  │  ├─ openclaw-home (PVC, 50Gi)
│  │  ├─ openclaw-data (PVC, 100Gi)
│  │  └─ openclaw-config (ConfigMap)
│  ├─ Env Vars: OPENCLAW_GATEWAY_TOKEN, OPENCLAW_LOG_LEVEL, ...
│  └─ Ports: 8080 (Gateway WebSocket)
│
├─ Container: ollama-runtime
│  ├─ Image: clawdevsai/ollama-runtime:latest
│  ├─ CPU: 4000m (solicitado), 8000m (limite)
│  ├─ Memory: 6Gi (solicitado), 12Gi (limite)
│  ├─ GPU: 1 (NVIDIA)
│  ├─ Volumes:
│  │  └─ ollama-data (PVC, 200Gi)
│  ├─ Env Vars: OLLAMA_API_KEY, OLLAMA_AUTO_PULL_MODELS
│  └─ Ports: 11434 (API), 11435 (WebUI)
│
├─ Container: searxng-runtime
│  ├─ Image: clawdevsai/searxng-runtime:latest
│  ├─ CPU: 500m (solicitado), 1000m (limite)
│  ├─ Memory: 512Mi (solicitado), 1Gi (limite)
│  ├─ Volumes:
│  │  └─ searxng-config (ConfigMap)
│  └─ Ports: 8888 (API)
│
├─ Container: clawdevs-panel-backend
│  ├─ Image: clawdevsai/clawdevs-panel-backend:latest
│  ├─ CPU: 500m (solicitado), 1000m (limite)
│  ├─ Memory: 512Mi (solicitado), 1Gi (limite)
│  ├─ Volumes:
│  │  └─ panel-db (PVC, 20Gi) — PostgreSQL
│  ├─ Env Vars: DATABASE_URL, OPENCLAW_GATEWAY_URL, ...
│  └─ Ports: 8000 (FastAPI)
│
└─ Container: clawdevs-panel-frontend
   ├─ Image: clawdevsai/clawdevs-panel-frontend:latest
   ├─ CPU: 200m (solicitado), 500m (limite)
   ├─ Memory: 256Mi (solicitado), 512Mi (limite)
   ├─ Volumes:
   │  └─ frontend-config (ConfigMap)
   └─ Ports: 3000 (Next.js)

Services:
├─ openclaw-gateway (ClusterIP:8080)
├─ ollama-api (ClusterIP:11434)
├─ panel-backend-api (ClusterIP:8000)
└─ panel-frontend (ClusterIP:3000)

PersistentVolumeClaims:
├─ openclaw-home (50Gi)
├─ openclaw-data (100Gi)
├─ ollama-data (200Gi)
└─ panel-db (20Gi)
```

---

## 2. OpenClaw Gateway

### 2.1 Ciclo de Vida

```
Gateway Startup:
1. Initialize WebSocket Server (port 8080)
2. Load openclaw.json Configuration
3. Initialize Session Store (RocksDB / SQLite)
4. Load Plugins (context engine, memory providers, skills)
5. Prepare Skill Directories (global + per-agent)
6. Subscribe to System Events (cron, webhooks, presence)
7. Listen for Client Connections

Client Connection:
1. Establish WebSocket
2. Send 'connect' Frame (device token handshake)
3. Gateway Issues Device Token
4. Client Ready → Can send 'agent' commands

Agent Execution (per request):
1. Validate 'agent' RPC params
2. Resolve Session Key (from channel/peer/type)
3. Acquire Session Write Lock
4. Load/Create Session
5. Invoke Pi Agent Runtime (embedded)
6. Handle Tool Execution
7. Stream Results to Client
8. Persist Session History
9. Release Lock
```

### 2.2 Configuração (openclaw.json)

**Estrutura Principal:**
```json
{
  "agent": {
    "workspace": "~/.openclaw/workspace",
    "defaultModel": "anthropic/claude-sonnet-4-5",
    "sandbox": { "mode": "off" },
    "tools": { "allow": "*", "deny": [] },
    "blockStreamingDefault": "on",
    "blockStreamingChunk": { "minChars": 1500, "maxChars": 4000 },
    "humanDelay": "off",
    "contextPruning": { "mode": "cache-ttl", "ttl": "5m" },
    "memorySearch": {
      "provider": "gemini",
      "model": "gemini-embedding-2-preview",
      "outputDimensionality": 3072
    },
    "compaction": { "model": "anthropic/claude-sonnet-4-5" }
  },
  "session": {
    "dmScope": "per-channel-peer",
    "resetByType": { "direct": "4:00", "group": "4:00", "thread": "4:00" },
    "idleMinutes": 0,
    "sendPolicy": { "rules": [], "default": "allow" },
    "maintenance": { "mode": "warn", "pruneAfter": 30, "maxEntries": 500 }
  },
  "messages": {
    "inbound": { "debounceMs": 2000 },
    "queue": { "cap": 20, "drop": "old" },
    "responsePrefix": "🤖 "
  },
  "channels": {
    "whatsapp": { "accounts": [], "historyLimit": 20 },
    "telegram": { "accounts": [], "historyLimit": 20 },
    "discord": { "accounts": [], "historyLimit": 50 }
  },
  "plugins": { "slots": {}, "entries": {} },
  "models": {
    "providers": {
      "anthropic": { "apiKey": "$ANTHROPIC_API_KEY" },
      "openrouter": { "apiKey": "$OPENROUTER_API_KEY", "baseUrl": "https://openrouter.ai/api/v1" },
      "ollama": { "baseUrl": "http://ollama-api:11434" }
    }
  }
}
```

### 2.3 Tools Embutidas

```
Sessão:
├─ sessions_list      — Enumera sessões com filtros
├─ sessions_history   — Recupera transcrição
├─ sessions_send      — Roteia mensagens para outras sessões
└─ sessions_spawn     — Lança sub-agentes isolados

Memória:
├─ memory_search      — Busca semântica
└─ memory_get         — Leitura dirigida

Sistema:
├─ shell              — Executa comandos shell
├─ read               — Lê arquivos
├─ write              — Escreve arquivos
├─ edit               — Edita arquivos
└─ exec               — Executa scripts Python
```

---

## 3. Ollama Integration

### 3.1 Modelos Configurados

```yaml
# container/base/ollama-container.yaml
env:
  - name: OLLAMA_AUTO_PULL_MODELS
    value: "true"
  - name: OLLAMA_BOOT_MODELS
    value: "nemotron-3-super:cloud qwen3-next:80b-cloud nomic-embed-text"
  - name: OLLAMA_MEMORY_LIMIT
    value: "4gb"
  - name: OLLAMA_NUM_GPU
    value: "1"
```

**Modelos Disponíveis:**

| Modelo | Uso | Params | GPU | Velocidade |
|--------|-----|--------|-----|-----------|
| `nemotron-3-super:cloud` | Geral (code, text) | 88B | Completo | Média |
| `qwen3-next:80b-cloud` | Alternativa | 80B | Completo | Média |
| `nomic-embed-text` | Embeddings (memória) | 137M | CPU | Rápido |

### 3.2 API Client

**Endpoint Base:** `http://ollama-api:11434`

**Operações Principais:**
```bash
# List models
curl http://ollama-api:11434/api/tags

# Generate (streaming)
curl -X POST http://ollama-api:11434/api/generate \
  -d '{"model":"nemotron-3-super:cloud","prompt":"hello","stream":true}'

# Embeddings
curl -X POST http://ollama-api:11434/api/embeddings \
  -d '{"model":"nomic-embed-text","prompt":"text to embed"}'
```

---

## 4. Control Panel

### 4.1 Backend (FastAPI)

**Estrutura:**
```
control-panel/backend/
├── app/
│   ├── __init__.py
│   ├── main.py             (Application factory)
│   ├── config.py           (Settings via Pydantic)
│   ├── database.py         (SQLAlchemy setup)
│   ├── models/
│   │   ├── agent.py
│   │   ├── task.py
│   │   ├── execution.py
│   │   └── log.py
│   ├── schemas/            (Pydantic validators)
│   │   ├── agent.py
│   │   ├── task.py
│   │   └── ...
│   ├── routers/
│   │   ├── agents.py       (GET /agents, POST /agents/{id}/run)
│   │   ├── tasks.py        (CRUD /tasks)
│   │   ├── executions.py   (Status tracking)
│   │   ├── logs.py         (Log streaming)
│   │   └── system.py       (Health, stats)
│   ├── dependencies.py     (DI containers)
│   └── utils/
│       ├── openclaw_client.py  (WebSocket client para Gateway)
│       ├── github_client.py    (API GitHub)
│       └── telegram_bot.py     (Notificações)
├── migrations/             (Alembic)
├── tests/
├── requirements.txt
└── pyproject.toml
```

**Endpoints Principais:**
```
GET  /api/health              — Health check
GET  /api/agents              — Lista agentes
POST /api/agents/{id}/run     — Executa agente
GET  /api/agents/{id}/status  — Status
GET  /api/tasks               — Lista tarefas
POST /api/tasks               — Cria tarefa
GET  /api/logs/stream         — SSE logs

Authentication: Bearer token (via OPENCLAW_GATEWAY_TOKEN)
```

**Database Schema:**
```sql
-- Agentes
CREATE TABLE agents (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  workspace_path VARCHAR(255),
  schedule CRON_EXPRESSION,
  enabled BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Tarefas
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  agent_id VARCHAR(255) FOREIGN KEY,
  title VARCHAR(255),
  description TEXT,
  status ENUM('pending', 'running', 'completed', 'failed'),
  priority ENUM('low', 'medium', 'high'),
  created_at TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);

-- Execuções
CREATE TABLE executions (
  id UUID PRIMARY KEY,
  task_id UUID FOREIGN KEY,
  agent_id VARCHAR(255) FOREIGN KEY,
  session_key VARCHAR(255),
  status ENUM('queued', 'running', 'success', 'error'),
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  exit_code INT,
  error_message TEXT
);

-- Logs
CREATE TABLE logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  execution_id UUID FOREIGN KEY,
  level ENUM('DEBUG', 'INFO', 'WARN', 'ERROR'),
  message TEXT,
  timestamp TIMESTAMP
);
```

### 4.2 Frontend (Next.js)

**Estrutura:**
```
control-panel/frontend/
├── app/
│   ├── layout.tsx          (Root layout)
│   ├── page.tsx            (Dashboard)
│   ├── agents/
│   │   ├── page.tsx        (Agent list)
│   │   └── [id]/
│   │       ├── page.tsx    (Agent details)
│   │       └── logs.tsx    (Live logs)
│   ├── tasks/
│   │   ├── page.tsx
│   │   └── [id]/page.tsx
│   └── api/
│       └── [...]/route.ts  (Next.js API routes)
├── components/
│   ├── AgentCard.tsx
│   ├── TaskList.tsx
│   ├── ExecutionStatus.tsx
│   ├── LogViewer.tsx
│   └── ...
├── hooks/
│   ├── useAgent.ts
│   ├── useTask.ts
│   ├── useExecutions.ts
│   └── useSSE.ts           (Server-Sent Events)
├── styles/
│   ├── globals.css
│   └── ...
├── lib/
│   ├── api-client.ts
│   ├── types.ts
│   └── utils.ts
├── package.json
└── next.config.js
```

**Componentes Principais:**

1. **Dashboard**
   - Status dos agentes (online/offline)
   - Últimas execuções
   - Métricas agregadas (total tasks, success rate)

2. **Agent Management**
   - CRUD de agentes
   - Configuração de schedule
   - Trigger manual de execução

3. **Task Tracking**
   - Visualização de tarefas
   - Status em tempo real
   - Histórico de execução

4. **Log Viewer**
   - Streaming de logs via SSE
   - Filtros (nivel, source, agent)
   - Full-text search

---

## 5. Kustomize e ConfigMaps

### 5.1 Estrutura

```
container/
├── kustomization.yaml      (Root — combina base + overlays)
├── base/
│   ├── kustomization.yaml
│   ├── openclaw-container.yaml
│   ├── ollama-container.yaml
│   ├── searxng-container.yaml
│   ├── panel-backend-container.yaml
│   ├── panel-frontend-container.yaml
│   ├── pvc.yaml            (PersistentVolumeClaims)
│   ├── service.yaml
│   ├── storage-class.yaml
│   ├── openclaw-config/    (ConfigMaps)
│   │   ├── kustomization.yaml
│   │   ├── shared/         (Arquivos comuns)
│   │   │   ├── CONSTITUTION.md
│   │   │   ├── BRIEF_TEMPLATE.md
│   │   │   ├── SPEC_TEMPLATE.md
│   │   │   ├── PLAN_TEMPLATE.md
│   │   │   ├── TASK_TEMPLATE.md
│   │   │   ├── SDD_OPERATIONAL_PROMPTS.md
│   │   │   ├── SDD_CHECKLIST.md
│   │   │   └── SDD_FULL_CYCLE_EXAMPLE.md
│   │   ├── agents/         (Specs de agentes)
│   │   │   ├── dev-backend.md
│   │   │   ├── dev-frontend.md
│   │   │   ├── dev-mobile.md
│   │   │   ├── qa.md
│   │   │   ├── devops-sre.md
│   │   │   ├── security-engineer.md
│   │   │   ├── ux-designer.md
│   │   │   └── dba-data-engineer.md
│   │   └── bootstrap-scripts/
│   │       ├── 00-base-setup.sh
│   │       ├── 01-docker-setup.sh
│   │       ├── 02-nvidia-setup.sh
│   │       ├── 03-storage-setup.sh
│   │       ├── 04-pullsecrets.sh
│   │       ├── 05-dockerlogin.sh
│   │       ├── 06-app-setup.sh
│   │       ├── 07-volume-setup.sh
│   │       ├── 08-ollama-setup.sh
│   │       └── 09-openclaw-config.sh
│   └── monitoring/         (Opcional)
│       ├── prometheus.yaml
│       └── grafana.yaml
└── overlays/               (Variações por env)
    ├── development/
    ├── staging/
    └── production/
```

### 5.2 Injeção de Configuração

**Via Kustomize:**
```yaml
# container/base/kustomization.yaml
configMapGenerator:
  - name: openclaw-config
    files:
      - openclaw-config/shared/CONSTITUTION.md
      - openclaw-config/shared/BRIEF_TEMPLATE.md
      - openclaw-config/agents/dev-backend.md
      # ...

secretGenerator:
  - name: openclaw-secrets
    envs:
      - ../.env        # Referencia container/.env
```

**Montagem em Container:**
```yaml
# Container spec
volumeMounts:
  - name: openclaw-config
    mountPath: /openclaw/config
    readOnly: true
  - name: openclaw-secrets
    mountPath: /var/run/secrets/openclaw

volumes:
  - name: openclaw-config
    configMap:
      name: openclaw-config
  - name: openclaw-secrets
    secret:
      secretName: openclaw-secrets
```

---

## 6. Fluxos de Dados

### 6.1 Agent Execution Flow

```
Client (Control Panel)
  │
  ├─ POST /api/agents/{id}/run
  │
  └─→ Backend (FastAPI)
      │
      ├─ Validate request
      ├─ Create task record
      │
      └─→ OpenClaw Gateway (WebSocket)
          │
          ├─ agent RPC {"model": "...", "prompt": "..."}
          │
          └─→ Pi Agent Runtime (embedded)
              │
              ├─ Resolve system prompt
              ├─ Load skills
              │
              └─→ LLM Inference
                  │
                  ├─ Anthropic API (remoto)
                  └─ ou Ollama (local)
                  │
                  └─→ Tool Execution
                      │
                      ├─ sessions_* tools
                      ├─ memory_* tools
                      ├─ shell/read/write/exec
                      ├─ GitHub API calls
                      └─ Telegram notifications
                      │
                      └─→ Response Streaming
                          │
                          └─→ Backend (SSE)
                              │
                              └─→ Frontend (UI update)
                                  │
                                  └─→ Database (audit trail)
```

### 6.2 Session Persistence

```
Agent Execution
  │
  └─→ Session Store (RocksDB/SQLite)
      │
      ├─ Key: "agent:<agentId>:<sessionKey>"
      │
      ├─ Session File: ~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl
      │   ├─ User message #1
      │   ├─ Assistant response #1
      │   ├─ Tool call #1
      │   ├─ Tool result #1
      │   ├─ User message #2
      │   └─ ...
      │
      └─ Index: ~/.openclaw/agents/<agentId>/sessions/sessions.json
          ├─ List of all sessions
          ├─ Last activity timestamp
          ├─ Message count
          └─ Summary
```

### 6.3 Memory System

```
Agent Memory Write
  │
  ├─→ Automatic flush (antes de compaction)
  │   └─ Silent agentic turn: "Remember important facts..."
  │       └─ Writes to memory/YYYY-MM-DD.md
  │
  ├─→ Manual write (agent decision)
  │   └─ memory_get() tool
  │       └─ Writes to MEMORY.md (curated)
  │
└─→ Vector Embedding
    │
    ├─ Local: node-llama-cpp
    ├─ OpenAI: OpenAI API
    ├─ Gemini: Google API
    ├─ Voyage: Voyage API
    └─ Ollama: Local instance
    │
    └─→ Vector Store (memory search)
        │
        ├─ Hybrid search (vector + BM25)
        ├─ MMR (reduce duplicates)
        ├─ Temporal decay (boost recent)
        │
        └─→ Retrieved context
            └─ Injected into next prompt
```

---

## 7. Security Model

### 7.1 Authentication & Authorization

```
Device Pairing:
┌─────────────────────────────────────────┐
│ Client (first time)                      │
├─────────────────────────────────────────┤
│ 1. Connect request (without token)       │
│ 2. Gateway challenges nonce              │
│ 3. User approves on gateway host         │
│ 4. Gateway issues device token           │
│ 5. Client persists token locally         │
│ 6. Future connects use token             │
└─────────────────────────────────────────┘

Token Types:
├─ Device Token — Client identification
├─ Bearer Token (OPENCLAW_GATEWAY_TOKEN) — API auth
└─ OAuth Tokens (per provider) — GitHub, Google, etc.
```

### 7.2 Sandbox & Tool Restrictions

```
Per-Agent Policy:
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "sandbox": { "mode": "off" },
        "tools": { "allow": "*", "deny": [] }
      },
      {
        "id": "family",
        "sandbox": { "mode": "all", "scope": "agent" },
        "tools": { "allow": ["read"], "deny": ["exec", "write"] }
      }
    ]
  }
}

Sandbox Visibility Scopes:
├─ self — Current session only
├─ tree — Current + spawned children
├─ agent — All sessions for agent ID
└─ all — Cross-agent access
```

### 7.3 Credentials Storage

```
Hierarchy:
1. ~/.openclaw/credentials/oauth.json    (import-only)
2. ~/.openclaw/agents/<id>/agent/auth-profiles.json (primary)
3. ~/.openclaw/agents/<id>/agent/auth.json (legacy)

Example auth-profiles.json:
{
  "profiles": {
    "anthropic": {
      "apiKey": "sk-...",
      "refreshToken": "...",
      "expiresAt": "2026-03-28T00:00:00Z"
    },
    "github": {
      "accessToken": "ghp_...",
      "refreshToken": "...",
      "expiresAt": "2026-06-27T00:00:00Z"
    }
  }
}
```

---

## 8. CI/CD e Deploy

### 8.1 Image Build

```
Dockerfile Hierarchy:
├─ docker/openclaw.Dockerfile
│  ├─ Base: Ubuntu 22.04
│  ├─ Install: openclaw, gh, git, python
│  ├─ Pre-warm: skills, configs
│  └─ Entrypoint: openclaw gateway --host 0.0.0.0
│
├─ docker/ollama.Dockerfile
│  ├─ Base: Ubuntu 22.04
│  ├─ Install: ollama, NVIDIA CUDA libs
│  ├─ Pre-warm: models (nemotron, qwen3-next, nomic-embed)
│  └─ Entrypoint: ollama serve
│
├─ docker/searxng.Dockerfile
│  ├─ Base: searxng:latest
│  ├─ Configure: settings.yml
│  └─ Plugins: custom engines
│
├─ docker/panel-backend.Dockerfile
│  ├─ Base: python:3.12-slim
│  ├─ Install: FastAPI, SQLAlchemy, alembic
│  ├─ Copy: app code, requirements.txt
│  └─ Entrypoint: uvicorn app.main:app --host 0.0.0.0
│
└─ docker/panel-frontend.Dockerfile
   ├─ Base: node:20-alpine (build), nginx (runtime)
   ├─ Build: next build
   └─ Serve: nginx (static content)
```

### 8.2 Push to Docker Hub

```bash
# Manual build + push
docker build -t clawdevsai/openclaw-runtime:2026.3.24 \
  -f docker/openclaw.Dockerfile .
docker push clawdevsai/openclaw-runtime:2026.3.24

# Via Makefile
make images-build        # Build localmente
make images-push         # Push para Docker Hub
make images-release      # Build + Push
```

### 8.3 Local vs Remote Mode

```
Mode: PUSH_IMAGE=remote (padrão)
├─ Kustomize usa imagens publicadas
├─ Mais rápido (pull pronto)
└─ Requer acesso Docker Hub

Mode: PUSH_IMAGE=local
├─ Kustomize builda localmente no Docker
├─ Não requer Docker Hub
└─ Mais lento no primeiro build
```

---

## 9. Observabilidade

### 9.1 Logging

```
Log Levels:
├─ debug — Entrada/saída de funções, state changes
├─ info — Eventos importantes (agente started, tool called)
├─ warn — Comportamentos inesperados (fallback, retry)
└─ error — Falhas (exception, abort, timeout)

Sinks:
├─ Container logs (docker-compose logs)
├─ Persistent volume (/openclaw/logs/)
├─ Structured logging (JSON)
└─ Panel backend (log viewer com filtros)
```

### 9.2 Métricas

```
Prometheus scrape targets (se habilitado):
├─ openclaw-gateway:8080/metrics
├─ ollama-api:11434/metrics
├─ panel-backend:8000/metrics
└─ node-exporter (cluster metrics)

Métricas-chave:
├─ agent_executions_total
├─ agent_execution_duration_seconds
├─ agent_tools_calls_total
├─ ollama_model_load_duration
├─ panel_api_request_duration
└─ panel_database_connections
```

### 9.3 Tracing

```
Request flow tracing (com OpenClaw debug=true):
├─ X-Request-ID header (propagated)
├─ Agent execution trace
│  ├─ System prompt assembly
│  ├─ LLM inference
│  ├─ Tool execution
│  └─ Response streaming
└─ Correlated logs

Jaeger/Zipkin integration (opcional):
├─ Export spans
├─ Visualize service graph
└─ Analyze bottlenecks
```

---

## 10. Performance & Scaling

### 10.1 Bottlenecks Comuns

```
Scenario 1: LLM Inference Lento
├─ Causa: Ollama com muitos contextos paralelos
├─ Solução:
│  ├─ Aumentar OLLAMA_NUM_GPU
│  ├─ Reduzir OLLAMA_MEMORY_LIMIT (swap via CPU)
│  ├─ Usar modelo menor (qwen3-next em vez de nemotron)
│  └─ Aumentar timeout do agent (default 600s)
│
Scenario 2: Memory Bloat (compaction)
├─ Causa: Sessions antigas não compactadas
├─ Solução:
│  ├─ Trigger manual: /compact
│  ├─ Alterar auto-compact threshold em openclaw.json
│  └─ Usar pruning + context engine customizado
│
Scenario 3: Control Panel Lento
├─ Causa: Database queries não-otimizadas
├─ Solução:
│  ├─ Adicionar índices (SQLAlchemy relationships)
│  ├─ Paginação em list endpoints
│  ├─ Cache em Redis (para dashboards)
│  └─ Profile com py-spy / cProfile
```

### 10.2 Horizontal Scaling

```
Atualmente: 1 gateway, 1 ollama
Futuro: Multi-node setup

Arquitetura escalada:
├─ Load Balancer (nginx/HAProxy)
│  └─ Distribui entre múltiplos gateways
│
├─ Gateway Nodes (stateless)
│  ├─ Gateway #1 (port 8080)
│  ├─ Gateway #2 (port 8080)
│  └─ Gateway #N
│  └─ Session store (shared) — PostgreSQL em vez de RocksDB
│
├─ Ollama Nodes (stateless)
│  ├─ Ollama #1 (load balanced)
│  └─ Ollama #2
│
└─ Panel (stateless)
   ├─ Backend #1
   ├─ Backend #2
   └─ PostgreSQL (shared)
```

---

## 11. Troubleshooting

### 11.1 Common Issues

```
Issue: Container stuck in ImagePullBackOff
Solução:
├─ Check: docker-compose describe container <container>
├─ Verificar: docker login credentials
├─ Ou: PUSH_IMAGE=local (builda localmente)

Issue: GPU not available
Solução:
├─ Run: make gpu-doctor
├─ Verify: nvidia-smi in container
├─ Fix: make gpu-plugin-apply

Issue: Ollama models not loaded
Solução:
├─ Check: make ollama-logs
├─ Wait: Containere estar pulling (verificar space)
├─ Manual: docker-compose exec -it <container> ollama pull nemotron-3-super:cloud

Issue: Compaction infinite loop
Solução:
├─ Check: OPENCLAW_LOG_LEVEL=debug
├─ Review: openclaw.json compaction settings
├─ Reset: /new (nova sessão)
```

### 11.2 Debug Mode

```bash
# Enable debug logging
docker-compose set env container/openclaw-runtime OPENCLAW_LOG_LEVEL=debug

# Attach to container shell
docker-compose exec -it <container> /bin/bash

# View system state
docker-compose describe container <container>
docker-compose get pvc
docker-compose get events

# Stream logs
docker-compose logs -f <container>
docker-compose logs -f <container> --previous  (crashed container)
```

---

## 12. Referências Rápidas

### 12.1 Arquivos Críticos

- **Configuração:** `container/.env`, `openclaw.json`
- **Containers:** `container/base/*.yaml`
- **ConfigMaps:** `container/base/openclaw-config/`
- **Backend:** `control-panel/backend/app/`
- **Frontend:** `control-panel/frontend/app/`

### 12.2 Comandos Úteis

```bash
# Debugging
docker-compose get containers -w
docker-compose describe container <container>
docker-compose exec -it <container> /bin/bash
docker-compose logs -f <container>

# Port forwarding
docker-compose port-forward service/panel-backend-api 8000:8000
docker-compose port-forward service/ollama-api 11434:11434

# Restart services
docker-compose rollout restart deployment <deployment>

# View resources
docker-compose get pvc
docker-compose get configmap
docker-compose get secret
```

---

**Documento Completo — Pronto para Implementação**

Data: 27 de março de 2026
