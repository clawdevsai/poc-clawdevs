---
description: Regras de arquitetura e orquestração baseada em Redis Streams para o ClawDevs.
---
# 🏗️ Arquitetura e Orquestração (Redis Ops)

- **Redis Streams é a Lei:** Toda comunicação entre agentes é assíncrona via Redis Streams. Agentes são consumidores de eventos puros.
- **Idempotência Obrigatória:** Consumidores NUNCA devem enviar `ACK` ao Redis antes de o trabalho estar 100% gravado em disco (NVMe). Em caso de queda ou restart brusco (ex: pausa térmica), a tarefa deve ser re-processável sem duplicidade ou efeitos colaterais.
- **Orquestração na Borda:** Lógicas de controle complexas (Token Bucket, Truncamento de Contexto, VFM) pertencem ao `Gateway` ou `Orquestrador`. O código do agente deve focar na sua especialidade técnica.
- **Event-Driven Routing:** Utilize metadados e tags para roteamento inteligente. Diferencie explicitamente eventos que podem rodar localmente (`tier: local`) dos que exigem nuvem (`tier: cloud`).
- **Desacoplamento Cognitivo:** Um agente não deve saber a complexidade interna do outro. A interface de contrato é o payload do evento no Redis.
