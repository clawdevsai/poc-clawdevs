# ClawDevs AI

Repositorio reduzido para o nucleo operacional da nova arquitetura.

## Fluxo ativo

```text
Diretor (UI/Telegram) -> cmd:strategy -> PO -> draft.2.issue -> Architect -> task:backlog -> Developer -> code:ready -> pr:review -> QA + DBA + CyberSec -> consenso (approve => event:devops | blocked => task:backlog) -> (>=6 rounds => Architect-review) -> DevOps
```

## Estado atual

O repositorio hoje nao e mais o projeto historico completo. Ele foi reduzido para o runtime principal e para o fluxo central de desenvolvimento por agentes.

O nucleo ativo ja possui:

- runtime compartilhado para todos os workers
- envelope padrao de evento com `run_id`, `trace_id`, `attempt` e budget
- budgets de execucao com enforcement no loop do runtime
- `ToolRegistry` minimo para envio ao OpenClaw
- stack explicita `OpenClaw + Ollama`
- assets explicitos de `profiles`, `rules` e `skills` para o OpenClaw
- governanca centralizada em um unico modulo
- logs estruturados em JSON
- resultados de agente com `status_code` e `event_name`

## Estrutura

```text
app/
  agents/     agentes do fluxo principal (PO, Architect, Developer, QA, DevOps)
  runtime/    loop compartilhado, contratos, OpenClaw client e ToolRegistry
  core/       governanca e orquestracao (strikes, estados, degradacao)
  shared/     Redis e estado de issue
  openclaw/   assets do OpenClaw: profiles, rules, skills, output_schemas, souls
  interfaces/ bridges externas (ex.: telegram-director)
tests/
  test_runtime.py
  test_orchestration.py
k8s/
  stack.yaml
  stack-host-ollama.yaml
director-console/
  Next.js + Tailwind (painel do diretor)
```

## Stack de inferencia

O runtime atual assume explicitamente esta stack:

```text
Workers -> OpenClaw Gateway -> Ollama
```

Todos os pods de agentes e gateway usam imagem com `gh` CLI instalada (`gh --version`).

Contexto do agente no OpenClaw:

```text
profile + rules + skills + allowed tools + output schema + instruction
```

## GPU (RTX 3060 Ti + Minikube)

A stack Kubernetes suporta dois modos:

**Modo padrão (Ollama no host)** — recomendado quando a GPU esta no host:

- `make up` ou `make up-host-ollama`: sobe o cluster sem GPU no node, usa Ollama no host; gateway e workers no Minikube.
- `stack-host-ollama.yaml`: sem pod Ollama no cluster; addon `nvidia-device-plugin` nao e obrigatorio.

**Modo GPU no cluster** — pod Ollama dentro do Minikube com GPU:

- `ollama` com `resources.requests/limits.nvidia.com/gpu: 1`
- `openclaw-gateway` em CPU (gateway chama Ollama via rede)
- `make up-gpu`: minikube com `--gpus all`, addon `nvidia-device-plugin` habilitado
- Fallbacks: `make up-force` (recria profile GPU), `make up-cdi` (CDI: `--gpus nvidia.com`)

Pre-requisitos no host:

- driver NVIDIA instalado
- Docker Desktop com suporte a GPU
- NVIDIA Container Toolkit funcional no host Docker
- Minikube e kubectl instalados

## Variaveis minimas

```bash
OPENCLAW_GATEWAY_WS=ws://openclaw-gateway:18789
MODEL_PROVIDER=ollama
MODEL_MODE=cloud
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen3-next:80b-cloud
```

Roteamento por papel (primary/fallback) suportado via env (exemplos no `k8s/stack.yaml`):

```bash
OPENCLAW_MODEL_CEO_PRIMARY=qwen3.5:397b-cloud
OPENCLAW_MODEL_CEO_FALLBACK=qwen3-next:80b-cloud
OPENCLAW_MODEL_PO_PRIMARY=qwen3-next:80b-cloud
OPENCLAW_MODEL_PO_FALLBACK=ministral-3:14b-cloud
OPENCLAW_MODEL_ARCHITECT_DRAFT_PRIMARY=devstral-2:123b-cloud
OPENCLAW_MODEL_ARCHITECT_DRAFT_FALLBACK=qwen3.5:397b-cloud
OPENCLAW_MODEL_DEVELOPER_PRIMARY=qwen3-coder:480b-cloud
OPENCLAW_MODEL_DEVELOPER_FALLBACK=qwen3-coder-next:cloud
OPENCLAW_MODEL_QA_PRIMARY=gpt-oss:120b-cloud
OPENCLAW_MODEL_QA_FALLBACK=nemotron-3-nano:30b-cloud
OPENCLAW_MODEL_DEVOPS_PRIMARY=devstral-small-2:24b-cloud
OPENCLAW_MODEL_DEVOPS_FALLBACK=rnj-1:8b-cloud
```

## Comandos

```bash
make test
make check-runtime-stack
make preflight              # valida binarios (minikube, kubectl, docker)
make up                     # sobe stack com Ollama no host (padrao)
make up-host-ollama          # idem
make up-gpu                  # sobe stack com GPU no cluster (pod Ollama)
make up-force                # recria profile Minikube GPU e sobe
make status
make logs
make down                    # remove stack (pod Ollama no cluster)
make down-host               # remove stack host-ollama
make gh-check
make env-sync                # .env -> configmap + secret (gh-token-sync)
make gh-auth-check
make telegram-enable TELEGRAM_BOT_TOKEN=<token> TELEGRAM_CHAT_ID=<chat_id>
make telegram-logs
```

## Director Console

Existe agora uma plataforma unica para o diretor em Next.js + Tailwind:

```text
director-console/
```

Ela oferece:

- overview executivo com estados de issue no Redis
- volumes de stream (`cmd:strategy`, `draft.2.issue`, `code:ready`, `event:devops`)
- leitura de PRs no GitHub
- console para enviar novas diretivas ao pipeline

Execucao local:

```bash
cd director-console
npm install
# Copie o env de exemplo (Windows: copy / Linux ou macOS: cp)
copy .env.local.example .env.local   # Windows
# cp .env.local.example .env.local   # Linux / macOS
npm run dev
```

Se o Redis estiver rodando no cluster, use port-forward antes:

```bash
kubectl -n clawdevs-ai port-forward svc/redis 6379:6379
```

E ajuste em `director-console/.env.local` conforme o ambiente:

```bash
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
GITHUB_REPO=org/repo    # repositorio a ser consultado (issues/PRs)
GITHUB_TOKEN=<token>
```

As variaveis de stream (`STREAM_CMD_STRATEGY`, `STREAM_DRAFT_ISSUE`, `QA_STREAM`, `STREAM_EVENT_DEVOPS`) e `KEY_PREFIX_PROJECT` devem bater com o runtime; o exemplo em `.env.local.example` ja esta alinhado.

No modo host (`make up-host-ollama` ou `make up`), para usar uma imagem externa do Gateway:

```bash
make up-host-ollama OPENCLAW_GATEWAY_IMAGE=ghcr.io/openclaw/openclaw:latest
```

Se `make` nao estiver instalado no ambiente local, use os binarios direto (exemplo para stack com GPU no cluster):

```bash
minikube start --driver=docker --gpus all
minikube addons enable nvidia-device-plugin
minikube image build -t clawdevs-ai:latest .
kubectl apply -f k8s/stack.yaml
kubectl get pods -n clawdevs-ai
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia.com/gpu
```

Para stack com Ollama no host, use `k8s/stack-host-ollama.yaml` em vez de `k8s/stack.yaml`.

### Director Console no Kubernetes

O `director-console` e publicado como deployment separado. Para acessar:

```bash
kubectl -n clawdevs-ai port-forward svc/director-console 3000:3000
```

## Telegram -> CEO

O deployment `telegram-director` recebe mensagens do Telegram e publica no stream `cmd:strategy` (entrada do fluxo CEO/PO).

Comandos suportados no chat:

- `/status`: retorna status estruturado (tarefas por estado, fluxo PO/QA/DevOps, PRs GitHub)
- `iniciar desenvolvimento <demanda>`: enfileira demanda no pipeline de agentes
- `/pesquisar <tema>`: CEO responde com contexto web best-effort + plano objetivo

Configure via Make (recomendado):

```bash
make telegram-enable TELEGRAM_BOT_TOKEN=<BOT_TOKEN> TELEGRAM_CHAT_ID=<CHAT_ID>
make telegram-logs
```

Ou via ConfigMap e restart manual:

```bash
kubectl -n clawdevs-ai patch configmap clawdevs-config --type merge -p "{\"data\":{\"TELEGRAM_BOT_TOKEN\":\"<BOT_TOKEN>\",\"TELEGRAM_CHAT_ID\":\"<CHAT_ID>\"}}"
kubectl -n clawdevs-ai rollout restart deployment/telegram-director
kubectl -n clawdevs-ai logs deployment/telegram-director -f
```

Envie uma mensagem para o bot no chat configurado. O worker PO vai consumir via `cmd:strategy`.

## Escopo removido

Foram excluidos da repo:

- UI paralela
- scripts operacionais antigos
- safety stack periferica
- kanban legado
- slots e automacoes fora do fluxo principal
- documentacao historica que nao refletia mais o codigo vivo

## Licenca

MIT
