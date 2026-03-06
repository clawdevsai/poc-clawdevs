# 13 — Integrações de Sistemas e APIs Externas
> **Objetivo:** Mapear a arquitetura orientada a eventos e as fronteiras de integração do projeto.
> **Público-alvo:** Devs, Arquitetos
> **Ação Esperada:** Devs implementam integrações externas como MCP servers para manter a segurança do cluster.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Mapa de Integrações

```mermaid
graph TD
    subgraph EXTERNAL["Sistemas Externos"]
        TG[Telegram API]
        WA[WhatsApp Baileys]
        GH_EXT[GitHub externo]
        OR[OpenRouter API]
    end

    subgraph GATEWAY["OpenClaw :18789"]
        OC_RECV[Webhook Receiver]
        OC_SEND[Message Sender]
        OC_SESS[Session Store]
    end

    subgraph CLAWDEVS["ClawDevs Core"]
        ORCH[Orquestrador\nLangGraph]
        AGENTS[Pods de Agentes]
        REDIS[Redis Streams\n+ Pub/Sub]
    end

    subgraph SCM["Controle de Código"]
        GITEA[Gitea :3000\nauto-hosted]
        WEBHOOK_GIT[Gitea Webhooks]
    end

    subgraph INFRA["Infraestrutura"]
        PROM[Prometheus :9090]
        GRAFANA[Grafana :3001]
        LOKI[Loki :3100\nlog aggregation]
        QDRANT[Qdrant :6333]
        POSTGRES[PostgreSQL :5432]
    end

    subgraph MCP["MCP Servers"]
        MCP_FS[mcp-filesystem]
        MCP_GIT[mcp-gitea]
        MCP_PG[mcp-postgres]
        MCP_QDRANT[mcp-qdrant]
    end

    TG <-->|Bot API| OC_RECV
    WA <-->|Baileys WS| OC_RECV
    OC_RECV --> ORCH
    AGENTS --> OC_SEND --> TG & WA

    AGENTS <-->|XADD/XREAD| REDIS
    ORCH <-->|state + lock| REDIS

    AGENTS <-->|clone/commit/PR via MCP| GITEA
    GITEA --> WEBHOOK_GIT --> ORCH

    AGENTS <-->|MCP tool calls| MCP_FS & MCP_GIT & MCP_PG & MCP_QDRANT
    MCP_GIT <--> GITEA
    MCP_PG <--> POSTGRES
    MCP_QDRANT <--> QDRANT

    AGENTS -->|fallback inference| OR
    AGENTS -->|scrape metrics| PROM
    PROM --> GRAFANA
    AGENTS -->|structured logs| LOKI
    LOKI --> GRAFANA
```

---

## 1. Integração OpenClaw

### Webhook de Entrada (Diretor → Agentes)

```python
# FastAPI handler no Orquestrador
from fastapi import FastAPI, Request, HTTPException, Header
import hmac, hashlib, json

app = FastAPI()

@app.post("/hooks/agent")
async def openclaw_webhook(
    request: Request,
    authorization: str = Header(...)
):
    # 1. Valida Bearer token
    if authorization != f"Bearer {OPENCLAW_AGENT_TOKEN}":
        raise HTTPException(403, "Invalid token")

    # 2. Lê payload
    body = await request.json()
    """
    Payload OpenClaw:
    {
      "channel": "telegram",
      "chat_id": "123456789",
      "user_id": "diego_morais",
      "text": "#arch revisar o ADR-005 amanhã",
      "attachments": [],
      "timestamp": "2026-03-06T10:30:00Z"
    }
    """

    # 3. Roteamento
    destination = route_message(body["text"])
    session_id = f"{body['channel']}:{body['chat_id']}"

    # 4. Despacha para fila
    task_id = await dispatch_task(
        destination=destination,
        session_id=session_id,
        message=body["text"],
        attachments=body.get("attachments", []),
        reply_channel=body["channel"],
        reply_chat_id=body["chat_id"],
    )

    return {"status": "accepted", "task_id": task_id}


async def send_to_director(chat_id: str, channel: str, text: str):
    """Envia resposta de volta ao Diretor via OpenClaw."""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://openclaw-svc:18789/send",
            headers={"Authorization": f"Bearer {OPENCLAW_AGENT_TOKEN}"},
            json={
                "channel": channel,
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
            },
            timeout=30,
        )
```

### Configuração openclaw.json para ClawDevs

```json
{
  "version": "1.0",
  "server": {
    "port": 18789,
    "host": "0.0.0.0",
    "tls": false
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "bot_token": "${TELEGRAM_BOT_TOKEN}",
      "webhook_url": "https://${PUBLIC_DOMAIN}/telegram/webhook",
      "allowed_users": ["${DIRECTOR_TELEGRAM_ID}"]
    },
    "whatsapp": {
      "enabled": true,
      "adapter": "baileys",
      "session_path": "/data/openclaw/sessions/wa",
      "allowed_numbers": ["${DIRECTOR_WHATSAPP}"]
    }
  },
  "agents": [
    {
      "name": "clawdevs-orchestrator",
      "webhook": "http://orchestrator-svc:8000/hooks/agent",
      "bearer_token": "${OPENCLAW_AGENT_TOKEN}",
      "channels": ["telegram", "whatsapp"],
      "active": true
    }
  ],
  "security": {
    "rate_limit": "30/minute",
    "max_message_size": "10MB",
    "allowed_file_types": ["pdf", "txt", "md", "png", "jpg"]
  }
}
```

---

## 2. Integração Gitea (SCM Agents)

```mermaid
sequenceDiagram
    participant DEV as Dev Agent
    participant MCP_GIT as MCP-Gitea
    participant GITEA as Gitea :3000
    participant QA as Quinn Agent
    participant ORCH as Orquestrador

    DEV->>MCP_GIT: tool: create_branch("feat/user-auth")
    MCP_GIT->>GITEA: POST /api/v1/repos/clawdevs/app/branches
    GITEA-->>MCP_GIT: {branch: "feat/user-auth"}
    MCP_GIT-->>DEV: ✅ branch criada

    DEV->>MCP_GIT: tool: commit_files([...], "feat: add JWT auth")
    MCP_GIT->>GITEA: POST /api/v1/repos/clawdevs/app/contents/*
    GITEA-->>MCP_GIT: commit SHA
    MCP_GIT-->>DEV: ✅ commit feito

    DEV->>MCP_GIT: tool: create_pull_request("feat/user-auth", "main")
    MCP_GIT->>GITEA: POST /api/v1/repos/clawdevs/app/pulls
    GITEA-->>MCP_GIT: {pr_number: 42}
    GITEA->>ORCH: webhook: pull_request.opened (PR#42)

    ORCH->>QA: TASK_DELEGATE: review_pr(42)
    QA->>MCP_GIT: tool: get_pr_diff(42)
    MCP_GIT->>GITEA: GET /api/v1/repos/clawdevs/app/pulls/42/files
    QA->>QA: Analisa diff com LLM
    QA->>MCP_GIT: tool: add_pr_review(42, comments, "REQUEST_CHANGES")
    QA->>ORCH: TASK_RESULT: review_done
```

### MCP Server Gitea (implementação)

```python
# mcp_servers/gitea/server.py
from mcp.server import MCPServer
import httpx

GITEA_BASE = "http://gitea-svc:3000/api/v1"
GITEA_TOKEN = os.getenv("GITEA_AGENT_TOKEN")
HEADERS = {"Authorization": f"token {GITEA_TOKEN}"}

server = MCPServer("mcp-gitea")

@server.tool("create_branch")
async def create_branch(repo: str, branch: str, from_branch: str = "main") -> dict:
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{GITEA_BASE}/repos/clawdevs/{repo}/branches",
            headers=HEADERS,
            json={"new_branch_name": branch, "old_branch_name": from_branch},
        )
    return r.json()

@server.tool("create_pull_request")
async def create_pull_request(
    repo: str, title: str, head: str, base: str = "main",
    body: str = "", assignees: list[str] | None = None
) -> dict:
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{GITEA_BASE}/repos/clawdevs/{repo}/pulls",
            headers=HEADERS,
            json={"title": title, "head": head, "base": base,
                  "body": body, "assignees": assignees or []},
        )
    return r.json()

@server.tool("add_pr_review")
async def add_pr_review(
    repo: str, pr_number: int,
    body: str, event: str,  # "APPROVE" | "REQUEST_CHANGES" | "COMMENT"
    comments: list[dict] | None = None
) -> dict:
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{GITEA_BASE}/repos/clawdevs/{repo}/pulls/{pr_number}/reviews",
            headers=HEADERS,
            json={"body": body, "event": event, "comments": comments or []},
        )
    return r.json()
```

### Webhooks Gitea → Orquestrador

```yaml
# Configurar no Gitea UI ou API após bootstrap
events:
  - push           → ORCH: ci_pipeline_trigger
  - pull_request   → ORCH: pr_review_request
  - issues         → ORCH: issue_triage
  - release        → ORCH: deploy_trigger
```

---

## 3. Integração Redis — Pub/Sub vs Streams

| Cenário | Use Streams | Use Pub/Sub |
|---------|-------------|-------------|
| Tarefas A2A | ✅ (persistência, replay) | ❌ |
| Notificações broadcast em tempo real | ❌ | ✅ (menor latência) |
| Dashboard updates ao vivo | ❌ | ✅ |
| Audit log | ✅ | ❌ |
| Heartbeats | ❌ | ✅ |

```python
# Pub/Sub para dashboard real-time
import redis.asyncio as aioredis

redis_pubsub = aioredis.from_url("redis://redis-svc:6379")

async def publish_dashboard_event(event_type: str, data: dict):
    """Publica evento para o dashboard via pub/sub."""
    await redis_pubsub.publish(
        "clawdevs.dashboard",
        json.dumps({"type": event_type, "ts": time.time(), "data": data})
    )

# Uso nos agentes:
await publish_dashboard_event("task_started", {
    "agent": "dev-dev",
    "task_id": task_id,
    "description": "Implementando auth JWT"
})
```

---

## 4. Integração OpenRouter (Fallback Inference)

```mermaid
flowchart TD
    AGENT[Agente] --> CHECK{Ollama\ndisponível?}
    CHECK -->|Sim + GPU OK| OLLAMA[Ollama Local\ncusto: $0]
    CHECK -->|Não / timeout 3s| KILL{Kill switch\n$50/mês?}
    KILL -->|Limite OK| OR_MODEL{Seleciona\nmodelo cloud}
    KILL -->|Limite atingido| BLOCK[❌ Bloqueia\nNotifica Diretor]

    OR_MODEL -->|CEO/PO| CLAUDE["Claude 3.5 Sonnet\nanth_..."]
    OR_MODEL -->|Dev/Arch| DEEPSEEK["DeepSeek R1\ndeepseek/..."]
    OR_MODEL -->|QA| LLAMA["Llama 70B\nmeta-llama/..."]

    OLLAMA & CLAUDE & DEEPSEEK & LLAMA --> RESPONSE[Resposta]
    RESPONSE --> AGENT
```

```python
# inference/router.py
import httpx, os, time

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
MONTHLY_LIMIT_USD = float(os.getenv("OPENROUTER_KILL_SWITCH_USD", "50.0"))

AGENT_MODELS = {
    "claw-ceo":  {"ollama": "qwen2.5:14b",       "cloud": "anthropic/claude-sonnet-4-5"},
    "priya-po":  {"ollama": "qwen2.5:14b",       "cloud": "meta-llama/llama-3.3-70b"},
    "axel-arch": {"ollama": "qwen2.5-coder:14b", "cloud": "anthropic/claude-sonnet-4-5"},
    "dev-dev":   {"ollama": "qwen2.5-coder:14b", "cloud": "deepseek/deepseek-r1"},
    "quinn-qa":  {"ollama": "qwen2.5-coder:7b",  "cloud": "meta-llama/llama-3.3-70b"},
}

async def call_inference(agent_id: str, messages: list, temperature: float = 0.7):
    models = AGENT_MODELS[agent_id]

    # 1. Tenta Ollama local
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                "http://ollama-svc:11434/api/chat",
                json={"model": models["ollama"], "messages": messages,
                      "stream": False, "options": {"temperature": temperature}},
            )
            if r.status_code == 200:
                await track_inference("ollama", agent_id, cost=0.0)
                return r.json()["message"]["content"]
    except Exception:
        pass  # Ollama offline → fallback

    # 2. Kill switch check
    current_spend = await get_monthly_spend()
    if current_spend >= MONTHLY_LIMIT_USD:
        await notify_director(f"⚠️ OpenRouter kill switch ativado. Gasto: ${current_spend:.2f}")
        raise Exception("OpenRouter budget exceeded")

    # 3. OpenRouter cloud
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}",
                     "HTTP-Referer": "https://clawdevs.ai"},
            json={"model": models["cloud"], "messages": messages,
                  "temperature": temperature},
        )
        data = r.json()
        cost = data.get("usage", {}).get("total_cost", 0.001)
        await track_inference("openrouter", agent_id, cost=cost)
        return data["choices"][0]["message"]["content"]
```

---

## 5. MCP Servers — Configuração Completa

```yaml
# k8s/configmaps/mcp-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-server-config
  namespace: clawdevs-agents
data:
  servers.json: |
    {
      "mcpServers": {
        "filesystem": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem",
                   "/workspace", "/data/artifacts"],
          "description": "Acesso ao workspace e artefatos"
        },
        "gitea": {
          "command": "python",
          "args": ["/mcp/gitea/server.py"],
          "env": {"GITEA_AGENT_TOKEN": "${GITEA_AGENT_TOKEN}",
                  "GITEA_BASE_URL": "http://gitea-svc:3000"},
          "description": "SCM: branches, commits, PRs, issues"
        },
        "postgres": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-postgres",
                   "${POSTGRES_CONN_STR}"],
          "description": "Banco de dados de auditoria e métricas"
        },
        "qdrant": {
          "command": "python",
          "args": ["/mcp/qdrant/server.py"],
          "env": {"QDRANT_HOST": "qdrant-svc:6333"},
          "description": "Busca semântica na memória vetorial"
        },
        "fetch": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-fetch"],
          "description": "HTTP fetch para APIs externas (somente GET)"
        }
      }
    }
```

---

## 6. Event-Driven Integration — Fluxo Completo

```mermaid
sequenceDiagram
    participant DIR as Diretor
    participant OC as OpenClaw
    participant ORCH as Orquestrador
    participant REDIS as Redis Streams
    participant AGENT as Agente
    participant GITEA as Gitea
    participant DASH as Dashboard

    DIR->>OC: "#dev implementa login com Google"
    OC->>ORCH: POST /hooks/agent {text, chat_id, channel}
    ORCH->>REDIS: XADD clawdevs.a2a {task, dest: dev-dev}
    REDIS-->>DASH: PUBLISH clawdevs.dashboard {task_queued}
    DASH-->>DIR: 🔔 "Nova task para Dev"

    REDIS-->>AGENT: XREADGROUP (mensagem)
    AGENT->>REDIS: PUBLISH clawdevs.dashboard {task_started}
    DASH-->>DIR: 🔔 "Dev iniciou implementação"

    AGENT->>GITEA: MCP: create_branch + commit
    GITEA->>ORCH: webhook: push event
    AGENT->>GITEA: MCP: create_pull_request
    GITEA->>ORCH: webhook: pr.opened
    ORCH->>REDIS: XADD clawdevs.a2a {task, dest: quinn-qa}

    Note over AGENT: PR#43 criado
    AGENT->>OC: POST /send {text: "✅ PR#43 criado"}
    OC->>DIR: "✅ Dev: PR#43 pronto para review"
    REDIS-->>DASH: PUBLISH {pr_created, pr_number: 43}
```

---

## Checklist de Integrações por Fase

```mermaid
graph TD
    P1["🟡 Fase 1 (Semana 1-2)\nFundação"]
    P2["🟠 Fase 2 (Semana 3-6)\nCore"]
    P3["🟢 Fase 3 (Semana 7-12)\nProdução"]

    P1 --> OC1["✅ OpenClaw + Telegram webhook"]
    P1 --> REDIS1["✅ Redis Streams (5 consumer groups)"]
    P1 --> GITEA1["✅ Gitea bootstrap + repos"]
    P1 --> OLLAMA1["✅ Ollama + qwen2.5 pull"]

    P2 --> MCP2["✅ MCP servers (gitea, pg, qdrant)"]
    P2 --> A2A2["✅ A2A protocol (todos os agentes)"]
    P2 --> OR2["✅ OpenRouter fallback + kill switch"]
    P2 --> PROM2["✅ Prometheus + Grafana"]

    P3 --> WA3["✅ WhatsApp via Baileys"]
    P3 --> DASH3["✅ Dashboard Diretor em tempo real"]
    P3 --> SELFEVOL3["✅ Self-evolution pipeline completo"]
    P3 --> LOKI3["✅ Loki log aggregation"]
```

---

## Variáveis de Ambiente Consolidadas

```env
# OpenClaw
OPENCLAW_AGENT_TOKEN=<Bearer token 256-bit>
TELEGRAM_BOT_TOKEN=<BotFather token>
DIRECTOR_TELEGRAM_ID=<numeric ID>
DIRECTOR_WHATSAPP=<numero+countrycode>

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@redis-svc:6379
REDIS_PASSWORD=<strong password>

# Gitea
GITEA_AGENT_TOKEN=<gitea API token>
GITEA_BASE_URL=http://gitea-svc:3000

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_KILL_SWITCH_USD=50.0

# PostgreSQL
POSTGRES_CONN_STR=postgresql://clawdevs:${PG_PASS}@postgres-svc:5432/clawdevs
POSTGRES_PASSWORD=<strong password>

# Qdrant
QDRANT_HOST=qdrant-svc
QDRANT_PORT=6333

# Segurança interna
INTERNAL_A2A_TOKEN=<openssl rand -hex 32>
INTERNAL_SECRET=<openssl rand -hex 32>
```


