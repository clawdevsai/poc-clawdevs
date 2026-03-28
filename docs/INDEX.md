# ClawDevsAI Documentation Index

Complete technical documentation for software engineers. **Start here** to find what you need.

---

## 📚 Quick Navigation by Role

### For Backend Engineers
- [Architecture Overview](./architecture/overview.md) — System design and component relationships
- [Backend Services Guide](./guides/backend-setup.md) — FastAPI setup, database, API structure
- [Deployment Guide](./guides/deployment.md) — container, containers, local development
- [Agent Development](./architecture/agents.md) — How agents work, agent loop, tools

### For DevOps/Infrastructure Engineers
- [Deployment Guide](./guides/deployment.md) — Full infrastructure setup and operations
- [Docker Compose Reference](./architecture/container.md) — Container specs, services, storage, networking
- [GPU Support Guide](./guides/gpu-setup.md) — NVIDIA integration and troubleshooting
- [Operations Checklist](./operations/checklist.md) — Pre-flight, monitoring, scaling

### For Frontend Engineers
- [Architecture Overview](./architecture/overview.md) — System design
- [Frontend Services Guide](./guides/frontend-setup.md) — Next.js, React components, API integration
- [Control Panel Guide](./guides/control-panel.md) — UI components and features

### For All Engineers
- **[Setup & Local Development](./guides/setup.md)** — Get started locally
- **[Architecture Overview](./architecture/overview.md)** — Understand the system
- **[Troubleshooting Guide](./operations/troubleshooting.md)** — Debug common issues
- **[Glossary](./reference/glossary.md)** — Terms and concepts

---

## 📁 Documentation Structure

```
docs/
├── INDEX.md (this file)
├── architecture/
│   ├── overview.md           ← START: System design, components, data flow
│   ├── agents.md             ← How agents work, agent loop, tools
│   ├── memory-system.md      ← Memory, embeddings, search
│   ├── container.md         ← Container specs, manifests, services
│   ├── control-panel.md      ← Backend API, database schema, frontend architecture
│   └── security.md           ← Authentication, authorization, secrets
├── guides/
│   ├── setup.md              ← Local development environment
│   ├── deployment.md         ← Production deployment, Docker, makefile
│   ├── backend-setup.md      ← FastAPI configuration, dependencies
│   ├── frontend-setup.md     ← Next.js setup, components, styling
│   ├── gpu-setup.md          ← NVIDIA device plugin, Ollama GPU configuration
│   └── control-panel.md      ← Control panel features and usage
├── operations/
│   ├── checklist.md          ← Pre-flight checks, health checks, monitoring
│   ├── troubleshooting.md    ← Debug common issues, logs, diagnostics
│   ├── scaling.md            ← Performance tuning, horizontal scaling
│   └── maintenance.md        ← Backup, recovery, updates
├── reference/
│   ├── glossary.md           ← Terms and abbreviations
│   ├── api-reference.md      ← API endpoints, schemas
│   ├── environment.md        ← Configuration variables (container/.env)
│   └── makefile-commands.md  ← All make targets explained
├── agentes/                   ← Agent specifications (existing)
│   ├── README.md
│   ├── dev_backend.md
│   ├── dev_frontend.md
│   └── ... (other agents)
└── README.md                  ← Legacy, kept for reference

```

---

## 🎯 By Task

### I'm new to this project
1. Read [Architecture Overview](./architecture/overview.md)
2. Follow [Setup & Local Development](./guides/setup.md)
3. Run `make clawdevs-up` and explore the control panel
4. Read [Glossary](./reference/glossary.md) for key terms

### I need to set up locally
→ [Setup & Local Development](./guides/setup.md)

### I need to deploy to production
→ [Deployment Guide](./guides/deployment.md)

### I need to fix GPU issues
→ [GPU Support Guide](./guides/gpu-setup.md)

### I'm debugging a problem
1. Check [Troubleshooting Guide](./operations/troubleshooting.md)
2. Look at [Glossary](./reference/glossary.md) for context
3. Review relevant architecture doc (agents, container, etc.)

### I need API documentation
→ [API Reference](./reference/api-reference.md)

### I need environment variables
→ [Environment Reference](./reference/environment.md)

### I need to understand agents
→ [Agents Architecture](./architecture/agents.md) and [agentes/](./agentes/)

### I need to understand memory system
→ [Memory System](./architecture/memory-system.md)

---

## 🔑 Key Concepts

**Agent** — An AI-powered role (dev_backend, QA, DevOps, etc.) that executes tasks. Each agent has:
- Own workspace with configuration files (AGENTS.md, SOUL.md, etc.)
- Access to tools (shell, file operations, GitHub API, web search)
- Persistent session history
- Optional memory system

**OpenClaw** — The agent orchestration framework. Manages:
- Agent lifecycle and execution
- Session persistence
- Tool routing and security
- Multi-channel integration (Telegram, Discord, etc.)

**Control Panel** — Web UI (Next.js + FastAPI) for:
- Monitoring agent status
- Triggering agent execution
- Viewing logs and history
- Managing tasks

**SDD (Structured Development Development)** — Workflow:
CONSTITUTION → BRIEF → SPEC → CLARIFY → PLAN → TASK → IMPLEMENTATION

---

## 🚀 Common Commands

```bash
# Setup and deployment
make help                    # Show all available targets
make preflight             # Validate configuration
make clawdevs-up           # Full setup (dev environment)
make stack-apply           # Deploy application stack

# Debugging
make openclaw-logs         # View agent logs
make gpu-doctor            # Diagnose GPU issues
make panel-logs-backend    # View API logs

# Access
make panel-url             # Get Control Panel URL
docker-compose exec -it statefulset/clawdevs-ai -c openclaw -- bash  # Shell into agent container
```

---

## 📊 System Architecture (Brief)

```
Control Panel (Web UI)
        ↓ (WebSocket + REST API)
OpenClaw Gateway (Agent Orchestration)
        ↓
┌───────────────────────────────────────┐
│ Agents (Dev, QA, DevOps, etc.)        │
├───────────────────────────────────────┤
│ Tools: Shell, Files, GitHub, Web      │
├───────────────────────────────────────┤
│ Ollama (Local LLM) or OpenAI/Anthropic│
└───────────────────────────────────────┘
        ↓
Docker Compose (Docker) + Docker + GPU (optional)
```

**Data Flow:**
1. User sends message to Control Panel or Telegram
2. OpenClaw routes to appropriate agent
3. Agent executes tools (file operations, API calls, code execution)
4. LLM decides next steps
5. Results persisted in session history
6. Memory system learns from interactions

---

## 📝 Documentation Standards

All docs follow these conventions:
- **Markdown** format with standard structure
- **Code blocks** with language specification
- **Table of contents** for long documents (h2 headers)
- **Links** to related docs
- **Glossary terms** linked where relevant
- **Examples** for complex concepts
- **Warnings** for dangerous operations (⚠️)
- **Target audience** clearly stated at top of doc

---

## 🔗 External Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Docker Compose Documentation](https://container.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)

---

## 📞 Support

- **Issues:** GitHub issues in default repository
- **Emergency:** Escalate to CEO via Telegram (TELEGRAM_BOT_TOKEN_CEO)
- **Technical Debt:** Use GitHub projects/milestones

---

**Last Updated:** March 27, 2026
**Maintained By:** ClawDevsAI Team
**License:** MIT
