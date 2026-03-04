# [team-devs-ai] SOUL — identidade e prompts de personalidade por agente

**Fase:** 1 — Agentes  
**Labels:** agents, prompts, soul

## Descrição

Criar e integrar os arquivos SOUL (alma, tom, valores, frase de efeito, limites) de cada agente como base para system prompts no OpenClaw. Um arquivo por agente em `soul/` (ex.: CEO.md, PO.md, Developer.md).

## Critérios de aceite

- [ ] Arquivo SOUL para cada um dos 9 agentes (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA).
- [ ] Cada SOUL contém: tom, diretriz resumida, frase de efeito, limites (o que NUNCA fazer).
- [ ] Integração com OpenClaw: system prompt do agente carrega o conteúdo do SOUL correspondente.
- [ ] Documentação ou README em soul/ explicando o uso.

## Referências

- [02-agentes.md](../02-agentes.md) (Prompts de personalidade)
- [soul/](../soul/) (README, CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA)
