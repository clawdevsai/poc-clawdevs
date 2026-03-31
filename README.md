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

# ClawDevs AI

Stack local com `NemoClaw runtime + Ollama + Control Panel`, operada via `Makefile` e Docker.

## Inicio rapido (comandos corretos do Makefile)

> Importante: `make up` **nao** sobe a stack. O target correto para stack completa e `make up-all`.

```bash
cp .env.example .env
# preencha o .env (ex.: GIT_TOKEN, PANEL_ADMIN_PASSWORD, etc)
make env-check
make up-all
make panel-url
```

### NemoClaw (modo recomendado: host-side)

O NemoClaw é **host-side** (instala OpenShell e cria um sandbox). Para usar o gateway do NemoClaw a partir dos containers do painel:

1) No `.env`, configure:
- `NEMOCLAW_EXTERNAL=true`
- `NEMOCLAW_GATEWAY_URL=http://host.docker.internal:18789`

2) No host (fora do Docker), instale e faça onboard:

```bash
curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash
nemoclaw onboard
openshell term
```

Na primeira subida com banco novo:

```bash
make panel-db-migrate
```

## Servicos da stack

O fluxo `make up-all` sobe os containers da stack `clawdevs-*`, incluindo:

- PostgreSQL
- Redis
- Ollama
- NemoClaw Runtime
- SearXNG + SearXNG Proxy
- Panel Backend
- Panel Worker
- Panel Frontend
- Token Init

## Acesso local

| Servico | URL |
|---------|-----|
| Control Panel (Frontend) | http://localhost:3000 |
| Control Panel (Backend API) | http://localhost:8000 |
| Control Panel (Docs) | http://localhost:8000/docs |
| NemoClaw Runtime | http://localhost:18789 |
| Ollama API | http://localhost:11434 |
| SearXNG Proxy | http://localhost:18080 |
| PostgreSQL | http://localhost:5432 |
| Redis | http://localhost:6379 |

## Comandos mais importantes

### Operacao da stack

```bash
make help                  # resumo dos comandos suportados
make env-check             # valida .env e preflight
make up-all                # build local + sobe stack completa
make up-all-with-cache     # build com cache + sobe stack completa
make up-gpu                # stack completa com --gpus all no Ollama
make down                  # remove containers da stack
make restart               # down + up-all
make ps                    # alias de status dos containers
make status                # status (nome, estado, portas)
```

### Logs e suporte

```bash
make logs                  # logs agregados dos containers em execucao
make logs-follow           # alias de logs
make panel-logs            # logs backend + worker
make backend-logs          # logs backend + worker
make frontend-logs         # logs frontend
make nemoclaw-logs         # logs do NemoClaw runtime
make ollama-logs           # logs do Ollama
make top                   # uso de recursos da stack
```

### NemoClaw e Ollama

```bash
make nemoclaw-dashboard    # dashboard do runtime
make ollama-list           # lista modelos no Ollama
make ollama-sign           # login interativo no Ollama
```

### Banco e painel

```bash
make panel-url             # imprime URLs do painel
make panel-db-migrate      # alias para make migrate
make migrate               # alembic upgrade head no panel-backend
```

### Subir servico individual

```bash
make up-postgres
make up-redis
make up-ollama
make up-searxng
make up-searxng-proxy
make up-panel-backend
make up-panel-worker
make up-panel-frontend
make up-token-init
make up-nemoclaw
make up-nemoclaw-with-cache
```

### Build, release e limpeza

```bash
make build                 # build local das imagens
make build-with-cache      # build local com cache
make pull                  # pull das imagens remotas
make push                  # push das imagens
make release               # images-build + images-push
make clean                 # alias para reset (remove volumes da stack)
make reset                 # remove containers + volumes (com confirmacao)
make destroy               # remove stack + imagens/cache locais (com confirmacao)
make destroy-complete      # limpeza completa adicional da stack
make prune                 # docker system prune -af
```

## Requisitos

- Windows, macOS ou Linux
- Docker Desktop ativo
- `.env` preenchido a partir de `.env.example`
- Para GPU: driver NVIDIA + suporte a `--gpus all`

Teste rapido de GPU:

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base nvidia-smi
```

## Fluxo SDD (especificacao antes de implementacao)

1. `CONSTITUTION`
2. `BRIEF`
3. `SPEC`
4. `CLARIFY` (quando houver ambiguidade)
5. `PLAN`
6. `TASK`
7. implementacao + validacao

Para templates e referencias do SDD, consulte a documentação do projeto em `docs/`
make sdd-prompts
make sdd-example
```

## Estrutura do projeto (resumo)

```text
.env.example
Makefile
docker/
  base/
    bootstrap-scripts/
  clawdevs-nemoclaw/
  clawdevs-ollama/
  clawdevs-panel-backend/
  clawdevs-panel-worker/
  clawdevs-panel-frontend/
```
