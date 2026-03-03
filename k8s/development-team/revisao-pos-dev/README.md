# Revisão pós-Dev — Slot único (007 + 125)

Um único consumidor do stream **code:ready** (consumer group **revisao-pos-dev**). Adquire o GPU Lock uma vez, executa Architect → QA → CyberSec → DBA em sequência, libera e envia XACK.

## ConfigMap dos scripts

Criar o ConfigMap a partir dos scripts (uma vez):

```bash
kubectl create configmap revisao-slot-scripts -n ai-agents \
  --from-file=slot_revisao_pos_dev.py=app/slot_revisao_pos_dev.py \
  --from-file=gpu_lock.py=app/gpu_lock.py \
  --dry-run=client -o yaml | kubectl apply -f -
```

Ou use `make revisao-slot-configmap` (se definido no Makefile).

## Apply

```bash
kubectl apply -f k8s/development-team/revisao-pos-dev/configmap-env.yaml
kubectl apply -f k8s/development-team/revisao-pos-dev/deployment.yaml
```

O deployment monta o ConfigMap `revisao-slot-scripts` (crie antes). Hard timeout por execução do slot: documentado em docs/39 e docs/04 (até 300 s para o bloco de revisão).

Ref: [docs/39-consumer-groups-pipeline-revisao.md](../docs/39-consumer-groups-pipeline-revisao.md).
