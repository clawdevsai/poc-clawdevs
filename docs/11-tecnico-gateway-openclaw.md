# 11 — Gateway de Comunicação (OpenClaw)
> **Objetivo:** Definir a arquitetura, roteamento e segurança do gateway central OpenClaw.
> **Público-alvo:** Devs, DevOps
> **Ação Esperada:** Devs implementam os endpoints de webhook descritos; DevOps mantêm a infra de comunicação.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Posição no stack

```mermaid
graph TD
    subgraph EXTERNAL["Exterior ao cluster"]
        TG["📱 Telegram"]
        SL["💬 Slack"]
        WA["📲 WhatsApp"]
        DC["🎮 Discord"]
    end

    subgraph GW_NS["namespace: clawdevs-gateway"]
        OC["OpenClaw Gateway\npod: openclaw\n:18789\nlicença MIT"]
    end

    subgraph CLUSTER["Cluster interno"]
        ORCH["Orquestrador\n/hooks/agent"]
        AGENTS["Agentes\nCEO · PO · Arch · Dev · QA"]
    end

    TG & SL & WA & DC -->|"mensagem do Diretor"| OC
    OC -->|"POST /hooks/agent\nBearer token"| ORCH
    ORCH --> AGENTS
    AGENTS -->|"resposta"| ORCH
    ORCH -->|"resultado"| OC
    OC -->|"entrega no canal"| TG & SL

    style OC fill:#7C3AED,stroke:#5B21B6,color:#fff
    style ORCH fill:#059669,stroke:#047857,color:#fff
```

---

## Fluxo completo de uma mensagem

```mermaid
sequenceDiagram
    actor D as 👤 Diretor
    participant TG as Telegram API
    participant OC as OpenClaw Gateway
    participant OR as Orquestrador
    participant AG as Agente Alvo
    participant OL as Ollama

    D->>TG: "#dev implemente /login com JWT"
    TG->>OC: webhook message event
    OC->>OC: valida allowFrom (chat_id autorizado?)
    OC->>OC: extrai hashtag → route: "developer"

    OC->>OR: POST /hooks/agent\n{agentId:"developer", message:..., channel:"telegram"}
    OR->>OR: valida token Bearer
    OR->>OR: carrega SOUL do agente
    OR->>AG: dispatch(task + soul + context)
    AG->>OL: POST /api/chat {model, messages}
    OL-->>AG: stream de resposta
    AG-->>OR: task_result {output, status}
    OR-->>OC: 202 Accepted + resultado
    OC-->>TG: send_message (Diretor)
    TG-->>D: "✅ Código implementado"
```

---

## Roteamento por hashtag

```mermaid
flowchart TD
    MSG["Mensagem do Diretor"]
    PARSE["OpenClaw\nparseia hashtag"]

    MSG --> PARSE

    PARSE -->|"#ceo"| CEO["🎯 CEO — Claw\nStatus · Relatórios · Bloqueios"]
    PARSE -->|"#po"| PO["📋 PO — Priya\nBacklog · User Stories"]
    PARSE -->|"#arch"| ARCH["🏗️ Architect — Axel\nADRs · PR Review"]
    PARSE -->|"#dev"| DEV["💻 Developer — Dev\nImplementação · Testes"]
    PARSE -->|"#qa"| QA["🧪 QA — Quinn\nValidação · Bugs"]
    PARSE -->|"#time"| BCAST["📢 Broadcast\nTodos os agentes"]
    PARSE -->|"#evolui"| EVOL["🔄 CEO\nmodo self_evolution"]
    PARSE -->|"sem hashtag"| CEO

    style CEO fill:#7C3AED,stroke:#5B21B6,color:#fff
    style PO fill:#2563EB,stroke:#1D4ED8,color:#fff
    style ARCH fill:#D97706,stroke:#B45309,color:#fff
    style DEV fill:#059669,stroke:#047857,color:#fff
    style QA fill:#DC2626,stroke:#B91C1C,color:#fff
    style BCAST fill:#6B7280,stroke:#4B5563,color:#fff
    style EVOL fill:#7C3AED,stroke:#5B21B6,color:#fff
```

---

## Endpoints de webhook (Orquestrador)

```mermaid
graph LR
    subgraph HOOKS["Endpoints /hooks"]
        H1["POST /hooks/agent\nDispara agente específico\n→ 202 Accepted (async)"]
        H2["POST /hooks/wake\nHeartbeat / tarefa agendada\n→ 200 OK"]
        H3["GET /hooks/status\nStatus de todos os agentes\n→ 200 JSON"]
    end

    OC["OpenClaw Gateway"] -->|"Bearer token obrigatório"| H1 & H2 & H3

    subgraph AUTH["Autenticação"]
        A1["Header: Authorization: Bearer token"]
        A2["Header: x-openclaw-token: token"]
        A3["❌ Query string: rejeitado com 400"]
    end

    subgraph CODES["Response codes"]
        C1["200 — wake OK"]
        C2["202 — agent async iniciado"]
        C3["400 — payload inválido"]
        C4["401 — auth falhou"]
        C5["429 — rate limit"]
        C6["413 — payload muito grande"]
    end
```

---

## Payloads de referência

### Acionar agente específico

```json
{
  "message": "Implemente a feature X conforme issue #42",
  "agentId": "developer",
  "channel": "telegram",
  "model": "ollama/qwen2.5-coder:14b",
  "thinking": "high",
  "timeoutSeconds": 300,
  "deliver": true
}
```

### Orquestrador decide o agente (via hashtag)

```json
{
  "message": "#arch revise o ADR-003 sobre banco de dados",
  "channel": "telegram",
  "deliver": true
}
```

### Broadcast para o time

```json
{
  "message": "#time mudança de prioridade: feature Y é crítica agora",
  "channel": "telegram",
  "deliver": true
}
```

### Wake (heartbeat diário)

```json
{
  "text": "daily-standup: CEO gera relatório consolidado",
  "mode": "now"
}
```

---

## Segurança do Gateway

```mermaid
graph TD
    MSG["Mensagem recebida"]

    MSG --> C1{"allowFrom\nvalidado?"}
    C1 -->|"Não"| BLOCK1["❌ Bloqueado\nnão entrega"]
    C1 -->|"Sim"| C2{"Token Bearer\nválido?"}
    C2 -->|"Não"| BLOCK2["❌ 401 Unauthorized\n+ rate limit acumulado"]
    C2 -->|"Sim"| C3{"Payload\n≤ limite?"}
    C3 -->|"Não"| BLOCK3["❌ 413 Payload Too Large"]
    C3 -->|"Sim"| C4{"agentId\nna allowlist?"}
    C4 -->|"Não"| FALLBACK["⚠️ Fallback:\nagente default (CEO)"]
    C4 -->|"Sim"| DISPATCH["✅ Dispatch ao agente"]

    style BLOCK1 fill:#DC262622,stroke:#DC2626
    style BLOCK2 fill:#DC262622,stroke:#DC2626
    style BLOCK3 fill:#DC262622,stroke:#DC2626
    style DISPATCH fill:#05966922,stroke:#059669
    style FALLBACK fill:#D9770622,stroke:#D97706
```

---

## Comandos OpenClaw (CLI)

```bash
# Instalar OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# Setup inicial (configura daemon, canais, gateway)
openclaw onboard --install-daemon

# Verificar status
openclaw gateway status

# Conectar canal Telegram
openclaw channels login

# Iniciar gateway em foreground (debug)
openclaw gateway --port 18789

# Abrir dashboard web
openclaw dashboard
# → http://127.0.0.1:18789/

# Enviar mensagem de teste ao Diretor
openclaw message send --target <CHAT_ID> --message "ClawDevs online ✅"
```

---

## Configuração do OpenClaw (openclaw.json)
  // GATEWAY — porta e binding
  // ─────────────────────────────────────────
  "gateway": {
    "port": 18789,
    "host": "0.0.0.0"
    // "0.0.0.0" expõe no cluster — use "127.0.0.1" para local-only
  },

  // ─────────────────────────────────────────
  // HOOKS — webhook do Orquestrador → OpenClaw
  // ─────────────────────────────────────────
  "hooks": {
    "enabled": true,

    // Token compartilhado — NUNCA hardcode, use env var
    "token": "${OPENCLAW_HOOK_SECRET}",

    // Path base dos endpoints
    "path": "/hooks",

    // Agentes que podem ser acionados explicitamente via agentId
    // Use ["*"] para permitir qualquer agente
    "allowedAgentIds": ["ceo", "po", "architect", "developer", "qa"],

    // Session key padrão para requests via webhook
    "defaultSessionKey": "hook:ingress",

    // SEGURANÇA: não permitir que caller defina session key
    "allowRequestSessionKey": false,
    "allowedSessionKeyPrefixes": ["hook:"],

    // SEGURANÇA: não permitir conteúdo externo sem sanitização
    "allowUnsafeExternalContent": false
  },

  // ─────────────────────────────────────────
  // CHANNELS — canais de mensagem autorizados
  // ─────────────────────────────────────────
  "channels": {
    "telegram": {
      "enabled": true,

      // CRÍTICO: apenas o chat_id do Diretor pode enviar comandos
      // Obter com @userinfobot no Telegram
      "allowFrom": ["${TELEGRAM_DIRECTOR_CHAT_ID}"],

      // false: qualquer mensagem é processada
      // true: só processa se mencionar @clawdevs
      "requireMention": false
    },
    "slack": {
      "enabled": false,          // Habilitar quando Slack for configurado
      "allowFrom": [],
      "requireMention": true,
      "mentionPatterns": ["@clawdevs"]
    },
    "whatsapp": {
      "enabled": false           // Reservado para fase 2
    },
    "discord": {
      "enabled": false           // Reservado para fase 2
    }
  },

  // ─────────────────────────────────────────
  // AGENTS — roteamento por hashtag
  // ─────────────────────────────────────────
  "agents": {
    // Agente padrão quando nenhuma hashtag é detectada
    "default": "ceo",

    "routing": {
      // Formato: "hashtag": { "agentId": "id" }
      "#ceo":    { "agentId": "ceo" },
      "#po":     { "agentId": "po" },
      "#arch":   { "agentId": "architect" },
      "#dev":    { "agentId": "developer" },
      "#qa":     { "agentId": "qa" },

      // Broadcast: entrega para todos os agentes
      "#time":   { "broadcast": true },

      // Modo especial: ativa self_evolution no CEO
      "#evolui": { "agentId": "ceo", "mode": "self_evolution" }
    },

    // Endpoint interno do Orquestrador (dentro do cluster)
    "orchestratorEndpoint": "http://orchestrator-service.clawdevs-gateway:8080"
  },

  // ─────────────────────────────────────────
  // INFERENCE — provedores de LLM
  // ─────────────────────────────────────────
  "inference": {
    "providers": {
      "ollama": {
        "enabled": true,

        // Endpoint interno do pod Ollama no cluster
        "baseUrl": "http://ollama-service.clawdevs-infra:11434",

        // Prioridade 1 = primeira tentativa
        "priority": 1,

        // Descoberta automática de modelos disponíveis
        "autoDiscover": true
      },
      "openrouter": {
        "enabled": true,
        "baseUrl": "https://openrouter.ai/api/v1",

        // NUNCA hardcode — use K8s Secret
        "apiKey": "${OPENROUTER_API_KEY}",

        // Prioridade 2 = fallback quando Ollama não é viável
        "priority": 2,

        // Kill switch: desabilita OpenRouter automaticamente ao atingir o teto
        "budgetLimitUSD": 50,

        // Headers de identificação para OpenRouter (boas práticas)
        "headers": {
          "HTTP-Referer": "https://github.com/clawdevs/clawdevs-ai",
          "X-Title": "ClawDevs AI"
        }
      }
    }
  },

  // ─────────────────────────────────────────
  // SECURITY — controles de segurança do gateway
  // ─────────────────────────────────────────
  "security": {
    // Rejeita qualquer sender não listado em allowFrom
    "allowlistOnly": true,

    // Log imutável de todas as interações
    "auditLog": true,

    // Proteção contra contextos excessivamente grandes
    "maxTokensPerRequest": 16384,

    // Rate limiting por sender (mensagens/minuto)
    "rateLimitPerMinute": 20,

    // Bloqueia query string tokens (somente Bearer header)
    "rejectQueryStringTokens": true
  }
}
```

---

## Variáveis de ambiente necessárias

```bash
# ─── Obrigatórias ───────────────────────────────────────────────
OPENCLAW_HOOK_SECRET=<gerar com: openssl rand -hex 32>
TELEGRAM_DIRECTOR_CHAT_ID=<obter com @userinfobot no Telegram>

# ─── OpenRouter (opcional — fallback cloud) ──────────────────────
OPENROUTER_API_KEY=sk-or-<sua-chave>

# ─── Diretórios do OpenClaw ──────────────────────────────────────
OPENCLAW_HOME=/data/openclaw
OPENCLAW_STATE_DIR=/data/openclaw/state
OPENCLAW_CONFIG_PATH=/data/openclaw/openclaw.json
```

### Como criar o Secret K8s

```bash
kubectl create secret generic clawdevs-openclaw-secrets \
  --namespace clawdevs-gateway \
  --from-literal=hook-secret=$(openssl rand -hex 32) \
  --from-literal=telegram-chat-id=<SEU_CHAT_ID> \
  --from-literal=openrouter-api-key=sk-or-...
```

---

## ConfigMap — openclaw.json no cluster

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: openclaw-config
  namespace: clawdevs-gateway
data:
  openclaw.json: |
    {
      "version": "1.0",
      "gateway": { "port": 18789, "host": "0.0.0.0" },
      "hooks": {
        "enabled": true,
        "token": "$(OPENCLAW_HOOK_SECRET)",
        "path": "/hooks",
        "allowedAgentIds": ["ceo", "po", "architect", "developer", "qa"],
        "defaultSessionKey": "hook:ingress",
        "allowRequestSessionKey": false,
        "allowedSessionKeyPrefixes": ["hook:"],
        "allowUnsafeExternalContent": false
      }
    }
```

---

## Deployment OpenClaw no cluster

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openclaw
  namespace: clawdevs-gateway
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openclaw
  template:
    metadata:
      labels:
        app: openclaw
    spec:
      containers:
      - name: openclaw
        image: openclaw/gateway:latest
        ports:
        - containerPort: 18789
        env:
        - name: OPENCLAW_CONFIG_PATH
          value: "/config/openclaw.json"
        - name: OPENCLAW_HOOK_SECRET
          valueFrom:
            secretKeyRef:
              name: clawdevs-openclaw-secrets
              key: hook-secret
        - name: TELEGRAM_DIRECTOR_CHAT_ID
          valueFrom:
            secretKeyRef:
              name: clawdevs-openclaw-secrets
              key: telegram-chat-id
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: clawdevs-openclaw-secrets
              key: openrouter-api-key
        volumeMounts:
        - name: openclaw-config
          mountPath: /config
        - name: openclaw-data
          mountPath: /data/openclaw
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
      volumes:
      - name: openclaw-config
        configMap:
          name: openclaw-config
      - name: openclaw-data
        persistentVolumeClaim:
          claimName: openclaw-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: openclaw-service
  namespace: clawdevs-gateway
spec:
  selector:
    app: openclaw
  ports:
  - port: 18789
    targetPort: 18789
  type: ClusterIP
```

---

## Checklist de setup do OpenClaw

```mermaid
graph TD
    C1["☐ Node.js 22+ instalado\nnode --version"]
    C2["☐ OpenClaw instalado\ncurl -fsSL https://openclaw.ai/install.sh | bash"]
    C3["☐ OPENCLAW_HOOK_SECRET gerado\nopenssl rand -hex 32"]
    C4["☐ Telegram bot criado\n@BotFather no Telegram"]
    C5["☐ TELEGRAM_DIRECTOR_CHAT_ID obtido\n@userinfobot no Telegram"]
    C6["☐ openclaw.json configurado\ncom secrets via env vars"]
    C7["☐ openclaw onboard --install-daemon\nexecutado com sucesso"]
    C8["☐ openclaw gateway status\nretorna 'running'"]
    C9["☐ Mensagem de teste enviada\nopenclaw message send ..."]
    C10["☐ Roteamento #dev testado\nresposta do Developer recebida"]

    C1 --> C2 --> C3 --> C4 --> C5 --> C6 --> C7 --> C8 --> C9 --> C10

    style C10 fill:#05966922,stroke:#059669
```

---

## Referências

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenRouter API](https://openrouter.ai)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
```
