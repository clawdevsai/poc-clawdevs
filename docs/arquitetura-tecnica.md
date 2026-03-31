# Arquitetura Tecnica - ClawDevsAI (as-built)

## Topologia de execucao

A stack roda localmente via Docker Desktop e scripts em `scripts/docker`, acionados por alvos do `Makefile`.

## Containers da stack

- `clawdevs-openclaw`
- `clawdevs-ollama`
- `clawdevs-postgres`
- `clawdevs-redis`
- `clawdevs-searxng`
- `clawdevs-searxng-proxy`
- `clawdevs-panel-backend`
- `clawdevs-panel-worker`
- `clawdevs-panel-frontend`
- `clawdevs-token-init`

## Rede e aliases internos

Todos os servicos sobem em uma rede Docker da stack (`STACK_NETWORK`, padrao `clawdevs`) com aliases internos:

- `postgres`
- `redis`
- `ollama`
- `searxng`
- `searxng-proxy`
- `panel-backend`
- `panel-worker`
- `panel-frontend`
- `openclaw`

## Fluxo tecnico

1. Usuario interage pelo painel (`3000`) ou API (`8000`)
2. Backend aciona gateway OpenClaw (`18789`)
3. Agentes executam tarefas com ferramentas permitidas
4. Inferencia local ocorre no Ollama (`11434`) quando aplicavel
5. Estado e dados de apoio sao persistidos nos volumes da stack

## Inicializacao tecnica dos servicos

- Banco e cache sobem primeiro (PostgreSQL e Redis) com healthcheck.
- Ollama sobe com volume `ollama-data` e politica de auto-pull de modelos.
- Backend do painel sobe com migracao Alembic no startup.
- `token-init` executa uma vez e grava dados no volume `panel-token`.
- Frontend e worker sobem apos backend saudavel.
- OpenClaw sobe por script dedicado (`run-openclaw.sh`) com `openclaw-data` e bind de configuracao bootstrap.

## Configuracao

- Segredos e parametros operacionais ficam no `.env` da raiz
- `make preflight` valida chaves obrigatorias e arquivos criticos
- Configuracao dos agentes fica em `docker/base/openclaw-config/`

Variaveis centrais no runtime OpenClaw:

- `OPENCLAW_GATEWAY_TOKEN`
- `PROVEDOR_LLM` / `OPENROUTER_*` (quando aplicavel)
- `OPENCLAW_LOG_LEVEL`, `DEBUG_LOG_ENABLED`
- `*_CRON_ENABLED`, `*_CRON_EXPR`, `*_CRON_TZ` por agente

## Operacao e observabilidade

```bash
make status
make logs
make openclaw-logs
make ollama-logs
make backend-logs
make frontend-logs
```

Healthchecks utilizados:

- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Panel backend: `GET /healthz`
- OpenClaw: `GET /healthz`
- SearXNG e proxy: endpoint `/healthz`

## Acesso tecnico rapido

```bash
make openclaw-shell
make panel-url
make migrate
```

## Escopo desta documentacao

Este documento cobre apenas arquitetura e tecnica da implementacao atual no repositorio.
