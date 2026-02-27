# SOUL — Development Team (7 agentes)

ConfigMap **soul-development-agents**: SOUL dos agentes do time técnico no **escopo development**.

- **Escopo:** `devops.md`, `architect.md`, `developer.md`, `qa.md`, `cybersec.md`, `ux.md`, `dba.md`. Fonte: [docs/soul/](../../../docs/soul/) (DevOps-SRE, Architect, Developer, QA, CyberSec, UX, DBA).
- **Gateway:** O deployment openclaw usa initContainer `soul-merge` para juntar este ConfigMap com `soul-management-agents` em `/workspace/soul`.
- **Pods do time técnico:** Pods (ex.: Developer, slot Revisão pós-Dev) que precisarem do SOUL podem montar este ConfigMap:

```yaml
volumes:
  - name: soul-development-agents
    configMap:
      name: soul-development-agents
      optional: true
# volumeMounts: mountPath: /workspace/soul
```

Ref: [management-team/soul/README.md](../management-team/soul/README.md), [docs/soul/README.md](../../../docs/soul/README.md).
