# [team-devs-ai] Pods Architect, QA, CyberSec e UX (Ollama + GPU Lock)

**Fase:** 1 — Agentes  
**Labels:** agents, k8s, ollama

## Descrição

Implantar os pods dos agentes Architect, QA, CyberSec e UX. Cada um usa Ollama via GPU Lock (um por vez). Podem ser acordados por eventos (ex.: code:ready) e atuar como sidecars ou Jobs event-driven.

## Critérios de aceite

- [ ] Deployments (ou Jobs) para Architect, QA, CyberSec e UX.
- [ ] Todos usam o mesmo endpoint Ollama e adquirem GPU Lock antes de inferência.
- [ ] Modelos sugeridos por tipo (ex.: llama3:8b para Architect/QA/CyberSec, phi3:mini para UX quando leve).
- [ ] Integração com Redis Streams: acordar sob evento (ex.: após Developer publicar code:ready); evitar polling.
- [ ] Webhooks ou evento post-commit para evitar "ghost commits" (revisão só quando código sincronizado).

## Referências

- [02-agentes.md](../02-agentes.md)
- [03-arquitetura.md](../03-arquitetura.md)
- [04-infraestrutura.md](../04-infraestrutura.md)
