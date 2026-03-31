# O que a aplicacao faz

ClawDevsAI integra OpenClaw, Ollama e um Control Panel para executar agentes especializados em tarefas de engenharia de software.

## Capacidades principais

- Orquestracao de agentes por papel (backend, frontend, QA, DevOps, seguranca, etc.)
- Execucao assistida por LLM local via Ollama
- Integracao com GitHub para fluxo de trabalho tecnico
- Observabilidade via logs de servicos e painel web

## Exemplo de uso 1 - subir o ambiente

```bash
cp .env.example .env
make preflight
make up-all-with-cache
make panel-url
```

## Exemplo de uso 2 - diagnosticar problema

```bash
make status
make openclaw-logs
make backend-logs
make frontend-logs
```

## Exemplo de uso 3 - manutencao operacional

```bash
make migrate
make openclaw-shell
make down
```

## Servicos da stack

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
