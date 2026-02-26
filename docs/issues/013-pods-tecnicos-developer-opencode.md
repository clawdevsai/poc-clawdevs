# [team-devs-ai] Pod Developer com OpenCode e Ollama

**Fase:** 1 — Agentes  
**Labels:** agents, k8s, opencode

## Descrição

Implantar o pod do Agente Developer com OpenCode instalado e volume persistente (PVC) para código. O Developer usa Ollama (via GPU Lock) para inferência local e opera apenas dentro do OpenCode para gerar código.

## Critérios de aceite

- [ ] Deployment do Developer com OpenCode; volume PVC no NVMe para persistência do código.
- [ ] Developer obtém GPU Lock antes de usar Ollama; libera ao terminar.
- [ ] Regra aplicada: todo planejamento e codificação ocorrem dentro do OpenCode (orquestrador não escreve código).
- [ ] Modelo recomendado (ex.: deepseek-coder:6.7b) documentado ou configurável.

## Referências

- [02-agentes.md](../02-agentes.md) (Agente Developer)
- [33-opencode-controller.md](../33-opencode-controller.md)
- [04-infraestrutura.md](../04-infraestrutura.md)
