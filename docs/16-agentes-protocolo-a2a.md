# 16  Protocolo A2A e Contexto Compartilhado
> **Objetivo:** Definir o protocolo de comunicação inter-agentes (A2A), formatos de mensagens, e o esquema da memória compartilhada (Redis/Qdrant).
> **Público-alvo:** Devs, Arquitetos
> **Ação Esperada:** Devs implementam novos comportamentos respeitando as chaves de Redis e o contrato JSON do A2A Protocol.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Por que A2A e contexto compartilhado são o diferencial real

```mermaid
graph TD
    subgraph WITHOUT["❌ Sem A2A — Agentes ilhados"]
        A1["Agente A\nfaz tarefa X"]
        A2["Agente B\nfaz tarefa Y"]
        A3["Agente C\nfaz tarefa Z"]
        ORCH1["Orquestrador\npassa mensagens\nmanualmente"]
        A1 & A2 & A3 --- ORCH1
    end

    subgraph WITH["✅ Com A2A — Time real"]
        B1["Architect\ndecide stack"]
        B2["Developer\nrecebe contexto\nda decisão do Arch"]
        B3["QA\nrecebe critérios\ndo PO E contexto do Dev"]
        CTX["Contexto compartilhado\nTodos sabem o que\nos outros fizeram"]
        B1 <-->|"A2A"| B2 <-->|"A2A"| B3
        B1 & B2 & B3 --- CTX
    end
```

---

## Arquitetura A2A do ClawDevs

```mermaid
graph TD
    subgraph GATEWAY["clawdevs-gateway"]
        OC["OpenClaw\n:18789"]
        ORCH["Orquestrador\n:8080"]
    end

    subgraph AGENTS["clawdevs-agents — A2A mesh"]
        CEO_A["🎯 CEO\nAgent Card:\ncapabilities.json"]
        PO_A["📋 PO\nAgent Card:\ncapabilities.json"]
        ARCH_A["🏗️ Architect\nAgent Card:\ncapabilities.json"]
        DEV_A["💻 Developer\nAgent Card:\ncapabilities.json"]
        QA_A["🧪 QA\nAgent Card:\ncapabilities.json"]
    end

    subgraph BROKER["Message Broker — Filas em Memória"]
        STREAM_IN["queue:agent.{id}.inbox"]
        STREAM_OUT["queue:agent.{id}.outbox"]
        STREAM_BROAD["queue:team.broadcast"]
        STREAM_CTX["queue:project.context"]
    end

    subgraph MEMORY["Memória Local (K8s PVC)"]
        HD["Sistemas de Arquivos\nJSON e Markdown\nADRs, estado e histórico"]
        LOGS["Log Imutável\nArquivos de auditoria append-only"]
        STATE["Memória Efêmera\nEstado da tarefa em curso"]
    end

    OC --> ORCH
    ORCH --> CEO_A & PO_A & ARCH_A & DEV_A & QA_A

    CEO_A <-->|"A2A direto"| PO_A & ARCH_A
    PO_A <-->|"A2A direto"| DEV_A & QA_A
    ARCH_A <-->|"A2A direto"| DEV_A
    DEV_A <-->|"A2A direto"| QA_A

    AGENTS --> BROKER
    BROKER --> MEMORY

    style BROKER fill:#D9770622,stroke:#D97706
    style MEMORY fill:#2563EB22,stroke:#2563EB
```

---

## Agent Card — formato de autodescoberta

Cada agente publica um `Agent Card` (padrão A2A Protocol) que outros agentes consultam para saber o que ele pode fazer:

```json
{
  "id": "clawdevs/architect",
  "name": "Axel — Architect Agent",
  "version": "1.0.0",
  "description": "Responsible for architecture decisions, ADRs, and PR security reviews.",
  "capabilities": {
    "acceptsMessages": true,
    "canDelegate": true,
    "supportedTaskTypes": [
      "architecture_review",
      "adr_creation",
      "pr_review",
      "k8s_manifest_validation",
      "tech_decision"
    ]
  },
  "authentication": {
    "type": "bearer",
    "scope": "internal"
  },
  "endpoint": "http://agent-architect-service.clawdevs-agents:8090/a2a",
  "soulVersion": "1.0",
  "model": "qwen2.5-coder:14b",
  "securityLevel": "paranoid"
}
```

---

## Protocolo de mensagens A2A

```mermaid
sequenceDiagram
    participant DEV as 💻 Developer
    participant ARCH as 🏗️ Architect
    participant CTX as Contexto Compartilhado

    DEV->>ARCH: A2A Request\n{taskType: "architecture_review",\n payload: "Quero usar MongoDB. Faz sentido?",\n context_id: "project:clawdevs:task:42"}

    ARCH->>CTX: GET context_id: project:clawdevs:task:42
    CTX-->>ARCH: {stack: "K8s PVC local definido no ADR-001,\nFilas em memória para estado"}

    ARCH->>ARCH: Analisa com contexto completo

    ARCH-->>DEV: A2A Response\n{decision: "rejected",\n rationale: "Armazenamento local resolve isso. ADR-001.",\n alternative: "Use arquivo JSON se precisar de schema flexível",\n adr_reference: "ADR-001"}

    DEV->>CTX: APPEND decision_log\n{agent: "architect", decision: "rejected MongoDB", reason: "ADR-001"}
```

---

## Modelo de contexto compartilhado — 3 camadas

```mermaid
graph LR
    subgraph HOT["🔥 Hot — Memória RAM (< 1ms)"]
        H1["task:{id}:current_state\nO que está acontecendo agora"]
        H2["task:{id}:agents_involved\nQuem está trabalhando nessa tarefa"]
        H3["task:{id}:last_decision\nÚltima decisão tomada"]
        H4["project:context_summary\nResumo do projeto em 2k tokens"]
    end

    subgraph WARM["🌡️ Warm — Arquivos (< 50ms)"]
        W1["ADRs indexados\nbusca semântica por problema técnico"]
        W2["Issues resolvidas\ncomo esse problema foi resolvido antes?"]
        W3["PR comments histórico\npadrões de revisão do Architect"]
        W4["SOUL embeddings\no que cada agente sabe fazer"]
    end

    subgraph COLD["❄️ Cold — Logs em Disco (< 200ms)"]
        C1["Log imutável de todas\nas interações A2A"]
        C2["Histórico completo\nde decisões e seus outcomes"]
        C3["Auditoria de segurança\nquem fez o quê e quando"]
    end

    AGENT["Agente recebe tarefa"]
    ENRICH["Contexto enriquecido\n= tarefa + decisões passadas\n+ padrões do time\n+ estado atual"]

    AGENT -->|"1. busca estado atual"| HOT
    AGENT -->|"2. busca conhecimento relevante"| WARM
    AGENT -->|"3. busca histórico se necessário"| COLD
    HOT & WARM & COLD --> ENRICH
    ENRICH -->|"agente executa com contexto completo"| AGENT
```

---

## Fluxo completo de uma conversa A2A real

```mermaid
sequenceDiagram
    actor DIR as 👤 Diretor
    participant OC as OpenClaw
    participant CEO as 🎯 CEO
    participant PO as 📋 PO
    participant ARCH as 🏗️ Architect
    participant DEV as 💻 Developer
    participant QA as 🧪 QA
    participant CTX as Contexto Compartilhado

    DIR->>OC: "#dev Implemente sistema de autenticação JWT"
    OC->>CEO: dispatch task (high priority)
    CEO->>CTX: WRITE task:auth-jwt:status = "planning"
    CEO->>PO: A2A: "Preciso de critérios para auth JWT"
    PO->>CTX: READ project:stack (Python, FastAPI, Local Storage)
    PO->>ARCH: A2A: "Há alguma decisão arquitetural sobre auth?"
    ARCH->>CTX: READ ADRs semântico "autenticação"
    CTX-->>ARCH: ADR-002: "JWT com refresh tokens, secret via K8s"
    ARCH-->>PO: A2A: "Sim — ADR-002 define padrão JWT. Seguir isso."
    PO->>CTX: WRITE task:auth-jwt:acceptance_criteria
    PO-->>CEO: A2A: "Critérios definidos com base no ADR-002"
    CEO->>DEV: A2A: "Implementar issue #auth-jwt conforme ADR-002 + critérios"
    DEV->>CTX: READ task:auth-jwt (critérios + ADR-002 + stack)
    DEV->>DEV: implementa com contexto completo
    DEV->>CTX: WRITE task:auth-jwt:pr_url = "#PR-17"
    DEV->>QA: A2A: "PR #17 pronto para revisão"
    QA->>CTX: READ task:auth-jwt:acceptance_criteria
    QA->>QA: executa testes contra critérios
    QA->>ARCH: A2A: "PR #17 funcional. Precisa aprovação arquitetural."
    ARCH->>CTX: READ task:auth-jwt + ADR-002
    ARCH->>ARCH: valida segurança e padrões
    ARCH-->>QA: A2A: "Aprovado. Sem violações de segurança."
    QA->>DEV: A2A: "PR aprovado — pode mergear"
    DEV->>CTX: WRITE task:auth-jwt:status = "merged"
    CEO->>CTX: READ task:auth-jwt:summary
    CEO-->>DIR: via OpenClaw: "✅ Auth JWT implementado (PR #17). ADR-002 respeitado. Testes passando."
```

---

## Schema do contexto compartilhado (Em Memória / Arquivos)

```python
# Estrutura de estado na memória efêmera e arquivos

# Estado global do projeto
"project:{project_id}:summary"          # resumo em 2k tokens, atualizado pelo CEO
"project:{project_id}:stack"            # stack técnica definida
"project:{project_id}:principles"       # primícias e políticas ativas
"project:{project_id}:agents_online"    # set de agentes ativos no momento

# Estado de uma tarefa
"task:{task_id}:status"                 # planning|in_progress|review|done|blocked
"task:{task_id}:owner"                  # agente responsável atual
"task:{task_id}:acceptance_criteria"    # critérios do PO
"task:{task_id}:context"                # contexto acumulado da tarefa
"task:{task_id}:pr_url"                 # PR gerado
"task:{task_id}:adr_refs"              # ADRs referenciados

# Histórico de decisões (append-only file log)
"decisions:{project_id}"               # Arquivo / Fila de todas as decisões
# entry: {agent, decision, rationale, timestamp, task_id}

# Canal de broadcast do time
"team:broadcast"                        # Fila em memória — mensagens para todos os agentes
"team:alerts"                           # alertas críticos (CEO → Diretor)
```

---

## Implementação do A2A endpoint por agente

```python
# Estrutura base do A2A endpoint (cada agente implementa)
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

class A2ARequest(BaseModel):
    task_type: str
    payload: str
    context_id: str
    requesting_agent: str
    priority: str = "normal"

class A2AResponse(BaseModel):
    status: str           # accepted | rejected | delegated
    result: str
    rationale: str
    context_updated: bool

@app.post("/a2a")
async def handle_a2a(
    request: A2ARequest,
    authorization: str = Header(...)
):
    # 1. Validar token Bearer inter-agente
    verify_internal_token(authorization)

    # 2. Verificar se esta tarefa é competência deste agente
    if request.task_type not in SOUL["capabilities"]["supportedTaskTypes"]:
        raise HTTPException(400, "Task type not supported by this agent")

    # 3. Enriquecer contexto com estado atual e histórico
    context = await enrich_context(request.context_id)

    # 4. Processar com LLM (Ollama local)
    result = await process_with_llm(
        soul=SOUL,
        task=request.payload,
        context=context
    )

    # 5. Persistir decisão no contexto compartilhado
    await update_shared_context(request.context_id, result)

    return A2AResponse(
        status="accepted",
        result=result.output,
        rationale=result.rationale,
        context_updated=True
    )
```

---

## Segurança no A2A

```mermaid
graph TD
    REQUEST["A2A Request recebida"]

    C1{"Token Bearer\ninternalvalido?"}
    C2{"requesting_agent\nna allowlist?"}
    C3{"task_type\npermitido para\nesse requester?"}
    C4{"OPA policy\naprovada?"}
    EXECUTE["✅ Executa e responde"]
    REJECT["❌ 401/403 + log auditoria"]

    REQUEST --> C1
    C1 -->|"Não"| REJECT
    C1 -->|"Sim"| C2
    C2 -->|"Não"| REJECT
    C2 -->|"Sim"| C3
    C3 -->|"Não"| REJECT
    C3 -->|"Sim"| C4
    C4 -->|"Bloqueado"| REJECT
    C4 -->|"Permitido"| EXECUTE

    style REJECT fill:#DC262622,stroke:#DC2626
    style EXECUTE fill:#05966922,stroke:#059669
```

**Regras de segurança A2A:**
- Nenhum agente pode se passar por outro (token por agente)
- QA não pode pedir ao Developer para alterar testes
- Nenhum agente pode acionar o modo self_evolution via A2A (só o Diretor via OpenClaw)
- Toda mensagem A2A é logada em arquivo de auditoria (append-only)
- Circuit breaker: se agente não responde em 30s, orquestrador assume

---

---

## Visão Geral dos Canais de Comunicação

```mermaid
graph TD
    subgraph EXTERNO["Canal Externo (Diretor → Sistema)"]
        TG[Telegram Bot]
        WA[WhatsApp]
        SL[Slack]
    end

    subgraph GATEWAY["OpenClaw Gateway :18789"]
        ROUTER[Message Router]
        SESS[Session Manager]
        MAUTH[Auth Middleware]
    end

    subgraph ORCHESTRATOR["Orquestrador (LangGraph)"]
        DISPATCH[Task Dispatcher]
        QUEUE[Priority Queue\nRedis Streams]
        TRACKER[State Tracker]
    end

    subgraph AGENTS["Pods de Agentes (Kubernetes)"]
        CEO[Claw CEO\n:8001]
        PO[Priya PO\n:8002]
        ARCH[Axel Arch\n:8003]
        DEV[Dev Dev\n:8004]
        QA[Quinn QA\n:8005]
    end

    subgraph INTERNAL["Barramento Interno (Redis Streams)"]
        S_A2A[Stream: clawdevs.a2a]
        S_EVENTS[Stream: clawdevs.events]
        S_AUDIT[Stream: clawdevs.audit]
    end

    TG -->|webhook POST| ROUTER
    WA -->|webhook POST| ROUTER
    SL -->|webhook POST| ROUTER

    ROUTER --> MAUTH
    MAUTH --> SESS
    SESS --> DISPATCH

    DISPATCH --> QUEUE
    QUEUE --> CEO & PO & ARCH & DEV & QA

    CEO <-->|A2A via Redis| S_A2A
    PO <-->|A2A via Redis| S_A2A
    ARCH <-->|A2A via Redis| S_A2A
    DEV <-->|A2A via Redis| S_A2A
    QA <-->|A2A via Redis| S_A2A

    CEO & PO & ARCH & DEV & QA --> S_EVENTS
    S_EVENTS --> TRACKER
    S_A2A --> S_AUDIT
```

---

## Protocolo de Mensagem Interna (A2A Message Format)

Toda mensagem entre agentes segue o schema padrão A2A (Linux Foundation draft v0.2):

```json
{
  "a2a_version": "0.2",
  "message_id": "msg_01JXYZ789ABC",
  "correlation_id": "task_01JXYZ123DEF",
  "timestamp": "2026-03-06T10:30:00Z",
  "source": {
    "agent_id": "claw-ceo",
    "agent_role": "ceo",
    "pod": "claw-ceo-5f9d8b-xk2p",
    "namespace": "clawdevs-agents"
  },
  "destination": {
    "agent_id": "axel-arch",
    "agent_role": "architect",
    "broadcast": false
  },
  "message_type": "TASK_DELEGATE",
  "priority": "HIGH",
  "payload": {
    "task_type": "architecture_review",
    "description": "Revisar ADR-005 para implementação de circuit breaker",
    "context_id": "ctx_01JXYZ456GHI",
    "attachments": ["adr-005-draft.md"],
    "deadline": "2026-03-06T14:00:00Z",
    "requires_response": true
  },
  "routing": {
    "reply_to": "stream:clawdevs.a2a",
    "reply_stream_key": "claw-ceo",
    "ttl_seconds": 3600
  },
  "auth": {
    "token": "Bearer ${INTERNAL_A2A_TOKEN}",
    "hmac_sha256": "e3b0c44298fc1c149afb..."
  }
}
```

### Tipos de Mensagem

| Tipo | Direção | Descrição |
|------|---------|-----------|
| `TASK_DELEGATE` | Orq → Agente ou Agente → Agente | Delega tarefa específica |
| `TASK_ACCEPT` | Agente → Emissor | Confirmação de recebimento |
| `TASK_RESULT` | Agente → Emissor | Resultado/entrega da tarefa |
| `TASK_REJECT` | Agente → Emissor | Recusa com motivo (fora do SOUL) |
| `CONTEXT_REQUEST` | Agente → Redis | Busca contexto compartilhado |
| `CONTEXT_UPDATE` | Agente → Redis | Atualiza contexto compartilhado |
| `BROADCAST_ALERT` | Qualquer → Todos | Alerta crítico para todos os agentes |
| `SELF_EVOLUTION_PROPOSAL` | Agente → Diretor | Proposta de evolução do SOUL |
| `HEARTBEAT` | Agente → Monitor | Sinal de vida (a cada 15s) |
| `CAPABILITY_QUERY` | Agente → Agente | Pergunta quais tasks outro agente aceita |

---

## Redis Streams — Implementação Detalhada

### Estrutura dos Streams

```
clawdevs.a2a          → Mensagens A2A entre agentes
clawdevs.events       → Eventos de ciclo de vida (task started/completed/failed)
clawdevs.audit        → Log imutável de auditoria (append-only)
clawdevs.director     → Notificações para o Diretor
clawdevs.metrics      → Métricas em tempo real (para dashboard)
clawdevs.deadletter   → Mensagens não processadas após max_retries
```

### Consumer Groups por Agente

```python
# Configuração inicial dos streams (executar 1x no bootstrap)
import redis

r = redis.Redis.from_url("redis://redis-svc:6379")

streams = {
    "clawdevs.a2a": ["claw-ceo", "priya-po", "axel-arch", "dev-dev", "quinn-qa"],
    "clawdevs.events": ["orchestrator", "dashboard-service"],
    "clawdevs.metrics": ["dashboard-service", "prometheus-exporter"],
    "clawdevs.deadletter": ["orchestrator"],
}

for stream, groups in streams.items():
    for group in groups:
        try:
            r.xgroup_create(stream, group, id="0", mkstream=True)
            print(f"✅ Created consumer group '{group}' on stream '{stream}'")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"ℹ️  Group '{group}' already exists on '{stream}'")
```

### Produzindo Mensagens A2A

```python
# Dentro de qualquer agente (FastAPI + asyncio)
import redis.asyncio as aioredis
import json, uuid, hmac, hashlib, time

redis_client = aioredis.from_url("redis://redis-svc:6379")

async def send_a2a_message(
    destination_agent: str,
    task_type: str,
    payload: dict,
    priority: str = "NORMAL",
    correlation_id: str | None = None,
) -> str:
    message_id = f"msg_{uuid.uuid4().hex[:12]}"
    body = {
        "a2a_version": "0.2",
        "message_id": message_id,
        "correlation_id": correlation_id or f"task_{uuid.uuid4().hex[:12]}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": {"agent_id": AGENT_ID, "agent_role": AGENT_ROLE},
        "destination": {"agent_id": destination_agent},
        "message_type": "TASK_DELEGATE",
        "priority": priority,
        "payload": {"task_type": task_type, **payload},
        "routing": {"reply_to": "stream:clawdevs.a2a", "reply_stream_key": AGENT_ID},
    }

    # HMAC para integridade
    body["auth"] = {
        "hmac_sha256": hmac.new(
            INTERNAL_SECRET.encode(),
            json.dumps(body, sort_keys=True).encode(),
            hashlib.sha256,
        ).hexdigest()
    }

    stream_id = await redis_client.xadd(
        "clawdevs.a2a",
        {"data": json.dumps(body), "dest": destination_agent, "priority": priority},
    )
    return stream_id
```

### Consumindo Mensagens (Consumer Loop)

```python
async def consume_a2a_messages():
    """Loop principal do agente — lê mensagens do stream Redis."""
    consumer_name = f"{AGENT_ID}-{POD_NAME}"

    while True:
        try:
            messages = await redis_client.xreadgroup(
                groupname=AGENT_ID,
                consumername=consumer_name,
                streams={"clawdevs.a2a": ">"},   # ">" = apenas não lidas
                count=5,          # máximo 5 mensagens por lote
                block=5000,       # aguarda 5s se fila vazia
            )
            for stream, entries in (messages or []):
                for entry_id, fields in entries:
                    msg = json.loads(fields[b"data"])
                    dest = fields[b"dest"].decode()

                    if dest != AGENT_ID and dest != "broadcast":
                        # Mensagem não é para mim — NACK e ignora
                        await redis_client.xack("clawdevs.a2a", AGENT_ID, entry_id)
                        continue

                    # Processa a mensagem
                    await process_a2a_message(msg)

                    # ACK após processamento bem-sucedido
                    await redis_client.xack("clawdevs.a2a", AGENT_ID, entry_id)

        except Exception as e:
            # Log sem crash — loop resiliente
            await log_error(f"A2A consume error: {e}")
            await asyncio.sleep(1)
```

---

## Roteamento por Hashtag (Diretor → Orquestrador)

```mermaid
flowchart TD
    MSG["Mensagem do Diretor\n(Telegram/WhatsApp)"]

    MSG --> PARSE{Parse\nHashtag}

    PARSE -->|#ceo| CEO["Claw → CEO\nDecisão estratégica"]
    PARSE -->|#po| PO["Priya → PO\nPriorização / backlog"]
    PARSE -->|#arch| ARCH["Axel → Arquiteto\nDecisão técnica"]
    PARSE -->|#dev| DEV["Dev → Dev\nImplementação"]
    PARSE -->|#qa| QA["Quinn → QA\nTestes / qualidade"]
    PARSE -->|#time| ALL["Broadcast → TODOS\n(via clawdevs.a2a broadcast)"]
    PARSE -->|#evolui| EVOL["Self-Evolution\nPipeline de PR"]
    PARSE -->|sem hashtag| AUTO{"Auto-roteamento\npor NLP"}

    AUTO -->|keyword: bug/error| QA
    AUTO -->|keyword: arquitetura/design| ARCH
    AUTO -->|keyword: prazo/sprint| PO
    AUTO -->|"keyword: implanta/deploy"| DEV
    AUTO -->|não classificado| CEO

    CEO & PO & ARCH & DEV & QA & ALL & EVOL --> RESP["Resposta via\nOpenClaw → Canal original"]
```

### Implementação do Parser de Hashtag

```python
import re

HASHTAG_MAP = {
    "#ceo": "claw-ceo",
    "#po": "priya-po",
    "#arch": "axel-arch",
    "#dev": "dev-dev",
    "#qa": "quinn-qa",
    "#time": "broadcast",
    "#evolui": "self_evolution",
}

NLP_KEYWORDS = {
    "claw-ceo":  ["estratégia", "decisão", "prioridade", "visão", "negócio"],
    "priya-po":  ["sprint", "backlog", "épico", "story", "prazo", "release"],
    "axel-arch": ["arquitetura", "design", "adr", "padrão", "infraestrutura"],
    "dev-dev":   ["implementa", "código", "bug", "feature", "deploy", "commit"],
    "quinn-qa":  ["teste", "qualidade", "bug", "erro", "regressão", "cobertura"],
}

def route_message(text: str) -> str:
    """Retorna agent_id de destino baseado em hashtag ou NLP."""
    tags = re.findall(r"#\w+", text.lower())
    for tag in tags:
        if tag in HASHTAG_MAP:
            return HASHTAG_MAP[tag]

    # Fallback: NLP por keywords
    text_lower = text.lower()
    for agent_id, keywords in NLP_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return agent_id

    return "claw-ceo"  # Fallback final: CEO decide
```

---

## Contexto Compartilhado — 3 Camadas

```mermaid
graph LR
    A[Agente] -->|escrita/leitura <1ms| HOT["🔴 HOT — Redis\n• Estado atual de tasks\n• Context_id ativo\n• Lock de recursos\n• TTL: 24h"]
    A -->|busca semântica <50ms| WARM["🟡 WARM — Qdrant\n• Embeddings de decisões\n• Histórico de contexto\n• ADRs / docs técnicos\n• Permanente"]
    A -->|auditoria <200ms| COLD["🔵 COLD — PostgreSQL\n• Log imutável\n• Evidências de segurança\n• Métricas históricas\n• Append-only"]

    HOT -->|flush assíncrono a cada 5min| COLD
    WARM -->|indexa novos docs| A
```

### Schema Redis (Hot Context)

```
# Task state
task:{task_id}:state       → PENDING | RUNNING | BLOCKED | DONE | FAILED
task:{task_id}:owner       → agent_id do responsável atual
task:{task_id}:context     → JSON com contexto completo
task:{task_id}:deadline    → unix timestamp

# Shared context entre agentes
ctx:{context_id}:summary   → Resumo acumulado da conversa/task
ctx:{context_id}:agents    → Lista de agentes envolvidos
ctx:{context_id}:artifacts → Paths de arquivos produzidos

# Resource locks (evita conflitos)
lock:file:{path}           → agent_id (TTL: 5min, renovável)
lock:pr:{number}           → agent_id (TTL: 30min)
lock:deploy                → agent_id (TTL: 60min)

# Capacidades descobertas (Agent Card cache)
agent:{agent_id}:card      → JSON do Agent Card (TTL: 1h)
agent:{agent_id}:status    → IDLE | BUSY | UNAVAILABLE
agent:{agent_id}:heartbeat → unix timestamp (atualizado a cada 15s)
```

---

## Segurança de Canal

```mermaid
sequenceDiagram
    participant A as Agente A
    participant REDIS as Redis Streams
    participant B as Agente B
    participant AUDIT as Audit Log

    A->>A: Gera HMAC-SHA256(payload, INTERNAL_SECRET)
    A->>REDIS: XADD clawdevs.a2a {data, hmac, dest}
    REDIS-->>B: XREADGROUP (mensagem disponível)
    B->>B: Verifica HMAC → rejeita se inválido
    B->>B: Valida dest == próprio agent_id
    B->>B: Verifica TTL da mensagem (não aceita >1h)
    B->>B: Dedup: message_id já processado? → descarta
    B->>AUDIT: XADD clawdevs.audit {msg_id, from, to, action, ts}
    B->>B: Processa tarefa
    B->>REDIS: XADD clawdevs.a2a (resposta para A)
    B->>REDIS: XACK (confirma processamento)
```

### Chaves de Segurança (K8s Secrets)

```yaml
# k8s/secrets/a2a-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: a2a-secrets
  namespace: clawdevs-agents
type: Opaque
data:
  # openssl rand -hex 32 | base64
  INTERNAL_A2A_TOKEN: <base64>
  INTERNAL_SECRET: <base64>
  REDIS_PASSWORD: <base64>
```

---

## Padrões de Comunicação Avançados

### 1. Request-Reply com Timeout

```python
async def request_with_timeout(
    destination: str,
    task_type: str,
    payload: dict,
    timeout_seconds: int = 120,
) -> dict | None:
    correlation_id = f"req_{uuid.uuid4().hex[:12]}"

    await send_a2a_message(destination, task_type, payload,
                           correlation_id=correlation_id)

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        # Lê stream de resposta do próprio agente
        replies = await redis_client.xread(
            {f"reply:{AGENT_ID}:{correlation_id}": "0-0"}, count=1, block=1000
        )
        if replies:
            return json.loads(replies[0][1][0][1][b"data"])

    # Timeout — aciona circuit breaker
    await circuit_breaker.record_failure(destination)
    return None
```

### 2. Broadcast com Quorum

```python
async def broadcast_and_wait_quorum(
    task_type: str, payload: dict, min_responses: int = 3, timeout: int = 60
) -> list[dict]:
    """Envia para todos e aguarda N respostas."""
    correlation_id = f"bcast_{uuid.uuid4().hex[:12]}"
    agents = ["claw-ceo", "priya-po", "axel-arch", "dev-dev", "quinn-qa"]
    responses = []

    for agent in agents:
        await send_a2a_message(agent, task_type, payload,
                               correlation_id=correlation_id)

    deadline = time.time() + timeout
    while len(responses) < min_responses and time.time() < deadline:
        # Coleta respostas...
        await asyncio.sleep(0.5)

    return responses
```

### 3. Saga Pattern (Transação Distribuída)

```mermaid
sequenceDiagram
    participant ORCH as Orquestrador
    participant PO as Priya (PO)
    participant ARCH as Axel (Arch)
    participant DEV as Dev
    participant QA as Quinn

    ORCH->>PO: SAGA_START: nova feature
    PO->>ORCH: SAGA_STEP_DONE: spec aprovada
    ORCH->>ARCH: SAGA_STEP: desenha arquitetura
    ARCH->>ORCH: SAGA_STEP_DONE: ADR criado

    ORCH->>DEV: SAGA_STEP: implementa
    DEV--xORCH: SAGA_STEP_FAILED: bloqueio técnico

    Note over ORCH: Rollback saga
    ORCH->>ARCH: SAGA_COMPENSATE: reverte ADR
    ORCH->>PO: SAGA_COMPENSATE: volta spec para draft
    ORCH->>ORCH: SAGA_FAILED: notifica Diretor
```

---

## Monitoramento de Comunicação

```mermaid
graph TD
    STREAMS[Redis Streams] -->|consumer| PROM_EXP[Prometheus Exporter\nclawdevs-metrics:9090]
    PROM_EXP --> PROM[Prometheus]
    PROM --> GRAFANA[Grafana Dashboard]

    METRICS["Métricas coletadas:\n• a2a_messages_total\n• a2a_latency_p99\n• a2a_errors_total\n• agent_queue_depth\n• circuit_breaker_state\n• dead_letter_count"]
    PROM_EXP -.-> METRICS
```

### Alertas Críticos (AlertManager)

| Alerta | Condição | Severidade | Ação |
|--------|----------|-----------|------|
| `AgentHeartbeatMissing` | heartbeat > 45s ausente | CRÍTICO | Restart pod + notifica Diretor |
| `A2AHighLatency` | p99 > 500ms em 5min | ALTO | Log + alerta Slack |
| `DeadLetterQueueGrowing` | DLQ > 10 mensagens | ALTO | Alerta Diretor |
| `CircuitBreakerOpen` | CB aberto > 60s | ALTO | Log + fallback manual |
| `QueueDepthHigh` | fila > 50 msgs/agente | MÉDIO | Auto-scale (se ativado) |
| `HMACValidationFailed` | qualquer falha HMAC | CRÍTICO | Security alert + block |

---
