# SOUL — Management Team (CEO, PO)

ConfigMap **soul-management-agents**: SOUL do **CEO** e do **PO** (escopo management).

- **Escopo:** `ceo.md`, `po.md`. Fonte: [docs/soul/CEO.md](../../../docs/soul/CEO.md), [docs/soul/PO.md](../../../docs/soul/PO.md).
- **Gateway:** O deployment openclaw usa initContainer `soul-merge` para juntar este ConfigMap com `soul-development-agents` em `/workspace/soul` **e copiar `ceo.md` para `/workspace/SOUL.md`**. Não existe mais `workspace-ceo-configmap.yaml`; o SOUL do CEO vem unicamente de `soul-management-agents`.

Ref: [docs/soul/README.md](../../../docs/soul/README.md).
