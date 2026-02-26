# [team-devs-ai] Pipeline explícito GPU e slot único de revisão

**Fase:** 0 — Fundação (evolução da 007)  
**Labels:** foundation, architecture, redis, gpu

## Descrição

Implementar **pipeline explícito** e **slot único de revisão** conforme a [estrategia-uso-hardware-gpu-cpu.md](../estrategia-uso-hardware-gpu-cpu.md): em vez de Architect, QA, CyberSec, UX e DBA acordarem todos ao evento `code:ready` e disputarem o GPU Lock, um único consumidor/job "Revisão pós-Dev" é acionado por `code:ready`, adquire o GPU Lock **uma vez**, carrega um modelo (ex.: Llama 3 8B) e executa em sequência interna as etapas Architect, QA, CyberSec e DBA (e opcionalmente UX), gerando todos os pareceres em uma janela; ao final libera o lock. Maximiza utilização da GPU (uma carga de modelo por ciclo de revisão) e evita desperdício de múltiplos pods acordando.

## Critérios de aceite

- [ ] Evento `code:ready` aciona **um único** consumidor/job "Revisão pós-Dev" (não múltiplos pods Architect, QA, CyberSec, UX, DBA disputando o lock).
- [ ] O slot adquire o GPU Lock uma vez, carrega um modelo (ex.: Llama 3 8B) e executa Architect, QA, CyberSec e DBA em sequência interna sem liberar o lock entre etapas.
- [ ] Hard timeout no Kubernetes cobre a duração total do slot (ex.: 300 s se necessário), documentado no deployment.
- [ ] Integração com Consumer Groups (issue 007) e GPU Lock (issue 006); alinhado à [estrategia-uso-hardware-gpu-cpu.md](../estrategia-uso-hardware-gpu-cpu.md) e à [122-balanceamento-dinamico-gpu-cpu.md](122-balanceamento-dinamico-gpu-cpu.md).

## Referências

- [estrategia-uso-hardware-gpu-cpu.md](../estrategia-uso-hardware-gpu-cpu.md)
- [03-arquitetura.md](../03-arquitetura.md)
- [04-infraestrutura.md](../04-infraestrutura.md)
- [06-operacoes.md](../06-operacoes.md)
- [007-consumer-groups-fila-prioridade.md](007-consumer-groups-fila-prioridade.md)
- [006-gpu-lock-script.md](006-gpu-lock-script.md)
- [122-balanceamento-dinamico-gpu-cpu.md](122-balanceamento-dinamico-gpu-cpu.md)
