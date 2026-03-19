# clawdevs-ai (Windows only)

Fluxo para subir Kubernetes local no Docker Desktop (Windows), validar GPU real e rodar o stack (`ollama` + `openclaw`).

## Requisitos

- Windows 11
- Docker Desktop com suporte a GPU
- Driver NVIDIA atualizado
- `minikube`, `kubectl` e `make` no PATH
- Docker Desktop Kubernetes habilitado em `Settings > Kubernetes`

## Comandos principais

```bash
make preflight
make manifests-validate
make gpu-doctor
make docker-k8s-check
make gpu-plugin-apply
make gpu-node-check
```

O arquivo `k8s/.env` deve conter apenas valores preenchidos localmente. Antes de aplicar o stack, rode `make preflight` para validar os segredos obrigatorios.
Para manter o pod estavel e ainda ter logs úteis, use `OPENCLAW_LOG_LEVEL=info` em `k8s/.env`. Deixe `DEBUG_LOG_ENABLED=true` apenas para rastrear o bootstrap e espelhar sessoes dos agentes no log principal, porque esse modo gera muito mais ruido e pode atrapalhar o fluxo normal.

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

Observacao: o caminho Minikube com driver Docker pode nao expor NVML corretamente em alguns ambientes Windows/WSL2. O fluxo recomendado para GPU real neste repo e `docker-desktop`.

## GitHub (gh CLI)

- O repositório padrão para ações GitHub dos agentes deve vir de `GITHUB_REPOSITORY` (definido em `k8s/.env` e injetado no pod).
- O token deve vir de `GITHUB_TOKEN` (também definido em `k8s/.env` e injetado no pod).
- Para comandos `gh` fora de um checkout local, usar `--repo "$GITHUB_REPOSITORY"`.
- Documentação oficial: https://cli.github.com/manual/gh

## Manifestos

- `k8s/openclaw-pod.yaml`
- `k8s/nvidia-runtimeclass.yaml`
- `k8s/nvidia-device-plugin.yaml`


https://clawhub.ai/pskoett/self-improving-agent
