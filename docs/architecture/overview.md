# Architecture Overview

Visao de arquitetura do que esta implementado hoje no repositorio.

## Conceito arquitetural

A arquitetura segue o modelo "control plane + execution runtime":

- **Control plane:** painel web e API para operacao
- **Execution runtime:** OpenClaw + agentes + ferramentas
- **Inference plane:** Ollama local para modelos e embeddings
- **Data plane:** PostgreSQL, Redis e volumes Docker

## Componentes principais (as-built)

1. **Control Panel**
   - Frontend Next.js (`clawdevs-panel-frontend`)
   - Backend FastAPI (`clawdevs-panel-backend`)
   - Worker assinc (`clawdevs-panel-worker`)
2. **OpenClaw Gateway**
   - Container `clawdevs-openclaw`
   - Exposto em `localhost:18789`
3. **LLM local**
   - Container `clawdevs-ollama`
   - API em `localhost:11434`
4. **Servicos de apoio**
   - `clawdevs-postgres`, `clawdevs-redis`
   - `clawdevs-searxng`, `clawdevs-searxng-proxy`

## Diagrama logico

```text
Usuario -> Control Panel (3000/8000)
            -> OpenClaw Gateway (18789)
                -> Agentes (workspace + ferramentas)
                    -> Ollama (11434) / APIs externas
                    -> GitHub / web-search / shell / filesystem
```

## Fluxo tecnico de requisicao

1. Usuario envia acao pelo frontend (`3000`) ou API (`8000`).
2. Backend do painel processa e integra com OpenClaw via rede interna Docker.
3. OpenClaw seleciona/agenda agente e executa loop de ferramentas.
4. Quando necessario, o agente chama Ollama interno (`http://ollama:11434`).
5. Resultado volta para API/painel e logs permanecem disponiveis nos containers.

## Agentes

A configuracao de agentes fica em `docker/base/openclaw-config/agents/` e a referencia funcional em `docs/agentes/`.

## Persistencia

- Volumes Docker da stack guardam dados de OpenClaw, banco e modelos Ollama.
- Sessao e estado operacional sao preservados entre reinicios normais de container.

Volumes utilizados:

- `openclaw-data`
- `ollama-data`
- `postgres-data`
- `panel-token`

## Operacao

Use os alvos do `Makefile` como interface oficial:

```bash
make up-all-with-cache
make status
make logs
make down
```

## Tecnica de operacao

- O start completo usa `make up-all` ou `make up-all-with-cache`.
- Cada servico tem healthchecks no bootstrap e timeout de subida.
- O backend aplica migracao Alembic automaticamente no entrypoint.
- O OpenClaw recebe variaveis de cron por agente no container runtime.
