# clawdevs-ai (Windows only)

Fluxo para subir Kubernetes local no Docker Desktop (Windows), validar GPU e rodar o pod `openclaw`.

## Requisitos

- Windows 11
- Docker Desktop com suporte a GPU
- Driver NVIDIA atualizado
- `minikube`, `kubectl`, `kind` e `make` no PATH

## Comandos principais

```bash
make gpu-doctor
make minikube-up
make gpu-plugin
make gpu-check
```

## Alternativa com kind

```bash
make kind-up
make kind-gpu-plugin
make kind-gpu-check
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

Para testar GPU com pod simples:

```bash
make gpu-test-apply
make gpu-test-logs
```

## Manifestos

- `k8s/openclaw-pod.yaml`
- `k8s/gpu-test.yaml`
