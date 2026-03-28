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

# Documentação operacional (clawdevs-ai)

## 📋 Referências Principais

- **Análise Completa do Projeto:** [analise-projeto.md](./analise-projeto.md) — Sumário executivo, arquitetura de alto nível, stack tecnológico e operação
- **Arquitetura Técnica Detalhada:** [arquitetura-tecnica.md](./arquitetura-tecnica.md) — Implementação técnica, topologia de rede, fluxos de dados e troubleshooting

## 📚 Documentação Operacional

- **O que a aplicação faz e exemplos de uso:** [aplicacao-e-exemplos.md](./aplicacao-e-exemplos.md)
- **Papel de cada agente (um arquivo por agente):** [agentes/README.md](./agentes/README.md)
- **Arquivos do workspace do agente (OpenClaw + ClawDevs):** [workspace-arquivos-agente.md](./workspace-arquivos-agente.md)
- **Engenharia de prompts (técnicas reutilizáveis):** [engenharia-de-prompts.md](./engenharia-de-prompts.md)
- **Planos de design / implementação (rascunhos):** [plans/](./plans/)

## Stack Docker Compose

| Recurso | Nome / observação |
|--------|-------------------|
| OpenClaw | `StatefulSet` `clawdevs-ai`, container típico `clawdevs-ai-0`, container `openclaw` |
| Ollama | `Container` `ollama`, `Service` `ollama` |
| PVC | `ollama-data` (`docker/base/ollama-pvc.yaml`) |
| SearXNG | `docker/base/searxng-deployment.yaml` |
| Painel de controle | `docker/base/control-panel/` — frontend, backend API, worker, Postgres, Redis (`docker-compose apply -k docker/base/control-panel/` via `make panel-apply`) |
| Rede | `docker/base/networkpolicy-allow-egress.yaml` |
| Segredos | `openclaw-auth`, `ollama-auth`, `clawdevs-panel-auth` gerados por `container/kustomization.yaml` a partir de `container/.env` |
| Config agentes | `ConfigMap` `openclaw-agent-config` (arquivos em `docker/base/openclaw-config/`) |

## Kustomize

- `docker-compose apply -k container` usa apenas `docker/base` (via `container/kustomization.yaml` → `resources: [base]`).
- GPU no Ollama: overlay `docker/overlays/gpu` (RuntimeClass, device plugin, patch do container `ollama`). Aplicar com `make openclaw-apply-gpu`, `make gpu-migrate-apply` (contexto `docker-desktop`) ou `docker-compose apply -k docker/overlays/gpu`.

## Segredos obrigatórios (`make preflight`)

Chaves que devem estar preenchidas em `container/.env`:

- `OPENCLAW_GATEWAY_TOKEN`
- `TELEGRAM_BOT_TOKEN_CEO`
- `TELEGRAM_CHAT_ID_CEO`
- `GIT_TOKEN`
- `GIT_ORG`
- `OLLAMA_API_KEY`

Demais variáveis: ver `container/.env.example`.

## Targets Make relevantes

- `make preflight` — valida segredos em `container/.env`
- `make manifests-validate` — `docker-compose kustomize container`
- `make clawdevs-up` — Docker + addons + `stack-apply` + status
- `make clawdevs-rebuild` — `destroy-all`, sobe cluster de novo, `storage-enable-expansion`, `stack-apply`
- `make stack-apply` — `ollama-apply` + `openclaw-apply-gpu` + `panel-apply` (OpenClaw pelo overlay `docker/overlays/gpu`, como definido no `Makefile`)
- `make openclaw-apply` — `docker-compose apply -k container` (contexto `KUBE_CONTEXT`, default `clawdevs-ai`)
- `make openclaw-apply-gpu` — aplica `docker/overlays/gpu`
- `make openclaw-restart` / `make openclaw-logs` — `statefulset/clawdevs-ai`
- `make ollama-volume-apply` — PVC; `make ollama-apply` — recria container `ollama`
- `make panel-apply` / `panel-status` / `panel-forward` / `panel-db-migrate` / `panel-restart` / `panel-destroy` — painel ClawDevs
- `make services-expose` / `services-stop` — port-forwards locais (painel 3000/8000 + gateway 18789; ver saída do target)
- Fluxo Docker Desktop + GPU: `gpu-doctor`, `docker-container-check`, `gpu-plugin-apply`, `gpu-node-check`, `gpu-migrate-apply`

## Exec no container OpenClaw

Usar o workload real, por exemplo:

```bash
docker-compose --context=clawdevs-ai exec -it statefulset/clawdevs-ai -c openclaw -- bash
```

## Estrutura `container/` (resumo)

```text
container/
  .env
  .env.example
  kustomization.yaml
  base/
    kustomization.yaml
    openclaw-container.yaml
    ollama-container.yaml
    ollama-pvc.yaml
    networkpolicy-allow-egress.yaml
    searxng-deployment.yaml
    openclaw-config/
    control-panel/
  overlays/
    gpu/
```
