# 12 — Inferência LLM (Ollama + OpenRouter)
> **Objetivo:** Estabelecer a estratégia híbrida de inferência (Local First, Cloud Fallback).
> **Público-alvo:** Devs, Arquitetos
> **Ação Esperada:** Arquitetos calibram os thresholds de custo/fallback; Devs integram as APIs seguindo os perfis de cada agente.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Estratégia de roteamento de inferência

```mermaid
flowchart TD
    START["Agente recebe tarefa"]

    START --> CK_HW{"Hardware OK?\nGPU < 85°C\nCPU < 90%"}
    CK_HW -->|"❌ Limites críticos"| KILL["🛑 Kill Switch\nTarefa enfileirada\nAlerta ao Diretor"]
    CK_HW -->|"✅ OK"| CK_BUDGET{"Budget OpenRouter\nnão esgotado?"}

    CK_BUDGET -->|"❌ Esgotado"| LOCAL_ONLY["⚠️ Apenas Ollama\nlocal disponível"]
    CK_BUDGET -->|"✅ OK"| CK_LOCAL{"Ollama viável?\n• modelo disponível\n• VRAM suficiente\n• contexto < 128k tokens"}

    CK_LOCAL -->|"✅ Sim"| OLLAMA["🦙 Ollama Local\nhttp://ollama-service:11434\nCusto: $0"]
    CK_LOCAL -->|"❌ Não"| OPENROUTER["🌐 OpenRouter\nhttps://openrouter.ai\nCusto: pay-per-use"]
    LOCAL_ONLY --> OLLAMA

    OLLAMA --> RESP["Resposta ao agente"]
    OPENROUTER --> RESP

    style KILL fill:#DC262622,stroke:#DC2626
    style OLLAMA fill:#05966922,stroke:#059669
    style OPENROUTER fill:#2563EB22,stroke:#2563EB
    style LOCAL_ONLY fill:#D9770622,stroke:#D97706
```

---

## Modelos por agente

```mermaid
graph LR
    subgraph AGENTS["Agentes"]
        CEO_A["🎯 CEO\nClaw"]
        PO_A["📋 PO\nPriya"]
        ARCH_A["🏗️ Architect\nAxel"]
        DEV_A["💻 Developer\nDev"]
        QA_A["🧪 QA\nQuinn"]
    end

    subgraph OLLAMA_M["Ollama — Modelos locais"]
        M1["qwen2.5:14b\n~9GB · 32k ctx\nRaciocínio geral"]
        M2["qwen2.5-coder:14b\n~9GB · 64k ctx\nCódigo + arquitetura"]
        M3["qwen2.5-coder:7b\n~4.5GB · 32k ctx\nTestes + análise leve"]
        M4["llama3.1:8b\n~4.7GB · 32k ctx\nFallback geral"]
    end

    subgraph OR_M["OpenRouter — Fallback cloud"]
        OR1["claude-sonnet-4-5\nRaciocínio complexo"]
        OR2["deepseek/deepseek-r1\nCódigo avançado"]
        OR3["llama-3.1-70b\nFallback geral"]
    end

    CEO_A -->|"primário"| M1
    CEO_A -->|"fallback"| OR1
    PO_A -->|"primário"| M1
    PO_A -->|"fallback"| OR3
    ARCH_A -->|"primário"| M2
    ARCH_A -->|"fallback"| OR1
    DEV_A -->|"primário"| M2
    DEV_A -->|"fallback"| OR2
    QA_A -->|"primário"| M3
    QA_A -->|"fallback"| OR3
    M1 & M2 & M3 & M4 -->|"fallback interno"| M4

    style M1 fill:#05966922,stroke:#059669
    style M2 fill:#05966922,stroke:#059669
    style M3 fill:#05966922,stroke:#059669
    style M4 fill:#D9770622,stroke:#D97706
    style OR1 fill:#2563EB22,stroke:#2563EB
    style OR2 fill:#2563EB22,stroke:#2563EB
    style OR3 fill:#2563EB22,stroke:#2563EB
```

---

## Tabela de modelos e parâmetros por agente

| Agente | Modelo Ollama | Fallback OpenRouter | Temp | Tokens | Thinking |
|---|---|---|---|---|---|
| CEO | `qwen2.5:14b` | `anthropic/claude-sonnet-4-5` | 0.3 | 4k | medium |
| PO | `qwen2.5:14b` | `meta-llama/llama-3.1-70b` | 0.4 | 4k | medium |
| Architect | `qwen2.5-coder:14b` | `anthropic/claude-sonnet-4-5` | 0.2 | 8k | high |
| Developer | `qwen2.5-coder:14b` | `deepseek/deepseek-r1` | 0.1 | 16k | high |
| QA | `qwen2.5-coder:7b` | `meta-llama/llama-3.1-70b` | 0.2 | 8k | medium |

---

## Kill switches — Proteção de hardware

```mermaid
stateDiagram-v2
    [*] --> Normal : cluster saudável

    Normal --> GpuWarning : GPU temp > 75°C
    GpuWarning --> Normal : temp normaliza
    GpuWarning --> GpuKill : GPU temp > 85°C

    Normal --> CpuWarning : CPU usage > 80%
    CpuWarning --> Normal : carga normaliza
    CpuWarning --> CpuKill : CPU usage > 90%

    Normal --> BudgetWarning : gasto OpenRouter > 80% do teto
    BudgetWarning --> Normal : ---
    BudgetWarning --> BudgetKill : gasto = 100% do teto

    GpuKill --> [*] : tasks enfileiradas\nalerta Telegram
    CpuKill --> [*] : tasks enfileiradas\nalerta Telegram
    BudgetKill --> LocalOnly : apenas Ollama disponível
    LocalOnly --> Normal : mês seguinte / teto ajustado

    note right of GpuKill: Nenhuma nova inferência\naté resfriamento
    note right of BudgetKill: OpenRouter desabilitado\nOllama continua
```

---

## Setup dos modelos Ollama

```bash
# Conectar ao pod Ollama
kubectl exec -it deploy/ollama -n clawdevs-infra -- bash

# Pull dos modelos necessários (~27GB total)
ollama pull qwen2.5-coder:14b      # ~9.0 GB — Developer + Architect (primário)
ollama pull qwen2.5:14b            # ~8.9 GB — CEO + PO (primário)
ollama pull qwen2.5-coder:7b       # ~4.5 GB — QA (primário)
ollama pull llama3.1:8b            # ~4.7 GB — fallback geral

# Verificar modelos instalados
ollama list

# Teste rápido de inferência
ollama run qwen2.5-coder:14b "Escreva um hello world em Python"

# Endpoints internos ao cluster
# Chat:     POST http://ollama-service.clawdevs-infra:11434/api/chat
# Generate: POST http://ollama-service.clawdevs-infra:11434/api/generate
# Models:   GET  http://ollama-service.clawdevs-infra:11434/api/tags
```

---

## Configuração OpenRouter (Secret K8s)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: clawdevs-secrets
  namespace: clawdevs-agents
type: Opaque
stringData:
  openrouter-key: "sk-or-..."
  openrouter-base-url: "https://openrouter.ai/api/v1"
  openrouter-budget-limit-usd: "50"   # Kill switch: $50/mês máximo
```

### Modelos OpenRouter por caso de uso

| Caso de uso | Modelo | Custo estimado |
|---|---|---|
| Raciocínio complexo (Architect) | `anthropic/claude-sonnet-4-5` | ~$3/M tokens |
| Código de alta complexidade | `deepseek/deepseek-r1` | ~$0.55/M tokens |
| Análise de segurança crítica | `openai/gpt-4o` | ~$2.50/M tokens |
| Tarefas gerais (fallback barato) | `meta-llama/llama-3.1-70b-instruct` | ~$0.12/M tokens |

---

## Consumo estimado de VRAM por perfil

```mermaid
graph LR
    subgraph LITE["Perfil LITE (sem GPU)\nRAM: ~20 GB"]
        L1["qwen2.5-coder:7b\n4.5 GB"]
        L2["qwen2.5:14b quantizado\n5.5 GB"]
        L3["llama3.1:8b\n4.7 GB"]
    end

    subgraph FULL["Perfil FULL (com GPU 12GB VRAM)\nVRAM: ~10 GB"]
        F1["qwen2.5-coder:14b\n9.0 GB VRAM"]
    end

    subgraph OVERFLOW["Overflow para RAM do sistema\nquando VRAM insuficiente"]
        O1["Modelos grandes\nrodam em CPU+RAM\n(mais lento, mas funciona)"]
    end

    LITE --> OVERFLOW
    FULL --> OVERFLOW

    style LITE fill:#D9770622,stroke:#D97706
    style FULL fill:#05966922,stroke:#059669
    style OVERFLOW fill:#6B728022,stroke:#6B7280
```


