# SOUL — Management Team (CEO, PO)

ConfigMap **soul-management-agents**: SOUL do **CEO** e do **PO** (escopo management).

- **Escopo:** `ceo.md`, `po.md`. Fonte: [docs/soul/CEO.md](../../../docs/soul/CEO.md), [docs/soul/PO.md](../../../docs/soul/PO.md).
- **Gateway:** O deployment openclaw usa initContainer `soul-merge` para juntar este ConfigMap com `soul-development-agents` em `/workspace/soul`. O workspace do CEO no gateway continua a usar [workspace-ceo-configmap.yaml](../openclaw/workspace-ceo-configmap.yaml) (SOUL.md injetado no system prompt).

Ref: [docs/soul/README.md](../../../docs/soul/README.md).
