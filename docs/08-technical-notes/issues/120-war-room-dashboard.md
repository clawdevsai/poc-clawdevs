# [team-devs-ai] Dashboard de orquestração (War Room)

**Fase:** 11 — Avançado  
**Labels:** advanced, ui, ops

## Descrição

Interface visual em que cada agente aparece como avatar ativo: estado do CEO (pesquisa em tempo real), Developer (branch em edição), CyberSec (alertas). Objetivo: tornar a automação auditável e visual para o Diretor.

## Critérios de aceite

- [ ] Conceito ou mock do dashboard: visão dos 9 agentes com estado (idle, working, alerta).
- [ ] Informações por agente: pelo menos estado atual e indicador de atividade (ex.: CEO pesquisando, Developer em branch X, CyberSec com N alertas).
- [ ] Fonte de dados: Redis, logs ou API de status dos pods; atualização periódica ou em tempo real.
- [ ] Documentação de uso (para o Diretor) e possíveis próximos passos (alertas, histórico).

## Referências

- [01-visao-e-proposta.md](../../01-core/01-visao-e-proposta.md) (War Room)

## Verificação (Fase 11)

- Conceito e mock: [war-room-dashboard.md](../../07-operations/war-room-dashboard.md); mock estático em [war-room-mock/index.html](../../../war-room-mock/index.html) (9 agentes, estados idle/working/alerta, atividade).
- Fonte de dados: doc § Fontes de dados (Redis, pods K8s, logs, API de status futuro); atualização periódica ou tempo real descrita.
- Documentação de uso: doc § Uso pelo Diretor. Próximos passos: § Próximos passos (alertas, histórico, integração Kanban).
