# clawdevs-ai (Windows only)

Fluxo para subir Kubernetes local com Minikube no Docker Desktop (Windows), expor GPU real e rodar o stack (`ollama` + `openclaw`).

## Fluxo de spec

Antes de implementar uma mudanca, o fluxo recomendado neste repositorio e:

0. `CONSTITUTION` com principios e guardrails
1. `BRIEF` com contexto e objetivo executivo
2. `SPEC` com comportamento observavel, contratos e criterios de aceite
3. `CLARIFY` quando houver ambiguidade
4. `PLAN` tecnico e arquitetura
5. `TASK` tecnica e issues
6. `FEATURE` e `USER STORY` quando fizer sentido para o fluxo de produto
7. implementacao e validacao

Templates e artefatos:

- `k8s/base/openclaw-config/shared/BRIEF_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/CLARIFY_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/PLAN_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/TASK_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/VALIDATE_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/SDD_OPERATIONAL_PROMPTS.md`
- `k8s/base/openclaw-config/shared/SPEC_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/CONSTITUTION.md`
- `k8s/base/openclaw-config/shared/SDD_CHECKLIST.md`
- `k8s/base/openclaw-config/shared/SDD_FULL_CYCLE_EXAMPLE.md`
- `k8s/base/openclaw-config/shared/SPECKIT_ADAPTATION.md`
- `k8s/base/openclaw-config/shared/initiatives/internal-sdd-operationalization/`
- `/data/openclaw/backlog/specs/`
- `/data/openclaw/backlog/briefs/`
- `/data/openclaw/backlog/user_story/`
- `/data/openclaw/backlog/tasks/`

O mesmo contrato vale para:
- a plataforma interna da ClawDevs AI
- os projetos e entregas feitos por ela

Em ambos os casos, a SPEC é a fonte de verdade do comportamento pretendido.
Quando houver ambiguidade, o passo correto é `clarify` antes de `plan` e `tasks`.
Use o `SDD_CHECKLIST.md` como gate de prontidao antes de mover uma entrega para a proxima etapa.
Use os templates para manter o fluxo repetivel entre plataforma interna e projetos.
Use `SDD_OPERATIONAL_PROMPTS.md` para iniciar conversas e execucoes com os agentes.
Use `SDD_FULL_CYCLE_EXAMPLE.md` como molde de referencia para novas iniciativas.
Use `shared/initiatives/internal-sdd-operationalization/` como iniciativa real pronta para execucao.

## Modo Vibe Coding

ClawDevs AI deve operar em ciclos curtos e demonstraveis:

1. definir um resultado visivel
2. escrever a spec minima
3. entregar um slice vertical funcional
4. validar com demo
5. endurecer com testes, logs e observabilidade

Regra pratica:
- se a mudanca nao cabe em uma demo curta, ela esta grande demais
- se o fluxo ficar invisivel por muito tempo, ele precisa ser fatiado
- se a solução nao for reversivel, ela precisa de mais cuidado antes de subir

## Requisitos

- Windows 11
- Docker Desktop com suporte a GPU
- Driver NVIDIA atualizado
- `minikube`, `kubectl` e `make` no PATH
- Docker Desktop rodando, com GPU exposta aos containers do driver Docker

## Comandos principais

```bash
make preflight
make manifests-validate
make clawdevs-up
```

Esse target executa o fluxo completo no Minikube com GPU:

```bash
make minikube-up
make minikube-context
make minikube-addons
kubectl apply -k k8s
kubectl get node clawdevs-ai -o custom-columns=NAME:.metadata.name,GPU_CAP:.status.capacity.nvidia\.com/gpu,GPU_ALLOC:.status.allocatable.nvidia\.com/gpu
```

O arquivo `k8s/.env` deve conter apenas valores preenchidos localmente. Antes de aplicar o stack, rode `make preflight` para validar os segredos obrigatorios.
Para manter o pod estavel e ainda ter logs úteis, use `OPENCLAW_LOG_LEVEL=info` em `k8s/.env`. Deixe `DEBUG_LOG_ENABLED=true` apenas para rastrear o bootstrap e espelhar sessoes dos agentes no log principal, porque esse modo gera muito mais ruido e pode atrapalhar o fluxo normal.

O `make minikube-up` já sobe o profile com `--gpus=all`, então o node passa a anunciar `nvidia.com/gpu` sem passo manual extra.

Por padrão, o deploy `kubectl apply -k k8s` já usa o overlay `gpu`. Na pratica, isso significa que o pod `ollama` sobe com `runtimeClassName: nvidia` e `limits.nvidia.com/gpu: 1`.

## Fluxo Alternativo (Docker Desktop)

Se você quiser usar o contexto `docker-desktop` em vez do Minikube, siga este caminho:

```bash
make gpu-doctor
make docker-k8s-check
make gpu-plugin-apply
make gpu-node-check
```

Quando o `gpu-node-check` mostrar `GPU_ALLOC` diferente de `<none>`, aplique o stack no contexto `docker-desktop`:

```bash
make gpu-migrate-apply
```

## Dashboard

```bash
make dashboard
```

Ou apenas URL:

```bash
make dashboard-url
```

## OpenClaw

Aplicar pod:

```bash
make openclaw-apply
```

Ver logs:

```bash
make openclaw-logs
```

Observacao: o fluxo validado para GPU real neste repo usa Minikube com `--gpus=all`. O caminho `docker-desktop` continua disponivel como alternativo.

## GitHub (gh CLI)

- A organização padrão para ações GitHub dos agentes deve vir de `GITHUB_ORG` (definido em `k8s/.env` e injetado no pod).
- Opcionalmente, `GITHUB_DEFAULT_REPOSITORY` define o primeiro repositório ativo na inicialização.
- O token deve vir de `GITHUB_TOKEN` (também definido em `k8s/.env` e injetado no pod).
- O repositório ativo por sessão fica em `/data/openclaw/contexts/active_repository.env` (`ACTIVE_GITHUB_REPOSITORY`).
- Para comandos `gh` fora de um checkout local, usar `--repo "$ACTIVE_GITHUB_REPOSITORY"` (ou `"$GITHUB_REPOSITORY"` para compatibilidade).
- Utilitários de contexto multi-repo no pod:
  - `claw-repo-discover [filtro]` para descobrir repositórios da organização
  - `claw-repo-ensure <repo> [--create]` para validar existência e criar quando autorizado
  - `claw-repo-switch <repo> [branch]` para trocar contexto de todos os agentes/workspaces
- Documentação oficial: https://cli.github.com/manual/gh

## Estrutura K8s

```text
k8s/
  .env
  .env.example
  kustomization.yaml
  base/
    kustomization.yaml
    openclaw-pod.yaml
    ollama-pod.yaml
    ollama-pvc.yaml
    networkpolicy-allow-egress.yaml
    openclaw-config/
      ceo/
      po/
      arquiteto/
      dev_backend/
  overlays/
    gpu/
      kustomization.yaml
      ollama-gpu-patch.yaml
      nvidia-device-plugin.yaml
      nvidia-runtimeclass.yaml
```

O comando padrão de deploy continua sendo:

```bash
kubectl apply -k k8s
```

O `base` concentra o stack comum e os agentes. O overlay `gpu` adiciona `RuntimeClass`, device plugin e o patch do `ollama` para GPU, e ele e aplicado por padrao pelo `kustomization` raiz.


https://clawhub.ai/pskoett/self-improving-agent
