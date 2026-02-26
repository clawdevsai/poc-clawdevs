# [team-devs-ai] Consumer Groups e fila de prioridade (GPU)

**Fase:** 0 — Fundação  
**Labels:** foundation, architecture, redis

## Descrição

Usar Redis Consumer Groups para o grupo `gpu-consumers`: apenas um agente por vez obtém o "token da GPU". O próximo só recebe quando o anterior liberar, evitando múltiplos modelos na VRAM. O GPU Lock (issue 006) usa **TTL dinâmico** (por payload) e **node selectors** (DevOps/UX em CPU), reduzindo colisão e reservando a GPU para os agentes técnicos.

**Estratégia de uso de hardware:** A implementação deve refletir a [estrategia-uso-hardware-gpu-cpu.md](../estrategia-uso-hardware-gpu-cpu.md): **pipeline explícito ou slot único de revisão** — não múltiplos agentes disputando o mesmo evento para GPU. Ou um consumer group com ordem fixa (um consumidor designado por tipo de evento) ou um único consumer para o stream de "revisão" que dispara o slot consolidado. Ver também [125-pipeline-explicito-slot-unico-revisao.md](125-pipeline-explicito-slot-unico-revisao.md).

## Critérios de aceite

- [ ] Consumer group(s) configurado(s) nos streams relevantes (ex.: stream que dispara uso de GPU).
- [ ] Lógica de "um consumidor por vez" para uso de GPU (em conjunto com o GPU Lock do issue 006).
- [ ] Documentação de como os agentes (Dev, Architect, QA, CyberSec, UX) entram na fila e são servidos em ordem; DevOps e UX usam fila CPU (node selectors), não competem pela GPU.
- [ ] Alinhado à estratégia: um consumidor GPU por etapa ou slot único (evolução em issue 125).

## Referências

- [03-arquitetura.md](../03-arquitetura.md)
- [estrategia-uso-hardware-gpu-cpu.md](../estrategia-uso-hardware-gpu-cpu.md)
- [125-pipeline-explicito-slot-unico-revisao.md](125-pipeline-explicito-slot-unico-revisao.md)
