# ClawDevs AI — Time de Desenvolvimento com Custo Zero 🚀

> **Qualquer empresa pode ter um time completo de desenvolvimento de IA, com custo praticamente zero, rodando 100% local com alta performance.**

O Diretor interage com os agentes via **Slack** e **Telegram**. Tudo roda dentro do **Kubernetes** (Minikube) com **Ollama** para inferência local — sem dependência de APIs pagas.

---

## 🤖 Time de Agentes

| Agente | Função |
|--------|--------|
| 👔 **CEO** | Orquestrador — rotas decisões e coordena o time |
| 📋 **PO** | Product Owner — quebra requisitos em issues |
| 🏛️ **Arquiteto** | Revisão técnica e decisões de arquitetura |
| 💻 **Developer** | Implementação de código |
| 🎨 **UX** | Design de interfaces |
| 🔬 **QA** | Testes e validação de qualidade |
| ⚙️ **DevOps** | Infraestrutura e CI/CD |
| 🛡️ **CyberSec** | Segurança e análise de vulnerabilidades |
| 🗄️ **DBA** | Banco de dados e migrations |

---

## 🏗️ Arquitetura

```
Diretor (Slack / Telegram)
          ↓
    OpenClaw Gateway
          ↓
  Redis Streams (orquestração)
          ↓
┌─────────────────────────────────────────┐
│  Kubernetes (Minikube)                  │
│  CEO → PO → Architect → Developer      │
│       ↓           ↓          ↓         │
│     DevOps        QA        DBA         │
│       ↓           ↓        UX           │
│              CyberSec                   │
└─────────────────────────────────────────┘
          ↓
    Ollama (LLM local — DeepSeek-R1 / Qwen2.5)
          ↓
    /workspace (código gerado e revisado)
```

**Mission Control** (painel web) permite ao Diretor monitorar agentes, tarefas e custos de tokens.

---

## 💻 Início Rápido

### Pré-requisitos
- Linux com GPU (recomendado) ou CPU
- Docker instalado
- 16 GB RAM mínimo (32 GB recomendado para DeepSeek-R1 14B)

### 1. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Preencha: TELEGRAM_BOT_TOKEN, OPENCLAW_SLACK_APP_TOKEN, GITHUB_TOKEN, GITHUB_REPO
```

### 2. Preparar a máquina
```bash
make prepare
# Instala: Docker, Minikube, Kubectl. Pode pedir sudo.
```

### 3. Montar workspace compartilhado
```bash
make shared
# Cria ~/clawdevs-shared, sincronizado com /workspace dentro do K8s
```

### 4. Subir o sistema completo
```bash
make up
# Liga: Redis, Ollama, OpenClaw, todos os agentes
# Ao final imprime a URL do Mission Control
```

---

## 🛠️ Comandos do Dia a Dia

| Comando | O que faz |
|---------|-----------|
| `make status` | Status dos pods e serviços |
| `make status-pods` | Logs em tempo real |
| `make reset-memory` | Limpa memória dos agentes (novo projeto) |
| `make verify` | Testa GPU/CPU |
| `make dashboard` | Abre Kubernetes Dashboard no browser |
| `make down` | Desliga tudo |

---

## 🎛️ Mission Control (Painel do Diretor)

Acesse via URL impressa pelo `make up` (ex.: `http://<IP_MINIKUBE>:30000`).

O painel oferece:
- **Dashboard**: saúde dos 9 agentes em tempo real
- **Central de Missões**: Kanban (Backlog → Em Andamento → Em Revisão → QA → Concluído)
- **FinOps / Tokens**: custo estimado por agente e teto diário
- **Intervenção**: reatribuir, pausar, cancelar ou elevar tarefas sem escrever código

---

## 📁 Estrutura do Projeto

```
poc-clawdevs/
├── app/                    # Python: agentes, orquestração, segurança
│   ├── agents/             # Implementação de cada agente
│   ├── core/               # Orquestrador, Kanban API, strikes
│   ├── features/           # FinOps, RAG, GPU lock, digest, etc.
│   ├── safety/             # CyberSec: prompt injection, quarentena
│   ├── shared/             # Utilitários compartilhados (redis_client, ollama, etc.)
│   └── contingency/        # Heartbeat e contingência para cluster sem cabeça
├── mission-control/        # Dashboard Next.js (substitui kanban-ui)
├── k8s/                    # Manifests Kubernetes (deployments, configmaps, secrets)
│   ├── development-team/   # Pods do time de desenvolvimento
│   ├── management-team/    # CEO, PO
│   ├── orchestrator/       # Orquestrador
│   ├── security/           # CyberSec, token rotation
│   └── shared/             # Redis, Ollama, Namespace
├── scripts/                # Automação organizada por contexto
│   ├── cluster/            # up, down, prepare, redis-streams-init
│   ├── configmaps/         # Scripts para cada ConfigMap de agente
│   ├── openclaw/           # Scripts do OpenClaw gateway
│   ├── ops/                # Operações: CISO scan, GPU, debug
│   ├── transcription/      # m4a → md para notas de voz
│   └── utils/              # Utilitários do Diretor
├── docs/                   # Documentação técnica detalhada
├── tests/                  # Testes automatizados (pytest)
├── avatar/                 # Imagens dos agentes
├── requirements.txt        # Dependências Python
└── Makefile                # Entry point de todos os comandos
```

---

## 📖 Documentação Técnica

| Arquivo | Conteúdo |
|---------|----------|
| `docs/01-core/` | Visão, proposta, agentes, arquitetura |
| `docs/02-infra/` | K8s, Ollama, Redis, contingência |
| `docs/03-agents/` | Comportamento, memória, protocolos A2A |

---

## ⚙️ Stack

| Componente | Tecnologia | Licença |
|------------|------------|---------|
| Gateway | OpenClaw | MIT |
| LLM local | Ollama + DeepSeek-R1 14B / Qwen2.5 14B | MIT / Apache |
| Orquestração | Redis Streams | BSD |
| Infraestrutura | Kubernetes (Minikube) | Apache |
| Dashboard | Next.js + Tailwind | MIT |
| Backend Kanban | Flask + SQLite | MIT |
| Segurança | OWASP, prompt injection detector | MIT |

---

## 🔒 Segurança

- **Zero dados na nuvem**: todo o processamento é local
- **Quarentena de URLs**: sandbox para URLs externas antes de executar código
- **Rotação de tokens**: troca automática de credenciais OpenClaw
- **SAST**: análise de entropia e pacotes maliciosos antes de instalar dependências
- **LGPD/GDPR**: nenhum dado sai da máquina

---

## 📜 Licença

MIT — veja [LICENSE](LICENSE)

---

> *"O Diretor nunca precisa tocar em uma linha de código."*
