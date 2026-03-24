# OpenClaw Runtime Image

Imagem otimizada para o `StatefulSet` do OpenClaw, com dependências e OpenClaw pré-instalados.

## Build local

```bash
docker build \
  --build-arg OPENCLAW_VERSION=2026.3.23-2 \
  -t clawdevsai/openclaw-runtime:2026.3.23-2 \
  -t clawdevsai/openclaw-runtime:latest \
  -f docker/openclaw-runtime/Dockerfile .
```

## Push Docker Hub

```bash
docker login -u clawdevsAI

docker push clawdevsai/openclaw-runtime:2026.3.23-2
docker push clawdevsai/openclaw-runtime:latest
```

## Uso no Kubernetes

O `k8s/base/openclaw-pod.yaml` já está apontando para `clawdevsai/openclaw-runtime:latest`.
