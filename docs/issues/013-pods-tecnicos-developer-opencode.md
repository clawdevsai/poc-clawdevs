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

## OpenCode na imagem (evolução Fase 1)

Há um **Dockerfile** em [k8s/development-team/developer/Dockerfile](../../k8s/development-team/developer/Dockerfile). O deployment usa hoje a imagem `python:3.12-slim` com scripts montados via ConfigMap; para usar a imagem local com dependências fixas (e eventual OpenCode), build e use:

```bash
docker build -t developer-agent:local -f k8s/development-team/developer/Dockerfile .
# No deployment, trocar image: para developer-agent:local (ou imagem do registry).
```

Para integrar OpenCode no pod: adicionar no Dockerfile a instalação do OpenCode (pip, COPY de build ou imagem base que já inclua OpenCode), conforme documentação do ecossistema OpenCode. Ver [33-opencode-controller.md](../33-opencode-controller.md).

## Referências

- [02-agentes.md](../02-agentes.md) (Agente Developer)
- [33-opencode-controller.md](../33-opencode-controller.md)
- [04-infraestrutura.md](../04-infraestrutura.md)
