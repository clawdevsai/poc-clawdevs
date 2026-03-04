# [team-devs-ai] ResourceQuota e LimitRange no namespace ai-agents

**Fase:** 0 — Fundação  
**Labels:** foundation, k8s, infra

## Descrição

Aplicar ResourceQuota e LimitRange no namespace do enxame (ex.: `ai-agents`) para garantir que o cluster não ultrapasse os 65% e que cada container tenha limites padrão definidos.

## Critérios de aceite

- [ ] ResourceQuota criada: limites de `requests.cpu`, `limits.cpu`, `requests.memory`, `limits.memory` e `pods` coerentes com 65% da máquina de referência.
- [ ] LimitRange definida: default e defaultRequest por Container (ex.: default 2 CPU, 2Gi RAM; defaultRequest 500m CPU, 512Mi RAM).
- [ ] **Node selectors** (ou equivalente em limits.yaml/manifests): pods DevOps e UX configurados para usar exclusivamente CPU (ex.: `workload-type: cpu-only`), reservando GPU para Developer, Architect e QA — ver [04-infraestrutura.md](../04-infraestrutura.md), [006-gpu-lock-script.md](006-gpu-lock-script.md).
- [ ] Namespace `ai-agents` (ou equivalente) usado de forma consistente nos deployments.
- [ ] Documentação ou comentários nos YAML explicando os valores.

## Referências

- [04-infraestrutura.md](../04-infraestrutura.md) (seção Resource Quota e LimitRange)
