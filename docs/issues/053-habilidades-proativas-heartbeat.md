# [team-devs-ai] Habilidades proativas: antecipação, heartbeat, ADL/VFM, persistência+FinOps

**Fase:** 5 — Self-improvement e memória  
**Labels:** proactive, agents

## Descrição

Implementar os três pilares: Proativo (antecipar necessidades, reverse prompting, check-ins úteis), Persistente (WAL, Working Buffer, recuperação), Autoaprimoramento (self-healing, resourcefulness, ADL/VFM **quantitativos**). Heartbeat periódico para integridade comportamental; crons autônomo vs promptado com guardrails. **Persistência** acoplada a **diversidade de ferramenta** e ao **Gateway FinOps** (evitar loops que esgotam orçamento e GPU).

## Critérios de aceite

- [ ] Proativo: diretrizes para "o que ajudaria o Diretor?" e reverse prompting; guardrail (nada para fora sem aprovação).
- [ ] Persistente: integrado com WAL e Working Buffer (issue 051) e memória Elite (052).
- [ ] **Resourcefulness com diversidade obrigatória:** se mesma ferramenta falhar 2x consecutivas pelo mesmo motivo, orquestrador bloqueia essa ferramenta no escopo da tarefa; agente forçado a mudar vetor (CLI, API, outra skill). Ver [06-operacoes.md](../06-operacoes.md), [13-habilidades-proativas.md](../13-habilidades-proativas.md).
- [ ] **Persistência ↔ FinOps:** contador de tentativas integrado ao Gateway FinOps (custo × número da tentativa no pre-flight); ao atingir gatilho, orquestrador interrompe tarefa, devolve ao backlog do PO e libera travas de hardware. Ver [06-operacoes.md](../06-operacoes.md), [10-self-improvement-agentes.md](../10-self-improvement-agentes.md).
- [ ] Autoaprimoramento: verificação antes de reportar "pronto" (VBR).
- [ ] Heartbeat: check-in periódico (ex.: CyberSec verifica padrões de injeção); documentado em 13-habilidades-proativas.
- [ ] **ADL/VFM quantitativos:** VFM via fitness function (vfmscore.json, limite no Gateway); ADL via auditoria de desvio no microADR com regex (lista negra de justificativas fracas; rejeição em tempo de execução). Ver [13-habilidades-proativas.md](../13-habilidades-proativas.md), [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md), [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).
- [ ] Checklist de migração de ferramentas (quando adicionar nova ferramenta) documentado.

## Referências

- [13-habilidades-proativas.md](../13-habilidades-proativas.md)
- [06-operacoes.md](../06-operacoes.md) (Diversidade de ferramenta, persistência+FinOps)
- [10-self-improvement-agentes.md](../10-self-improvement-agentes.md)
