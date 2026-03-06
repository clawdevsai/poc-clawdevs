# 01 — Visão do Projeto
> **Objetivo:** Estabelecer a visão macro da arquitetura, os princípios inegociáveis do produto e os modos de operação do sistema.
> **Público-alvo:** Produto (PO, Stakeholders)
> **Ação Esperada:** Entender o propósito do ecossistema e validar se o direcionamento técnico apoia as metas de negócio.

**v2.0 | 06 de março de 2026**

---

## Índice resumido

Para navegação completa acesse o [README principal](./README.md).

---

## Arquitetura Macro

```mermaid
graph TD
    DIRETOR["👤 Diretor (Humano)\nTelegram · Slack · Voz · Web"]

    subgraph GW["🌐 clawdevs-gateway"]
        OC["OpenClaw Gateway\n:18789\nRoteador · Sessões · Webhooks"]
    end

    subgraph CTRL["⚙️ Controle"]
        ORCH["Orquestrador Core\npod: orchestrator"]
        DASH["Dashboard + Monitor\npod: dashboard"]
    end

    subgraph AGENTS["🤖 clawdevs-agents"]
        CEO["🎯 CEO\nClaw"]
        PO["📋 PO\nPriya"]
        ARCH["🏗️ Architect\nAxel"]
        DEV["💻 Developer\nDev"]
        QA["🧪 QA\nQuinn"]
    end

    subgraph INFRA["🗄️ clawdevs-infra"]
        OLLAMA["Ollama\n:11434\nInferência local"]
        OR["OpenRouter\nFallback cloud"]
    end

    DIRETOR -->|"msg canal"| OC
    OC -->|"POST /hooks/agent"| ORCH
    OC --- DASH
    ORCH --> CEO & PO & ARCH & DEV & QA
    CEO & PO & ARCH & DEV & QA -->|"inferência"| OLLAMA
    OLLAMA -->|"fallback"| OR
    ORCH -->|"resposta"| OC
    OC -->|"entrega"| DIRETOR

    classDef human fill:#4A90D9,stroke:#2563EB,color:#fff
    classDef gateway fill:#7C3AED,stroke:#5B21B6,color:#fff
    classDef agent fill:#059669,stroke:#047857,color:#fff
    classDef infra fill:#D97706,stroke:#B45309,color:#fff

    class DIRETOR human
    class OC gateway
    class CEO,PO,ARCH,DEV,QA agent
    class OLLAMA,OR infra
```

---

## Fluxo de uma tarefa (ponta a ponta)

```mermaid
sequenceDiagram
    actor D as 👤 Diretor
    participant OC as OpenClaw Gateway
    participant OR as Orquestrador
    participant AG as Agente (ex: Developer)
    participant OL as Ollama

    D->>OC: "#dev implemente o endpoint /login"
    OC->>OR: POST /hooks/agent {agentId: "developer", message: ...}
    OR->>AG: dispatch(task, soul, context)
    AG->>OL: POST /api/chat {model: "qwen2.5-coder:14b", ...}
    OL-->>AG: resposta gerada
    AG->>OR: commit + abre PR #42 (interno)
    OR-->>OC: resultado consolidado
    OC-->>D: "✅ PR #42 aberto"
```

---

## Princípios de design

```mermaid
graph LR
    P1["🔒 1. Segurança\n(não negociável)"]
    P2["💰 2. Custo zero\nno núcleo"]
    P3["⚡ 3. Performance\nsustentável"]

    P1 -->|"precede"| P2
    P2 -->|"precede"| P3

    style P1 fill:#DC2626,stroke:#B91C1C,color:#fff
    style P2 fill:#D97706,stroke:#B45309,color:#fff
    style P3 fill:#059669,stroke:#047857,color:#fff
```

**Toda decisão técnica e de produto** deve ser avaliada nesta ordem de prioridade: segurança → custo → performance. Nunca invertida, independente de pressão de prazo.

---

## Time de agentes (v1.0)

```mermaid
graph TD
    DIR["👤 Diretor"]

    CEO["🎯 CEO — Claw\nEstratégia · Status · Bloqueios"]
    PO["📋 PO — Priya\nBacklog · User Stories · DoD"]
    ARCH["🏗️ Architect — Axel\nADRs · PR Review · Segurança"]
    DEV["💻 Developer — Dev\nCódigo · Testes · PRs"]
    QA["🧪 QA — Quinn\nValidação · Bugs · Cobertura"]

    DIR -->|"#ceo #po #arch #dev #qa #time"| CEO
    CEO -->|"consolida e reporta"| DIR
    CEO --- PO
    CEO --- ARCH
    PO -->|"issues + critérios"| DEV
    PO -->|"aceite"| QA
    ARCH -->|"revisão arquitetural"| DEV
    ARCH -->|"aprova/bloqueia merge"| QA
    DEV -->|"abre PR"| QA
    QA -->|"aprova PR"| ARCH

    classDef director fill:#4A90D9,stroke:#2563EB,color:#fff
    classDef exec fill:#7C3AED,stroke:#5B21B6,color:#fff
    classDef ops fill:#059669,stroke:#047857,color:#fff

    class DIR director
    class CEO,PO,ARCH exec
    class DEV,QA ops
```

---

## Modos de operação

```mermaid
stateDiagram-v2
    [*] --> Standby : cluster iniciado

    Standby --> Executing : Diretor envia tarefa via canal
    Executing --> Standby : tarefa concluída / resposta entregue

    Standby --> SelfEvolution : Diretor envia #evolui
    SelfEvolution --> AwaitingApproval : agentes propõem PR de melhoria
    AwaitingApproval --> Standby : Diretor aprova ou rejeita
    AwaitingApproval --> SelfEvolution : Diretor pede revisão

    Executing --> CircuitBreaker : GPU temp > 85°C OU CPU > 90%
    CircuitBreaker --> Standby : recursos normalizados

    note right of SelfEvolution: Toda mudança vira PR\nAprovação humana obrigatória
    note right of CircuitBreaker: Kill switch automático\nAlertas no Telegram
```

---

*Próximo Documento:* [02 — Backlog e MVP →](./02-produto-backlog-mvp.md)
