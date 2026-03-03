# Pod Developer (Fase 1 — 013)

Deployment do agente **Developer**: consome tarefas do Redis (`task:backlog`), adquire **GPU Lock** antes de usar Ollama, processa (stub; em produção integrar **OpenCode**) e envia XACK. Workspace em **PVC** para persistência do código.

## Recursos

- **deployment.yaml** — Pod com imagem Python, scripts montados via ConfigMap, PVC em `/workspace`.
- **pvc.yaml** — `developer-workspace` (5Gi).
- **configmap-env.yaml** — REDIS_HOST, stream, group.

## ConfigMap de scripts

O deployment espera o ConfigMap `developer-scripts` com `developer_worker.py` e `gpu_lock.py`. Crie com:

```bash
kubectl create configmap developer-scripts -n ai-agents \
  --from-file=developer_worker.py=app/developer_worker.py \
  --from-file=gpu_lock.py=app/gpu_lock.py \
  --dry-run=client -o yaml | kubectl apply -f -
```

Ou adicione alvo `make developer-configmap` no Makefile.

## Replicas

Por padrão o deployment pode estar com `replicas: 0` para não disputar o gateway único; aumentar para 1 quando quiser o Developer como consumidor dedicado de `task:backlog`.

Pasta: `k8s/development-team/developer/`. Apply: `kubectl apply -f k8s/development-team/developer/` (após `make developer-configmap`).

Ref: [docs/issues/013-pods-tecnicos-developer-opencode.md](../../../docs/issues/013-pods-tecnicos-developer-opencode.md), [docs/02-agentes.md](../../../docs/02-agentes.md).
