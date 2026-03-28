# Análise Completa do Projeto ClawDevsAI

**Autor:** Diego Silva Morais
**Data:** 27 de março de 2026
**Tipo:** Análise Técnica e Arquitetural

---

## 📋 Sumário Executivo

ClawDevsAI é uma **plataforma de agentes de IA baseada em OpenClaw** que orquestra múltiplos agentes especializados para gerenciar o ciclo completo de desenvolvimento de software. A arquitetura é construída sobre Docker Compose (Docker), OpenClaw, Ollama, e um Control Panel customizado, com suporte a GPU nativa via NVIDIA.

**Objetivo Principal:** Automatizar e orquestrar tarefas de desenvolvimento, QA, DevOps e design através de agentes de IA coordenados que seguem um fluxo estruturado (CONSTITUTION → BRIEF → SPEC → PLAN → TASK → IMPLEMENTAÇÃO).

---

## 🏗️ Arquitetura de Alto Nível

### Camadas Principais

```
┌────────────────────────────────────────────────────────────┐
│                     CONTROL PANEL                           │
│              (Frontend Next.js + Backend FastAPI)           │
├────────────────────────────────────────────────────────────┤
│                     OPENCLAW GATEWAY                        │
│          (Orquestração de Agentes + Roteamento)            │
├────────────────────────────────────────────────────────────┤
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │ Ollama       │ OpenClaw     │ Searxng              │    │
│  │ (LLM Local)  │ (Agentes)    │ (Busca Distribuída)  │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
├────────────────────────────────────────────────────────────┤
│         Docker Compose (Docker) + Docker + GPU (NVIDIA)       │
└────────────────────────────────────────────────────────────┘
```

### Stack Tecnológico

| Componente | Tecnologia | Propósito |
|-----------|-----------|----------|
| **Container** | Docker + Docker | Orquestração local com suporte a GPU |
| **LLM Runtime** | Ollama | Modelos locais (nemotron, qwen3-next, etc) |
| **Agent Framework** | OpenClaw | Gateway e orquestração de agentes |
| **Backend** | FastAPI + SQLAlchemy | API REST e gerenciamento de estado |
| **Frontend** | Next.js + React | Interface web interativa |
| **Busca** | Searxng | Agregador de busca distribuída |
| **Database** | PostgreSQL | Persistência de dados |
| **GPU** | NVIDIA Device Plugin | Aceleração de LLMs |

---

## 🤖 Estrutura de Agentes

O projeto define **8 agentes especializados**, cada um com seu próprio workspace isolado e schedule de execução:

### Agentes Implementados

| Agente | Responsabilidade | Schedule |
|--------|------------------|----------|
| **dev_backend** | Backend development, APIs, databases | A cada 2 horas (00 min) |
| **dev_frontend** | Frontend development, UI/UX, React | A cada 2 horas (15 min) |
| **dev_mobile** | Mobile development, apps cross-platform | A cada 2 horas (30 min) |
| **qa** | Testes, validação, QA automation | A cada 2 horas (45 min) |
| **devops_sre** | Infrastructure, deployments, monitoring | A cada 1 hora |
| **security_engineer** | Segurança, audits, compliance | Diariamente às 2h |
| **ux_designer** | Design systems, UX research | Às segundas às 9h |
| **dba_data_engineer** | Database optimization, data pipelines | Às segundas às 9h30 |

Cada agente:
- Possui workspace isolado com SOUL.md, AGENTS.md, IDENTITY.md
- Acessa dados via GitHub (GIT_TOKEN + GIT_ORG)
- Notifica CEO via Telegram (TELEGRAM_BOT_TOKEN_CEO)
- Recebe tarefas do Control Panel

### Especificações de Agente

**Workspace Padrão:** `~/.openclaw/workspace/<agentId>/`

**Arquivos Essenciais:**
- `AGENTS.md` — Instruções operacionais do agente
- `SOUL.md` — Persona, tom, valores
- `IDENTITY.md` — Nome, características, autorização
- `USER.md` — Contexto do usuário final
- `MEMORY.md` — Memória persistente de longo prazo
- `memory/YYYY-MM-DD.md` — Logs diários

---

## 📊 Fluxo de Desenvolvimento (SDD - Structured Development Development)

O projeto implementa um fluxo de especificação rigoroso chamado **Fluxo SDD**:

```
1. CONSTITUTION
   ↓ (Princípios e guardrails)
2. BRIEF
   ↓ (Contexto executivo e objetivo)
3. SPEC
   ↓ (Comportamento observável, contratos)
4. CLARIFY (se ambiguidade)
   ↓ (Questões abertos / edge cases)
5. PLAN
   ↓ (Arquitetura técnica)
6. TASK
   ↓ (Issues técnicas)
7. FEATURE / USER STORY
   ↓ (Fluxo de produto)
8. IMPLEMENTAÇÃO + VALIDAÇÃO
```

**Diretórios de Artefatos:**
- Templates: `container/base/openclaw-config/shared/*.md`
- Specs: `/data/openclaw/backlog/specs/`
- Briefs: `/data/openclaw/backlog/briefs/`
- User Stories: `/data/openclaw/backlog/user_story/`
- Tasks: `/data/openclaw/backlog/tasks/`

**Filosofia "Vibe Coding":**
- Ciclos curtos e demonstráveis
- Resultados visíveis antes de endurecer com testes
- Mudanças reversíveis antes de subir
- Se não cabe em uma demo curta, está grande demais

---

## 🚀 Deploy e Operação

### Pré-requisitos

- Windows 11
- Docker Desktop com suporte a GPU
- NVIDIA Driver atualizado
- `docker`, `docker-compose`, `make` no PATH

### Startup Rápido

```bash
# 1. Preparar segredos
cp container/.env.example container/.env
# edite container/.env com valores reais

# 2. Validar
make preflight          # Valida segredos obrigatórios
make manifests-validate # Valida kustomize

# 3. Subir tudo
make clawdevs-up       # Setup completo (não destrutivo)
```

O comando `make clawdevs-up` executa em sequência:
1. `preflight` — Valida segredos obrigatórios
2. `docker-up` — Inicia Docker com GPU
3. `docker-context` — Ajusta docker compose config
4. `docker-addons` — Habilita dashboard, metrics, storage, NVIDIA plugin
5. `storage-enable-expansion` — Expansão de volumes
6. `ollama-volume-apply` — PVC para dados do Ollama
7. `stack-apply` — Deploy de ollama + openclaw + control-panel

### Modo de Build de Imagens

**Remoto (padrão):**
```bash
PUSH_IMAGE=remote  # Faz pull de clawdevsai/* no Docker Hub
```

**Local:**
```bash
PUSH_IMAGE=local   # Builda imagens localmente no Docker
```

Para publicar imagens:
```bash
docker login -u clawdevsAI
make images-release STACK_IMAGE_TAG=latest
```

### Configuração de GPU

**Validação:**
```bash
make gpu-doctor              # Diagnóstico completo
make docker-container-context      # Muda para docker-desktop
make gpu-plugin-apply        # Aplica NVIDIA device plugin
make gpu-node-check          # Verifica GPU disponível
```

**Deploy com GPU:**
```bash
make openclaw-apply-gpu      # Deploy OpenClaw com suporte a GPU
```

---

## 🎛️ Control Panel

### Arquitetura

```
control-panel/
├── backend/          (FastAPI + SQLAlchemy)
│   ├── app/
│   ├── models/       (ORM SQLAlchemy)
│   ├── schemas/      (Pydantic)
│   ├── routers/      (Endpoints)
│   ├── migrations/   (Alembic)
│   └── requirements.txt
├── frontend/         (Next.js + React)
│   ├── app/          (App Router)
│   ├── components/
│   ├── hooks/
│   ├── styles/
│   └── package.json
└── scripts/          (Utilitários)
```

### Funcionalidades

- **Dashboard de Agentes** — Status, logs, execução
- **Gerenciamento de Tarefas** — Criar, acompanhar, atribuir
- **Visualização de Pipelines** — Fluxos SDD em tempo real
- **Logs Centralizados** — Backend + Frontend
- **API REST** — Controle programático

### Startup

```bash
make panel-apply       # Deploy do painel
make panel-url         # Exibe URLs de acesso
make panel-forward     # Port-forward para localhost:3000
make panel-db-migrate  # Executa migrations Alembic
make panel-logs-backend   # Logs do backend
make panel-logs-frontend  # Logs do frontend
```

---

## 🔧 Configuração (container/.env)

### Variáveis Essenciais

```bash
# Autenticação OpenClaw
OPENCLAW_GATEWAY_TOKEN=<token-bearer>

# Telegram (Notificações do CEO)
TELEGRAM_BOT_TOKEN_CEO=<id>:<hash>
TELEGRAM_CHAT_ID_CEO=<chat-id>

# GitHub (Integração com repositórios)
GIT_TOKEN=<personal-access-token>
GIT_ORG=<organização>
GIT_DEFAULT_REPOSITORY=<org/repo>

# Identificação
DIRECTORS_NAME=<nome-do-ceo>

# Ollama
OLLAMA_API_KEY=<opcional>
PROVEDOR_LLM=ollama  # ollama | openrouter

# OpenRouter (opcional)
OPENROUTER_API_KEY=<api-key>
OPENROUTER_MODEL=stepfun/step-3.5-flash:free

# Logs e Debug
OPENCLAW_LOG_LEVEL=info
DEBUG_LOG_ENABLED=false

# Dados
DEV_BACKEND_PROJECT_ROOT=/data/openclaw/projects
LANGUAGE=pt-BR

# Build
PUSH_IMAGE=remote  # local | remote

# Schedules (valores em cron expression)
DEV_BACKEND_CRON_EXPR="0 */2 * * *"
DEV_FRONTEND_CRON_EXPR="15 */2 * * *"
# ... outros agentes
```

---

## 📁 Estrutura do Projeto

```
clawdevs-ai/
├── README.md                 (Documentação principal)
├── Makefile                  (Automação de deploy)
├── LICENSE                   (MIT)
├── SECURITY.md               (Política de segurança)
│
├── docs/
│   ├── README.md             (Índice de documentação)
│   ├── agentes/              (Specs de cada agente)
│   ├── aplicacao-e-exemplos.md
│   ├── engenharia-de-prompts.md
│   ├── workspace-arquivos-agente.md
│   └── plans/                (Planos de execução)
│
├── container/                      (Docker Compose + Kustomize)
│   ├── .env.example          (Template de configuração)
│   ├── .env                  (Segredos — NÃO commitar)
│   ├── kustomization.yaml    (Kustomize root)
│   ├── base/                 (Manifestos base)
│   │   ├── openclaw-container.yaml
│   │   ├── ollama-container.yaml
│   │   ├── searxng-container.yaml
│   │   ├── openclaw-config/  (ConfigMaps e Secrets)
│   │   └── bootstrap-scripts/
│   └── overlays/             (Variações por ambiente)
│
├── control-panel/
│   ├── backend/              (FastAPI)
│   ├── frontend/             (Next.js)
│   └── scripts/              (Utilitários)
│
├── docker/                   (Dockerfiles customizados)
│
└── assets/                   (Imagens, logos)
```

---

## 🔌 Integrações Externas

### GitHub

- **Uso:** Leitura/escrita de repositórios
- **Autenticação:** Personal Access Token (GIT_TOKEN)
- **Permissões:** `repo`, `read:org`, `write:issues`
- **Escopo:** Organização configurada (GIT_ORG)

### Telegram

- **Uso:** Notificações e escalações para CEO
- **Autenticação:** Bot Token (TELEGRAM_BOT_TOKEN_CEO)
- **Formato:** Mensagens estruturadas com status

### Ollama (Local LLM)

- **Modelos Disponíveis:**
  - `nemotron-3-super:cloud` — Modelo principal
  - `qwen3-next:80b-cloud` — Modelo alternativo
  - `nomic-embed-text` — Embeddings para memória

- **Configuração:**
  - API Key: `OLLAMA_API_KEY` (opcional)
  - Auto-pull no boot: `OLLAMA_AUTO_PULL_MODELS`

### OpenRouter (LLM Remoto — Opcional)

- **Uso:** Alternativa a Ollama local
- **Configuração:** `PROVEDOR_LLM=openrouter`
- **API Key:** `OPENROUTER_API_KEY`
- **Modelo Padrão:** `stepfun/step-3.5-flash:free`

### Searxng (Busca Distribuída)

- **Uso:** Agregação de resultados de múltiplas engines
- **Integração:** Via proxy dedicado

---

## 🧠 Sistema de Memória

OpenClaw implementa um sistema de memória em **Markdown puro** no workspace:

### Estrutura

```
~/.openclaw/workspace/<agentId>/
├── MEMORY.md              (Memória curada, persistente)
├── memory/
│   ├── 2026-03-27.md      (Log diário: hoje)
│   ├── 2026-03-26.md      (Log diário: ontem)
│   └── ...
```

### Funcionalidades

- **Busca Semântica** — Embeddings (Gemini, OpenAI, local)
- **Busca Híbrida** — Vetores + BM25 keyword matching
- **MMR (Maximal Marginal Relevance)** — Reduz duplicatas
- **Decaimento Temporal** — Boosta memórias recentes
- **Cache de Embeddings** — Evita re-embedding

### Providers de Embedding

- `local` — node-llama-cpp
- `openai` — OpenAI Embeddings
- `gemini` — Google Embeddings
- `voyage` — Voyage API
- `mistral` — Mistral Embeddings
- `ollama` — Instância Ollama

---

## 🔐 Segurança

### Práticas Implementadas

1. **Isolamento de Agentes**
   - Workspace isolado por agente
   - Direitos de acesso por sandbox
   - Sessions segregadas por `dmScope`

2. **Credenciais**
   - Armazenadas em `~/.openclaw/credentials/`
   - Nunca comitadas no git
   - OAuth com PKCE flow

3. **Validação**
   - JSON Schema para frames WebSocket
   - Assinatura de challenges de nonce
   - Approval explícito de conexões não-loopback

4. **Auditoria**
   - Logs estruturados em OpenClaw
   - Tracked changes em documentos
   - Timestamps de todas as operações

### Segredos Obrigatórios (container/.env)

```
✓ OPENCLAW_GATEWAY_TOKEN
✓ TELEGRAM_BOT_TOKEN_CEO
✓ TELEGRAM_CHAT_ID_CEO
✓ GIT_TOKEN
✓ GIT_ORG
✓ GIT_DEFAULT_REPOSITORY
✓ DIRECTORS_NAME
```

Validados via `make preflight`.

---

## 📈 Métricas e Monitoramento

### Comandos Disponíveis

```bash
# Status do cluster
make docker-status        # Status do Docker
make docker-logs          # Logs do Docker
make gpu-doctor             # Diagnóstico GPU

# Status dos serviços
make stack-status           # Status de todos os containers
make panel-status           # Status do painel
make ollama-list            # Modelos disponíveis

# Logs
make ollama-logs            # Logs do Ollama
make openclaw-logs          # Logs do OpenClaw
make panel-logs-backend     # Logs do backend
make panel-logs-frontend    # Logs do frontend
```

### Dashboard OpenClaw

```bash
make openclaw-dashboard     # Abre dashboard em browser
```

---

## 🎯 Fluxo de Desenvolvimento (Vibe Coding)

O projeto segue uma metodologia pragmática para desenvolvimento rápido:

### Ciclo Típico

1. **Definir Resultado Visível**
   - O que o usuário vê/experimenta?

2. **Escrever Spec Mínima**
   - Comportamento observável
   - Contratos e critérios de aceite

3. **Entregar Slice Vertical Funcional**
   - Backend + Frontend + Testes

4. **Validar com Demo**
   - Demonstração prática
   - Feedback imediato

5. **Endurecer**
   - Testes, logs, observabilidade

### Regras Práticas

- ❌ Se a mudança não cabe em uma demo curta, está grande demais
- ❌ Se o fluxo fica invisível por muito tempo, precisa ser fatiado
- ❌ Se a solução não é reversível, precisa de mais cuidado antes de subir

---

## 🚦 Checklist de Prontidão (SDD)

Antes de mover uma entrega para a próxima etapa, use `make sdd-checklist`:

```
□ CONSTITUTION aprovada pelos stakeholders
□ BRIEF executivo alinhado com objetivos
□ SPEC completa com comportamento observável
□ CLARIFY resolveu todas as ambiguidades
□ PLAN técnico revisado
□ TASK com critérios de aceite testáveis
□ FEATURE/USER STORY aligned com roadmap
□ Implementação + testes + docs concluídos
□ Demo executada com sucesso
□ Pronto para produção
```

---

## 🔄 Manutenção e Operação

### Tarefas Rotineiras

```bash
# Deploy
make clawdevs-up             # Setup completo
make stack-apply             # Re-deploy apenas o stack

# Atualizações
make images-release          # Build + push todas as imagens
make openclaw-image-release  # Build + push apenas OpenClaw

# Reset (destrutivo)
make reset-all               # Recria stack do zero
make destroy-all             # Limpeza completa
make clawdevs-down           # Para e remove tudo
make docker-down           # Para Docker
```

### Escalação de Problemas

1. **Verificar logs**
   ```bash
   make <service>-logs
   ```

2. **Diagnosticar GPU**
   ```bash
   make gpu-doctor
   ```

3. **Validar configuração**
   ```bash
   make manifests-validate
   ```

4. **Resetar (último recurso)**
   ```bash
   make reset-all
   ```

---

## 📚 Recursos Importantes

### Documentação

- **Fluxo SDD:** `container/base/openclaw-config/shared/SDD_FULL_CYCLE_EXAMPLE.md`
- **Templates:** `container/base/openclaw-config/shared/*.md`
- **Iniciativas:** `container/base/openclaw-config/shared/initiatives/`
- **OpenClaw Docs:** `docs/README.md`

### Arquivos de Configuração

- Agentes: `docs/agentes/`
- Engenharia de Prompts: `docs/engenharia-de-prompts.md`
- Workspace: `docs/workspace-arquivos-agente.md`
- Aplicações: `docs/aplicacao-e-exemplos.md`

### Exemplos

- Specs Prontas: `/data/openclaw/backlog/specs/`
- Plans Prontos: `docs/plans/`

---

## 🎓 Aprendizado e Próximos Passos

### Para Começar

1. Leia `README.md` (este documento expandido)
2. Execute `make help` para ver todos os comandos
3. Estude `docs/README.md` para entender agentes
4. Suba o cluster com `make clawdevs-up`
5. Acesse Control Panel: `make panel-url`

### Customizações Frequentes

- **Adicionar novo agente:** Duplicate `docs/agentes/<agente>.md`, crie workspace
- **Alterar schedule:** Edite cron expression em `container/.env` ou container manifest
- **Integrar novo LLM:** Configure em `OPENROUTER_API_KEY` ou adicione modelo Ollama
- **Estender Control Panel:** Adicione endpoints em `control-panel/backend/routers/`

### Profundidade Técnica

- **OpenClaw internals:** Leia `container/base/openclaw-config/shared/SDD_OPERATIONAL_PROMPTS.md`
- **Kustomize:** Estude `container/base/` e `container/overlays/`
- **FastAPI:** Explore `control-panel/backend/app/`
- **Next.js:** Explore `control-panel/frontend/app/`

---

## 📞 Contato e Suporte

- **Autor:** Diego Silva Morais (`lukewaresoftwarehouse@gmail.com`)
- **Repositório:** GitHub (GIT_ORG)
- **Issues:** `GIT_DEFAULT_REPOSITORY`
- **Escalações:** Via Telegram (TELEGRAM_BOT_TOKEN_CEO)

---

## 📄 Licença

MIT License — Veja LICENSE para detalhes.

---

**Última Atualização:** 27 de março de 2026
