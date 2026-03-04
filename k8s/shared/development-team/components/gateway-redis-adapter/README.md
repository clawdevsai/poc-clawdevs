# Gateway Redis Adapter (Fase 1 — 018)

Serviço HTTP que recebe POST `/publish` com JSON `{ "stream": "cmd:strategy" | "task:backlog" | "draft.2.issue" | ..., "data": { ... } }` e publica no Redis via XADD. O OpenClaw (ou outro gateway) pode chamar este endpoint para publicar eventos a partir das respostas do CEO/PO.

- **Health:** GET `/health` (verifica Redis).
- **Publicar:** POST `/publish` com body JSON.

Criar ConfigMap dos scripts: `make gateway-redis-adapter-configmap`. Aplicar: `kubectl apply -f k8s/development-team/gateway-redis-adapter/`. Por padrão `replicas: 0`; ajustar para 1 quando for usar.

Ref: [docs/38-redis-streams-estado-global.md](../../../docs/38-redis-streams-estado-global.md), [docs/41-fase1-agentes-soul-pods.md](../../../docs/41-fase1-agentes-soul-pods.md).
