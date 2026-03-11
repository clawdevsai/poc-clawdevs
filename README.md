# ClawDevs AI

Repositorio reduzido para o nucleo operacional da nova arquitetura.

## Fluxo ativo

```text
cmd:strategy -> PO -> draft.2.issue -> Architect -> task:backlog -> Developer -> event:devops -> DevOps
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
  agents/   agentes do fluxo principal
  runtime/  loop compartilhado e contratos
  core/     governanca e degradacao
  shared/   redis e estado de issue
tests/
  test_runtime.py
  test_orchestration.py
k8s/
  stack.yaml
```

## Stack de inferencia

O runtime atual assume explicitamente esta stack:

```text
Workers -> OpenClaw Gateway -> Ollama
```

Contexto do agente no OpenClaw:

```text
profile + rules + skills + allowed tools + output schema + instruction
```

## GPU (RTX 3060 Ti + Minikube)

A stack Kubernetes foi preparada para GPU:

- `ollama` com `resources.requests/limits.nvidia.com/gpu: 1`
- `openclaw-gateway` em CPU (gateway chama Ollama via rede)
- `minikube` inicializado com `--gpus all`
- addon `nvidia-device-plugin` habilitado no `make up`
- fallback sem CDI: `make up-host-ollama` (Ollama no host, cluster sem pod Ollama)

Pre-requisitos no host:

- driver NVIDIA instalado
- Docker Desktop com suporte a GPU
- NVIDIA Container Toolkit funcional no host Docker
- Minikube e kubectl instalados

## Variaveis minimas

```bash
OPENCLAW_GATEWAY_WS=ws://openclaw-gateway:18789
MODEL_PROVIDER=ollama
MODEL_MODE=local
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5-coder:32b
```

## Comandos

```bash
make test
make check-runtime-stack
make up
make up-host-ollama
make status
make down
```

No modo host (`make up-host-ollama`), voce pode sobrescrever a imagem do Gateway:

```bash
make up-host-ollama OPENCLAW_GATEWAY_IMAGE=ghcr.io/openclaw/openclaw:latest
```

Se `make` nao estiver instalado no ambiente local, use fallback direto:

```bash
minikube start --driver=docker --gpus all
minikube addons enable nvidia-device-plugin
minikube image build -t clawdevs-ai:latest .
kubectl apply -f k8s/stack.yaml
kubectl get pods -n clawdevs-ai
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia.com/gpu
```

## Telegram -> CEO

O deployment `telegram-director` recebe mensagens do Telegram e publica no stream `cmd:strategy` (entrada do fluxo CEO/PO).

Configure:

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

