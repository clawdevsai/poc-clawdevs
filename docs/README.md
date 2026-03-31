# Documentacao Operacional (clawdevs-ai)

Documento tecnico do estado atual implementado da plataforma.

## Referencias principais

- [Indice geral](./INDEX.md)
- [Setup local](./guides/setup.md)
- [Arquitetura](./architecture/overview.md)
- [Troubleshooting](./operations/troubleshooting.md)

## Conceito da plataforma

ClawDevsAI e uma plataforma de orquestracao de agentes em runtime local, com:

- OpenClaw como gateway/orquestrador
- Ollama como provedor de inferencia local
- Control Panel (frontend, backend e worker) para operacao
- Servicos de apoio (PostgreSQL, Redis, SearXNG e proxy)

Toda a operacao e feita por Docker e scripts do repositorio (`scripts/docker/`), acionados por alvos do `Makefile`.

## Stack em execucao (as-built)

O projeto roda com containers Docker, orquestrados por alvos do `Makefile`:

- `clawdevs-openclaw` (gateway + agentes)
- `clawdevs-ollama` (LLM local)
- `clawdevs-searxng` e `clawdevs-searxng-proxy`
- `clawdevs-panel-backend`, `clawdevs-panel-worker`, `clawdevs-panel-frontend`
- `clawdevs-postgres`, `clawdevs-redis`, `clawdevs-token-init`

## Fluxo tecnico de inicializacao

```bash
cp .env.example .env
make preflight
make up-all-with-cache
make panel-url
```

Ordem real de bootstrap (`up-all.sh` + `run-openclaw.sh`):

1. `clawdevs-postgres` (healthcheck com `pg_isready`)
2. `clawdevs-redis` (healthcheck com `redis-cli ping`)
3. `clawdevs-ollama` (porta `11434`, volume `ollama-data`)
4. `clawdevs-searxng`
5. `clawdevs-panel-backend` (executa `alembic upgrade head` no start)
6. `clawdevs-token-init` (one-shot para token do painel em volume `panel-token`)
7. `clawdevs-searxng-proxy` (porta `18080`)
8. `clawdevs-panel-worker`
9. `clawdevs-panel-frontend` (porta `3000`)
10. `clawdevs-openclaw` (porta `18789`, volume `openclaw-data`)

## Portas e endpoints locais

- `3000`: frontend do painel
- `8000`: backend do painel e docs
- `11434`: API do Ollama
- `18080`: proxy SearXNG
- `18789`: gateway OpenClaw

## Comandos mais usados

```bash
make status
make logs
make openclaw-logs
make ollama-logs
make frontend-logs
make backend-logs
make openclaw-shell
make migrate
make down
```

## Volumes e persistencia

- `openclaw-data`: estado OpenClaw, workspaces e dados compartilhados
- `ollama-data`: modelos e cache do Ollama
- `postgres-data`: dados do PostgreSQL
- `panel-token`: token do painel gerado no bootstrap

## Configuracao tecnica relevante

- `clawdevs-openclaw` recebe `--env-file .env` e injeta variaveis de cron por agente.
- O gateway aponta para Ollama interno em `http://ollama:11434`.
- O backend do painel aponta para gateway interno em `http://openclaw:18789`.
- O frontend aponta para backend interno `http://panel-backend:8000`.

## Variaveis obrigatorias

As validacoes de `make preflight` exigem no minimo:

- `OPENCLAW_GATEWAY_TOKEN`
- `TELEGRAM_BOT_TOKEN_CEO`
- `GIT_TOKEN`
- `GIT_ORG`
- `PANEL_DB_PASSWORD`
- `PANEL_REDIS_PASSWORD`
- `PANEL_SECRET_KEY`
- `PANEL_ADMIN_USERNAME`
- `PANEL_ADMIN_PASSWORD`

## Estrutura de documentacao

- `docs/INDEX.md` - mapa principal
- `docs/guides/setup.md` - setup local
- `docs/architecture/overview.md` - arquitetura
- `docs/operations/troubleshooting.md` - diagnostico
- `docs/agentes/` - papeis e responsabilidades por agente
