<!--
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

# clawdevs-ai (Docker Compose)

Fluxo para subir a stack completa (`ollama` + `openclaw` + `control-panel`) localmente com Docker Compose, com suporte a GPU via Docker e NVIDIA Container Runtime.

## Novidades (2026-03-28)

- **Migração de Kubernetes para Docker Compose** - Simplificação do deployment
- **Control Panel integrado** ao fluxo principal via docker-compose.yaml
- **Comandos simplificados**: `make up`, `make down`, `make logs`
- **Suporte a GPU nativo** via Docker Compose + NVIDIA Container Runtime
- **Ambiente local otimizado**: sem necessidade de Minikube/Kubernetes

## Fluxo de spec

Antes de implementar uma mudança, o fluxo recomendado neste repositório é:

0. `CONSTITUTION` com princípios e guardrails
1. `BRIEF` com contexto e objetivo executivo
2. `SPEC` com comportamento observável, contratos e critérios de aceite
3. `CLARIFY` quando houver ambiguidade
4. `PLAN` técnico e arquitetura
5. `TASK` técnica e issues
6. `FEATURE` e `USER STORY` quando fizer sentido para o fluxo de produto
7. implementação e validação

Templates e artefatos:

- `container/base/openclaw-config/shared/BRIEF_TEMPLATE.md`
- `container/base/openclaw-config/shared/CLARIFY_TEMPLATE.md`
- `container/base/openclaw-config/shared/PLAN_TEMPLATE.md`
- `container/base/openclaw-config/shared/TASK_TEMPLATE.md`
- `container/base/openclaw-config/shared/VALIDATE_TEMPLATE.md`
- `container/base/openclaw-config/shared/SDD_OPERATIONAL_PROMPTS.md`
- `container/base/openclaw-config/shared/SPEC_TEMPLATE.md`
- `container/base/openclaw-config/shared/CONSTITUTION.md`
- `container/base/openclaw-config/shared/SDD_CHECKLIST.md`
- `container/base/openclaw-config/shared/SDD_FULL_CYCLE_EXAMPLE.md`
- `container/base/openclaw-config/shared/SPECKIT_ADAPTATION.md`
- `container/base/openclaw-config/shared/initiatives/internal-sdd-operationalization/`
- `/data/openclaw/backlog/specs/`
- `/data/openclaw/backlog/briefs/`
- `/data/openclaw/backlog/user_story/`
- `/data/openclaw/backlog/tasks/`

O mesmo contrato vale para:
- a plataforma interna da ClawDevs AI
- os projetos e entregas feitos por ela

Em ambos os casos, a SPEC é a fonte de verdade do comportamento pretendido.
Quando houver ambiguidade, o passo correto é `clarify` antes de `plan` e `tasks`.
Use o `SDD_CHECKLIST.md` como gate de prontidão antes de mover uma entrega para a próxima etapa.
Use os templates para manter o fluxo repetível entre plataforma interna e projetos.
Use `SDD_OPERATIONAL_PROMPTS.md` para iniciar conversas e execuções com os agentes.
Use `SDD_FULL_CYCLE_EXAMPLE.md` como molde de referência para novas iniciativas.
Use `shared/initiatives/internal-sdd-operationalization/` como iniciativa real pronta para execução.

## Modo Vibe Coding

ClawDevs AI deve operar em ciclos curtos e demonstráveis:

1. definir um resultado visível
2. escrever a spec mínima
3. entregar um slice vertical funcional
4. validar com demo
5. endurecer com testes, logs e observabilidade

Regra prática:
- se a mudança não cabe em uma demo curta, ela está grande demais
- se o fluxo ficar invisível por muito tempo, ele precisa ser fatiado
- se a solução não for reversível, ela precisa de mais cuidado antes de subir

## Requisitos

- Windows 11, macOS, ou Linux
- Docker Desktop (com GPU support para NVIDIA)
- NVIDIA Container Runtime (se usar GPU)
- Driver NVIDIA atualizado
- `.env` configurado com variáveis de ambiente (veja `.env.example`)

## Makefile - Comandos Disponíveis

O Makefile está organizado em **3 seções principais**. Para ver todos os comandos:

```bash
make help
```

### SEÇÃO 1: PREPARAÇÃO DE AMBIENTE

Comandos para setup inicial e configuração:

```bash
make up                       # Inicia stack completa (Docker Compose)
make down                     # Para e remove containers
make build                    # Build de todas as imagens localmente
make env-check                # Valida arquivo .env
```

### SEÇÃO 2: DEPLOY E OPERAÇÃO

**Stack Completa:**
```bash
make up                       # Inicia stack (ollama + openclaw + panel)
make down                     # Para stack
make restart                  # Reinicia stack
```

**Ollama:**
```bash
make ollama-logs              # Logs do Ollama
make ollama-list              # Lista modelos disponíveis
```

**OpenClaw:**
```bash
make openclaw-logs            # Logs do OpenClaw
make openclaw-shell           # Executa shell no container OpenClaw
```

**Control Panel:**
```bash
make panel-logs               # Logs do panel (backend + frontend)
make panel-url                # Mostra URLs de acesso
make panel-db-migrate         # Executa migrations Alembic
```

**Build de Imagens:**
```bash
make build                    # Build local de todas as imagens
make push                     # Push imagens para Docker Hub
make release                  # Build + Push
```

### SEÇÃO 3: LOGS E MONITORAMENTO

```bash
make logs                     # Todos os logs em tempo real
make logs-follow              # Segue logs (como docker-compose logs -f)
make ps                       # Status dos containers
make top                      # Recursos (CPU, memória) dos containers
```

## Ordem de execução — subindo toda a aplicação

### 1. Pré-requisitos

Copie e preencha o arquivo de variáveis de ambiente:

```bash
cp .env.example .env
# edite .env com os valores reais (GIT_TOKEN, PANEL_ADMIN_PASSWORD, etc)
```

### 2. Validar configuração

```bash
make env-check           # valida que as variáveis obrigatórias estão em .env
```

### 3. Subir a stack completa (OpenClaw + Ollama + Control Panel)

```bash
make up
```

Esse único target:
1. Valida `.env`
2. Build das imagens (se necessário)
3. Inicia todos os serviços (postgres, redis, ollama, openclaw, panel-backend, panel-frontend)
4. Aguarda health checks passarem

### 4. Acessar o Control Panel

O Control Panel já foi iniciado. Para acessá-lo:

```bash
make panel-url          # exibe as URLs de acesso (frontend, backend, API docs)
```

Para executar migrations do banco de dados na **primeira** subida:

```bash
make panel-db-migrate   # executa as migrations Alembic no backend
```

### 5. Acessar o OpenClaw Gateway

OpenClaw está rodando em `http://localhost:18789` (port-forward automático).

## Acesso aos Serviços

| Serviço | URL Local | Porta |
|---------|-----------|-------|
| **Control Panel** (Frontend) | http://localhost:3000 | 3000 |
| **Control Panel** (Backend API) | http://localhost:8000 | 8000 |
| **Control Panel** (API Docs) | http://localhost:8000/docs | 8000 |
| **OpenClaw** Gateway | http://localhost:18789 | 18789 |
| **Ollama** | http://localhost:11434 | 11434 |
| **PostgreSQL** | localhost:5432 | 5432 |
| **Redis** | localhost:6379 | 6379 |

## Logs e Monitoramento

Para acompanhar os logs dos componentes:

```bash
make logs                     # Todos os logs em tempo real
make panel-logs               # Apenas Panel
make openclaw-logs            # Apenas OpenClaw
make ollama-logs              # Apenas Ollama
```

Para verificar status:

```bash
make ps                       # Status dos containers
make top                      # CPU, memória por container
```

## Reset e Limpeza

Para reiniciar ou limpar o ambiente:

```bash
make restart                  # Para e reinicia stack (preserva volumes)
make down                     # Para e remove containers
make clean                    # Remove containers, volumes, redes
make prune                    # Docker system prune (limpeza profunda)
```

## Modo GPU (NVIDIA)

Para usar GPU com Docker:

### 1. Validar GPU

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base nvidia-smi
```

Se rodar sem erros, GPU está configurada.

### 2. Usar overlay de GPU (se usar Compose separado)

```bash
docker-compose -f docker-compose.yaml -f docker-compose.gpu.yaml up -d
```

O arquivo `docker-compose.yaml` já vem com suporte condicional a GPU via `deploy.resources.reservations.devices`.

## Estrutura de Configuração

```text
.env                              # Variáveis de ambiente (git-ignored)
.env.example                      # Template de .env
docker-compose.yaml               # Configuração principal
Makefile                          # Targets de conveniência
container/
  base/
    bootstrap-scripts/            # Scripts de inicialização
    openclaw-config/              # Config dos agentes
      agents/
      shared/
      initiatives/
```

## Conclusão para o desenvolvedor

Resumo do caminho **mínimo** para subir a stack completa:

### Ordem dos comandos (básico)

1. Copiar e preencher variáveis: `cp .env.example .env` e editar com valores reais.
2. (Recomendado) Validar: `make env-check`.
3. Subir tudo de uma vez: `make up`
   Isso já inclui postgres, redis, ollama, openclaw e control panel.
4. Na **primeira** subida com banco novo: `make panel-db-migrate`.
5. Conferir saúde: `make ps` e `make logs`.

### Acesso externo

Todos os serviços estão disponíveis em `localhost`:

- **Control Panel Frontend**: http://localhost:3000
- **Control Panel Backend**: http://localhost:8000 (API: `/docs`)
- **OpenClaw Gateway**: http://localhost:18789
- **Ollama**: http://localhost:11434

## GitHub (gh CLI)

- A organização padrão para ações GitHub dos agentes vem de `GIT_ORG` (definido em `.env` e injetado no container).
- Opcionalmente, `GIT_DEFAULT_REPOSITORY` define o primeiro repositório ativo na inicialização.
- O token vem de `GIT_TOKEN` (também definido em `.env` e injetado no container).
- O repositório ativo por sessão fica em `/data/openclaw/contexts/active_repository.env` (`ACTIVE_GIT_REPOSITORY`).
- Para comandos `gh` fora de um checkout local, usar `--repo "$ACTIVE_GIT_REPOSITORY"` (ou `"$GIT_REPOSITORY"` para compatibilidade).
- Utilitários de contexto multi-repo no container:
  - `claw-repo-discover [filtro]` para descobrir repositórios da organização
  - `claw-repo-ensure <repo> [--create]` para validar existência e criar quando autorizado
  - `claw-repo-switch <repo> [branch]` para trocar contexto de todos os agentes/workspaces
- Documentação oficial: https://cli.github.com/manual/gh

## Estrutura Docker Compose

```text
docker-compose.yaml
  networks:
    clawdevs/                     # Rede interna dos containers
  volumes:
    openclaw-data/                # Dados persistentes do OpenClaw
    ollama-data/                  # Modelos do Ollama
    postgres-data/                # Banco de dados PostgreSQL
    panel-token/                  # Token temporário Panel
  services:
    postgres/                     # Banco de dados (PostgreSQL)
    redis/                        # Cache (Redis)
    ollama/                       # LLM Backend
    searxng/                      # Busca web
    panel-backend/                # Control Panel API
    panel-frontend/               # Control Panel UI
    openclaw/                     # Gateway de agentes
```

O comando padrão de deploy continua sendo:

```bash
docker-compose up -d
```

---

https://clawhub.ai/pskoett/self-improving-agent
