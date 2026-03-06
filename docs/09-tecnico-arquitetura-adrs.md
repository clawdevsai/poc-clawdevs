# 09 — Arquitetura de Sistema e ADRs
> **Objetivo:** Definir a stack tecnológica definitiva (Kubernetes, OpenClaw, Ollama) e documentar as Decisões Arquiteturais (ADRs).
> **Público-alvo:** Arquitetos, Devs
> **Ação Esperada:** Arquitetos consultam ADRs antes de aprovar PRs; Devs usam como norte técnico proibindo tecnologias fora da stack.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Visão da stack por camada

```mermaid
graph TD
    subgraph L0["Camada 0 — Interface (Diretor)"]
        TG["📱 Telegram"]
        SL["💬 Slack"]
        WA["📲 WhatsApp"]
        DC["🎮 Discord"]
    end

    subgraph L1["Camada 1 — Gateway de Mensagens"]
        OC["OpenClaw\nlicença MIT · open source\nself-hosted"]
    end

    subgraph L2["Camada 2 — Orquestração de Containers"]
        K8S["Kubernetes (Minikube)\nApache 2.0 · local"]
    end

    subgraph L3["Camada 3 — Agentes de IA"]
        AGENTS["5 agentes especializados\nCEO · PO · Architect · Developer · QA\nClawDevs custom"]
    end

    subgraph L4["Camada 4 — Inferência"]
        OL["Ollama\nMIT · local · $0"]
        OR["OpenRouter\nfallback cloud · pay-per-use"]
    end



    L0 --> L1 --> L2 --> L3 --> L4

    style L0 fill:#4A90D922,stroke:#4A90D9
    style L1 fill:#7C3AED22,stroke:#7C3AED
    style L2 fill:#2563EB22,stroke:#2563EB
    style L3 fill:#05966922,stroke:#059669
    style L4 fill:#D9770622,stroke:#D97706
```

---

## Tabela completa da stack

| Camada | Tecnologia | Versão | Licença | Custo/mês |
|---|---|---|---|---|
| Gateway de mensagens | OpenClaw | latest | MIT | $0 |
| Orquestração | Kubernetes (Minikube) | 1.29+ | Apache 2.0 | $0 |
| Inferência local | Ollama | latest | MIT | $0 |
| Inferência cloud | OpenRouter | API | Proprietário | Pay-per-use |
| Modelos LLM | Qwen2.5-Coder 14B | latest | Apache 2.0 | $0 |
| Modelos LLM | Qwen2.5 14B | latest | Apache 2.0 | $0 |
| Modelos LLM | Llama 3.1 8B | latest | Meta Llama License | $0 |

| **Total núcleo** | | | | **$0/mês** |
| **OpenRouter (teto)** | | | | **≤ $50/mês** |

---

## Custo de operação estimado

```mermaid
pie title Custo mensal estimado (R$)
    "Energia elétrica" : 120
    "OpenRouter (fallback, se usado)" : 150
    "Infraestrutura self-hosted (R$0)" : 0
    "APIs cloud (R$0)" : 0
```

| Item | Custo estimado |
|---|---|
| Núcleo (software) | R$ 0 |
| Energia (máquina ligada 24/7) | R$ 80 – 150 |
| OpenRouter com uso moderado | R$ 0 – 200 |
| **Total realista** | **< R$ 350/mês** |

---

## Comparativo: ClawDevs vs. alternativas

```mermaid
graph LR
    subgraph CLAWDEVS["✅ ClawDevs AI"]
        CW1["Custo: ~$0 no núcleo"]
        CW2["Self-hosted: 100%"]
        CW3["Privacidade: dados locais"]
        CW4["Open source: núcleo MIT/Apache"]
        CW5["Replicável: qualquer hardware compatível"]
    end

    subgraph CLOUD["☁️ Alternativas cloud"]
        CL1["Custo: $500–5000/mês"]
        CL2["Dependência de vendor"]
        CL3["Dados saem da sua máquina"]
        CL4["Proprietário / lock-in"]
        CL5["Escalável mas caro"]
    end
```

---

## Modelos LLM — tamanho e requisitos

| Modelo | Tamanho | VRAM mínima | Contexto | Caso de uso |
|---|---|---|---|---|
| `qwen2.5-coder:14b` | ~9 GB | 10 GB | 64k | Developer, Architect |
| `qwen2.5:14b` | ~9 GB | 10 GB | 32k | CEO, PO |
| `qwen2.5-coder:7b` | ~4.5 GB | 5 GB | 32k | QA (lite) |
| `llama3.1:8b` | ~4.7 GB | 5 GB | 32k | Fallback geral |
## D1 — Protocolo A2A: padrão aberto (A2A Protocol) vs. custom

```mermaid
graph LR
    subgraph OPT_A["Opção A — A2A Protocol (Linux Foundation)"]
        A1["✅ Interoperabilidade com outros sistemas"]
        A2["✅ Comunidade crescente (Google, Microsoft, AWS)"]
        A3["✅ Sem lock-in de protocolo"]
        A4["❌ Overhead de implementação inicial"]
        A5["❌ Especificação ainda em evolução (2025-2026)"]
    end

    subgraph OPT_B["Opção B — Protocolo proprietário ClawDevs"]
        B1["✅ Controle total, customização máxima"]
        B2["✅ Mais rápido de implementar no início"]
        B3["❌ Nenhuma interoperabilidade externa"]
        B4["❌ Custo de manutenção a longo prazo"]
        B5["❌ Isolamento da comunidade A2A"]
    end

    DECISION["⚡ DECISÃO: Adotar A2A Protocol como base\ncom extensões ClawDevs onde necessário\n\nRationale: 2026 é o ano dos multi-agentes.\nEstar no padrão aberto = mais adoção,\nmenos manutenção, mais credibilidade."]

    OPT_A --> DECISION
    OPT_B --> DECISION

    style DECISION fill:#05966922,stroke:#059669,color:#059669
```

---

## D2 — Orquestração: framework vs. custom

```mermaid
quadrantChart
    title Frameworks de orquestração — Fit para ClawDevs
    x-axis Baixo controle --> Alto controle
    y-axis Baixa complexidade --> Alta complexidade
    quadrant-1 "Ideal para ClawDevs"
    quadrant-2 "Muito complexo / overhead"
    quadrant-3 "Simples mas limitado"
    quadrant-4 "Controle mas simples"

    LangGraph: [0.75, 0.80]
    CrewAI: [0.50, 0.55]
    AutoGen: [0.55, 0.70]
    Claude Agent SDK: [0.65, 0.60]
    Custom puro: [0.95, 0.90]
    Mastra TS: [0.60, 0.50]
```

**Decisão:** LangGraph como orquestrador core + extensões customizadas para o modelo de SOUL do ClawDevs.

**Rationale:** LangGraph é stateful, tem checkpoints, suporta grafos complexos de colaboração e é o mais adotado em produção em 2025-2026. Construir do zero gastaria 3x mais tempo sem vantagem real.

---

## D3 — Modelo de memória compartilhada

```mermaid
graph TD
    subgraph LAYERS["3 camadas de memória"]
        L1["🔥 Hot Memory — Redis\nContexto da tarefa atual\nTTL: duração da tarefa\nVelocidade: < 1ms"]
        L2["🌡️ Warm Memory — Qdrant\nConhecimento do projeto\nDecisões passadas (vetorial)\nVelocidade: < 50ms"]
        L3["❄️ Cold Memory — PostgreSQL\nHistórico completo\nAuditoria imutável\nVelocidade: < 200ms"]
    end

    AGENT["Agente recebe tarefa"]
    QUERY["Busca contexto relevante\nQdrant (semântico)\n+ Redis (tarefa atual)"]
    EXECUTE["Executa com contexto enriquecido"]
    PERSIST["Persiste resultado\nRedis (hot) + Qdrant (embed) + PG (log)"]

    AGENT --> QUERY
    L1 & L2 & L3 --> QUERY
    QUERY --> EXECUTE --> PERSIST

    style L1 fill:#DC262622,stroke:#DC2626
    style L2 fill:#D9770622,stroke:#D97706
    style L3 fill:#2563EB22,stroke:#2563EB
```

---

## D4 — Inferência: Ollama local puro vs. híbrido

**Decisão: Híbrido com Ollama como primário**

```mermaid
graph LR
    subgraph HYBRID["Modelo híbrido adotado"]
        direction TB
        T1["Tarefas rotineiras\nstatus · issues · reviews simples"]
        T2["Tarefas complexas\narquitetura · segurança · código crítico"]
        T3["Tarefas de emergência\ncluster em carga máxima"]

        T1 -->|"Ollama 7B"| CHEAP["$0 · rápido · local"]
        T2 -->|"Ollama 14B"| MED["$0 · mais lento · local"]
        T3 -->|"OpenRouter"| CLOUD["Pay-per-use · sempre disponível"]
    end
```

**Rationale:** Local puro limita capacidade. Cloud puro cria dependência e custo. Híbrido com Ollama primário é o único modelo que honra os 3 princípios: segurança, custo zero no core, performance.

---

## D5 — Licença: MIT vs. Dual Licensing

```mermaid
graph TD
    subgraph PHASES["Estratégia por fase"]
        P1["Fase 1 — Hoje\nMIT puro\nAdoção máxima\nComunidade cresce"]
        P2["Fase 2 — 6 meses\nEnterprise add-ons\nProprietário para:\n• Suporte enterprise\n• Compliance features\n• SLA garantido"]
        P3["Fase 3 — 12+ meses\nSaaS ClawDevs Cloud\n'Free tier self-hosted\nPaid tier cloud managed'"]
    end

    P1 -->|"quando tração validada"| P2 -->|"quando demanda enterprise"| P3

    style P1 fill:#05966922,stroke:#059669
    style P2 fill:#D9770622,stroke:#D97706
    style P3 fill:#7C3AED22,stroke:#7C3AED
```

---

## D6 — Público-alvo primário

```mermaid
graph TD
    subgraph SEGMENTS["Segmentos"]
        S1["👤 Dev solo / freelancer\nQuer time de agentes pessoal\nBudget: $0\nPaciência: alta para setup"]
        S2["🏢 Startup / scale-up\nQuer agilidade de time sem contratar\nBudget: $100-500/mês\nPaciência: baixa para setup"]
        S3["🏦 Enterprise\nQuer soberania de dados + compliance\nBudget: $1k+/mês\nPaciência: nenhuma — quer suporte"]
    end

    DECISION["⚡ DECISÃO v1.0:\nFoco em Dev solo + Startups\n\nMotivar com 'clone e rode'\nsuporte enterprise em v2.0\nApós tração validada"]

    S1 --> DECISION
    S2 --> DECISION
    S3 -.->|"v2.0"| DECISION

    style DECISION fill:#05966922,stroke:#059669,color:#059669
```

---

## D7 — Modelo de monetização

```mermaid
graph LR
    subgraph MODEL["Modelo freemium + serviços"]
        FREE["🆓 Core open source\nSempre gratuito\nSelf-hosted · MIT"]
        CLOUD["☁️ ClawDevs Cloud\nManaged hosting\nSetup em 5 min\nR$ 199/mês"]
        ENT["🏢 Enterprise\nSLA + suporte dedicado\nCustom SOULs\nR$ 2.000+/mês"]
        SERV["🛠️ Serviços\nSetup assistido\nSOULs customizados\nR$ 500–2.000 por projeto"]
    end

    FREE -->|"converte"| CLOUD & ENT & SERV
```

---

## D8 — Build vs. integrar (o que construir vs. usar pronto)

| Componente | Decisão | Justificativa |
|---|---|---|
| Orquestrador | **Integrar LangGraph** | 3x mais rápido; battle-tested |
| Protocolo A2A | **Integrar A2A Protocol** | Padrão de mercado emergente |
| Gateway de mensagens | **Integrar OpenClaw** | É o produto da ClawDevs |
| SOUL engine | **Construir** | Diferencial competitivo core |
| Memória vetorial | **Integrar Qdrant** | Open source melhor da categoria |
| Self-evolution | **Construir** | Não existe pronto — é IP do ClawDevs |
| Dashboard | **Construir** | UX específica para o produto |
| CI/CD | **Integrar Gitea + Forgejo** | Evitar reinventar SCM |

---

## D9 — Velocidade vs. Perfeição

**Decisão: MVP em 30 dias, perfeição em 90 dias**

```mermaid
timeline
    title Velocidade vs. Perfeição — por semana
    section Semanas 1-4 (MVP)
        Funciona : 2 agentes · 1 projeto · 1 PR
        Não quebra : Testes básicos · restart automático
        Chega ao Diretor : Telegram funcionando
    section Semanas 5-8 (Time completo)
        Colabora : 5 agentes · A2A · contexto compartilhado
        É consistente : SOULs respeitados · políticas ativas
        É rápido : SLA dentro do target
    section Semanas 9-12 (Perfeição)
        É seguro : Auditoria · Zero Trust validado
        É replicável : Qualquer um consegue subir
        É vivo : Self-evolution gerando PRs reais
```

---

## D10 — Open source vs. SaaS: quando bifurcar

**Decisão: Nunca fechar o core. Monetizar a camada gerenciada.**

O modelo de sucesso é HashiCorp (Terraform), Elastic, Grafana: core sempre open source, serviço gerenciado pago. Fechar o core destruiria a comunidade — e a comunidade é o diferencial competitivo do ClawDevs contra sistemas proprietários.
