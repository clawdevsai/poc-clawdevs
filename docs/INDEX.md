# ClawDevsAI Documentation Index

Guia principal da documentacao tecnica e operacional do repositorio.

## Comece por aqui

1. [Setup local](./guides/setup.md)
2. [Visao geral de arquitetura](./architecture/overview.md)
3. [Troubleshooting](./operations/troubleshooting.md)
4. [Glossario](./reference/glossary.md)

## Navegacao por objetivo

- **Entender o sistema:** [architecture/overview.md](./architecture/overview.md)
- **Subir o ambiente local:** [guides/setup.md](./guides/setup.md)
- **Diagnosticar problemas:** [operations/troubleshooting.md](./operations/troubleshooting.md)
- **Ver papeis dos agentes:** [agentes/README.md](./agentes/README.md)
- **Ver visao funcional:** [aplicacao-e-exemplos.md](./aplicacao-e-exemplos.md)
- **Ver analise detalhada:** [analise-projeto.md](./analise-projeto.md)
- **Ver arquitetura tecnica aprofundada:** [arquitetura-tecnica.md](./arquitetura-tecnica.md)

## Estrutura atual da pasta

```text
docs/
├── INDEX.md
├── README.md
├── architecture/
│   └── overview.md
├── guides/
│   └── setup.md
├── operations/
│   └── troubleshooting.md
├── reference/
│   ├── diagrams-guide.md
│   └── glossary.md
├── agentes/
│   ├── README.md
│   └── *.md
├── aplicacao-e-exemplos.md
├── analise-projeto.md
├── arquitetura-tecnica.md
├── engenharia-de-prompts.md
└── workspace-arquivos-agente.md
```

Arquivos em `docs/plans/` sao historico de trabalho e nao fazem parte da documentacao tecnica as-built.

## Comandos realmente usados neste projeto

```bash
make help
make preflight
make up-all
make up-all-with-cache
make up-gpu
make status
make logs
make openclaw-logs
make panel-url
make openclaw-shell
make migrate
make down
make reset
make destroy
```

## Nota de consistencia

Esta documentacao esta alinhada ao fluxo atual do `Makefile`, que opera a stack via Docker (`docker` + scripts em `scripts/docker/`).
