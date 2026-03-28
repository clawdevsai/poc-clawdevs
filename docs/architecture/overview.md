# Architecture Overview

**For:** All engineers
**Purpose:** Understand system design, component relationships, and data flow
**Reading Time:** 10 minutes

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Key Technologies](#key-technologies)
5. [Deployment Model](#deployment-model)

---

## System Overview

ClawDevsAI is an **AI-powered development orchestration platform** built on OpenClaw. It runs multiple specialized AI agents that work together to automate development tasks, from code reviews to deployment.

### What It Does

- **Automates development workflows** — Code generation, testing, deployment, security scanning
- **Orchestrates multiple AI agents** — Each agent specializes in a role (dev_backend, QA, DevOps, etc.)
- **Maintains persistent context** — Session history, memory system, team communication
- **Integrates with existing tools** — GitHub, Telegram, web search, local LLMs

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│  User Interfaces                                 │
│  ├─ Control Panel (Web UI)                       │
│  ├─ Telegram Bot                                 │
│  └─ Direct Gateway Access                        │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  OpenClaw Gateway (Agent Orchestration)          │
│  ├─ Session Management                           │
│  ├─ Tool Routing                                 │
│  ├─ Authentication                               │
│  └─ WebSocket API (JSON-RPC)                     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Agent Runtime                                   │
│  ├─ Agents (CEO, Dev_Backend, QA, etc.)         │
│  ├─ LLM Inference (Ollama or cloud)              │
│  └─ Tool Execution (shell, APIs, file I/O)      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  External Services & Storage                     │
│  ├─ Ollama (Local LLM)                           │
│  ├─ PostgreSQL (Metadata)                        │
│  ├─ PersistentVolumes (Session data, models)     │
│  ├─ GitHub API                                   │
│  ├─ SearXNG (Web search)                         │
│  └─ Telegram API                                 │
└─────────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Infrastructure                                  │
│  └─ Docker Compose (Docker) + Docker + GPU         │
└─────────────────────────────────────────────────┘
```

---

## Core Components

### 1. OpenClaw Gateway

The central orchestration engine. Manages:

- **Session Lifecycle** — Maintains conversation history per agent
- **Tool Routing** — Routes requests to appropriate tools
- **Authentication** — Device tokens, API auth, OAuth
- **Multi-Channel Support** — Telegram, Discord, WebSocket, etc.

**Key Concepts:**
- `Agent` — AI role with own workspace and configuration
- `Session` — Persistent conversation history
- `Tool` — Callable function (shell, file ops, API calls)
- `Hook` — Lifecycle event (before/after inference, tool execution)

**Port:** 8080 (internal), 18789 (exposed)

### 2. Agents

Specialized AI roles that execute tasks. Currently:

| Agent | Role | Schedule |
|-------|------|----------|
| dev_backend | Backend development, APIs, databases | Every 2 hours |
| dev_frontend | Frontend development, UI/UX | Every 2 hours |
| dev_mobile | Mobile development | Every 2 hours |
| qa_engineer | Testing, validation | Every 2 hours |
| devops_sre | Infrastructure, deployments | Every hour |
| security_engineer | Security audits, compliance | Daily at 2 AM |
| ux_designer | Design systems, UX research | Weekly (Monday) |
| dba_data_engineer | Database optimization, data pipelines | Weekly (Monday) |

**Additional Agents:**
- `ceo` — Executive oversight, delegation, GitHub integration
- `po` — Product ownership, requirements, roadmap
- `memory_curator` — Shared memory management
- `architect` — System design decisions

Each agent has:
- **Workspace** — Configuration files (AGENTS.md, SOUL.md, IDENTITY.md)
- **Memory** — Long-term learning (if enabled)
- **Toolset** — Permissions for what it can do
- **Schedule** — When it runs (cron-based)

### 3. Control Panel

Web-based dashboard for:

- **Agent Management** — Create, configure, monitor agents
- **Task Tracking** — View, create, assign tasks
- **Log Viewing** — Real-time agent logs with filtering
- **Metrics** — Execution history, success rates, performance

**Stack:**
- Frontend: Next.js + React
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL
- Real-time: WebSocket + SSE

**Port:** 3000 (frontend), 8000 (backend API)

### 4. Ollama (Local LLM)

Runs language models locally. Supports:

- **Primary Model:** `nemotron-3-super:cloud` (88B parameters)
- **Alternative:** `qwen3-next:80b-cloud` (80B parameters)
- **Embeddings:** `nomic-embed-text` (for memory search)

**API:** `http://ollama:11434`

**Optional:** Use cloud providers (Anthropic, OpenAI) instead via OpenRouter.

### 5. Storage

Three types of persistent storage:

| Component | Storage | Size | Purpose |
|-----------|---------|------|---------|
| Ollama Models | `ollama-data` PVC | 200 GB | Model weights, cache |
| OpenClaw Data | `openclaw-data` PVC | 100 GB | Sessions, logs, backups |
| Panel Database | `panel-db` PVC | 20 GB | Metadata, configuration |

---

## Data Flow

### User Sends Message

```
User → Control Panel (Web) or Telegram
    ↓
OpenClaw Gateway (JSON-RPC)
    ↓
[Route to agent based on rules]
    ↓
Agent Session
    ├─ Load workspace config (AGENTS.md, SOUL.md)
    ├─ Load session history
    ├─ Assemble system prompt
    └─ Pass to LLM
        ↓
    LLM Inference (Ollama)
        ├─ Read tools definitions
        ├─ Decide on tool calls
        └─ Generate response
            ↓
        Tool Execution
        ├─ Shell commands
        ├─ File operations
        ├─ GitHub API calls
        ├─ Web search (SearXNG)
        └─ Telegram notifications
            ↓
        Response Streaming
        ├─ Stream blocks to client
        ├─ Persist to session history
        └─ Update Control Panel
            ↓
        Response Complete
        └─ Optional: memory update, escalation
```

### Key Points

1. **Session-based** — Each conversation maintains history
2. **Async tool execution** — Tools run in parallel when possible
3. **Streaming** — Real-time output to user
4. **Persistence** — Everything saved to disk (RocksDB sessions, PostgreSQL metadata)
5. **Memory** — Agents can learn from past interactions

---

## Key Technologies

### Infrastructure

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Container Orchestration | Docker Compose (Docker) | 1.34.1 | Container management, networking |
| Container Runtime | Docker | Latest | Image building, running |
| GPU Support | NVIDIA Device Plugin | Latest | GPU acceleration for LLM |

### Agent Framework

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Agent Orchestration | OpenClaw | Latest | Session, tools, multi-channel |
| LLM | Ollama | Latest | Local model inference |
| System Language | Bash/Python/JavaScript | Latest | Scripting and tools |

### Web Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Frontend | Next.js | Latest | React UI framework |
| Frontend Styling | Tailwind CSS | Latest | Utility-first CSS |
| Backend | FastAPI | Latest | Python async API |
| Database | PostgreSQL | 15 | Metadata and logs |
| ORM | SQLAlchemy | Latest | Database abstraction |
| Migrations | Alembic | Latest | Database versioning |

### External Services

| Service | Purpose | Optional? |
|---------|---------|-----------|
| GitHub API | Repository management, issues | No |
| Telegram API | Bot notifications | No |
| SearXNG | Web search aggregation | Yes (local) |
| OpenRouter | Cloud LLM provider | Yes (fallback) |

---

## Deployment Model

### Development (Local Docker)

```
Developer Machine (Windows 11)
├─ Docker Desktop with GPU support
├─ Docker cluster (2 CPUs, 7GB RAM)
├─ Containers: OpenClaw, Ollama, Control Panel, PostgreSQL
└─ PersistentVolumes: 200GB (Ollama) + 100GB (OpenClaw) + 20GB (Database)
```

**Startup:** `make clawdevs-up` (5-10 minutes)

### Production (Proposed)

```
Docker Compose Cluster (Multi-node)
├─ Ingress Controller (HAProxy/nginx)
├─ OpenClaw Nodes (3x replicas, stateless)
├─ Ollama Nodes (2x, GPU)
├─ Control Panel (stateless backend + PostgreSQL)
├─ Persistent Storage
│   ├─ Sessions (shared database)
│   ├─ Models (network attached)
│   └─ Logs (centralized ELK)
└─ Monitoring (Prometheus + Grafana)
```

**Currently:** Single-node Docker (development only)

---

## Configuration Management

### Environment Variables

Stored in `container/.env` (not committed):

```bash
# Required
OPENCLAW_GATEWAY_TOKEN=<bearer-token>
TELEGRAM_BOT_TOKEN_CEO=<bot-id>:<bot-hash>
TELEGRAM_CHAT_ID_CEO=<chat-id>
GIT_TOKEN=<github-pat>
GIT_ORG=<github-org>

# Optional
OPENROUTER_API_KEY=<api-key>  # For cloud LLM
DEBUG_LOG_ENABLED=true|false
```

Full reference: [Environment Variables](../reference/environment.md)

### ConfigMaps

Agent configuration in `docker/base/openclaw-config/`:

```
openclaw-config/
├── shared/
│   ├── CONSTITUTION.md
│   ├── BRIEF_TEMPLATE.md
│   ├── SPEC_TEMPLATE.md
│   └── ... (SDD templates)
└── agents/
    ├── dev_backend/AGENTS.md
    ├── dev_frontend/AGENTS.md
    └── ... (agent specs)
```

These are mounted in containers and injected into agent workspace.

---

## Security Architecture

### Authentication

- **Device Pairing** — Initial device token handshake
- **Bearer Tokens** — API authentication (OPENCLAW_GATEWAY_TOKEN)
- **OAuth** — GitHub, cloud LLM providers

### Authorization

- **Agent Sandboxing** — Restrict tool access per agent
- **Session Isolation** — Separate conversations per user/channel
- **GitHub Credentials** — Scoped personal access tokens

### Secrets Management

- `container/.env` — Never committed, loaded at deploy time
- `/data/openclaw/credentials/` — OAuth tokens (runtime)
- `~/.openclaw/` — Local auth profiles (dev mode)

Full details: [Security](./security.md)

---

## Next Steps

1. **New to the project?** → Read [Setup & Local Development](../guides/setup.md)
2. **Need to deploy?** → Read [Deployment Guide](../guides/deployment.md)
3. **Want details on agents?** → Read [Agents Architecture](./agents.md)
4. **Troubleshooting?** → Read [Troubleshooting Guide](../operations/troubleshooting.md)

---

**Questions?** Check [Glossary](../reference/glossary.md) for terms or [API Reference](../reference/api-reference.md) for endpoints.
