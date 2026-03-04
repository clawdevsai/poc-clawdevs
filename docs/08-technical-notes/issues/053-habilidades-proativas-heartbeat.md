# [team-devs-ai] Habilidades proativas: antecipação, heartbeat, ADL/VFM, persistência+FinOps

**Fase:** 5 — Self-improvement e memória  
**Labels:** proactive, agents

## Descrição

Implementar os três pilares: Proativo (antecipar necessidades, reverse prompting, check-ins úteis), Persistente (WAL, Working Buffer, recuperação), Autoaprimoramento (self-healing, resourcefulness, ADL/VFM **quantitativos**). Heartbeat periódico para integridade comportamental; crons autônomo vs promptado com guardrails. **Persistência** acoplada a **diversidade de ferramenta** e ao **Gateway FinOps** (evitar loops que esgotam orçamento e GPU).

## Critérios de aceite

- [x] Proativo: diretrizes para "o que ajudaria o Diretor?" e reverse prompting; guardrail (nada para fora sem aprovação). **Ref:** [habilidades-proativas-heartbeat-implementacao.md](../agents-devs/habilidades-proativas-heartbeat-implementacao.md) §1, [13-habilidades-proativas.md](../13-habilidades-proativas.md) §1.
- [x] Persistente: integrado com WAL e Working Buffer (051) e memória Elite (052). **Ref:** [habilidades-proativas-heartbeat-implementacao.md](../agents-devs/habilidades-proativas-heartbeat-implementacao.md) §2, [protocolo-wal-working-buffer.md](../agents-devs/protocolo-wal-working-buffer.md), [memoria-elite-seis-camadas-implementacao.md](../agents-devs/memoria-elite-seis-camadas-implementacao.md).
- [x] **Resourcefulness com diversidade obrigatória:** mesma ferramenta falha 2x consecutivas pelo mesmo motivo → orquestrador bloqueia ferramenta no escopo da tarefa; agente forçado a mudar vetor. **Ref:** [habilidades-proativas-heartbeat-implementacao.md](../agents-devs/habilidades-proativas-heartbeat-implementacao.md) §3, [06-operacoes.md](../06-operacoes.md), [13-habilidades-proativas.md](../13-habilidades-proativas.md) §3.
- [x] **Persistência ↔ FinOps:** contador de tentativas integrado ao Gateway FinOps (custo × tentativa no pre-flight); ao atingir gatilho, orquestrador interrompe tarefa, devolve ao backlog do PO e libera travas. **Ref:** [06-operacoes.md](../06-operacoes.md) "Persistência acoplada ao FinOps", [habilidades-proativas-heartbeat-implementacao.md](../agents-devs/habilidades-proativas-heartbeat-implementacao.md) §4, [10-self-improvement-agentes.md](../10-self-improvement-agentes.md).
- [x] Autoaprimoramento: verificação antes de reportar "pronto" (VBR). **Ref:** [13-habilidades-proativas.md](../13-habilidades-proativas.md) §3 "Verificar antes de reportar (VBR)", [habilidades-proativas-heartbeat-implementacao.md](../agents-devs/habilidades-proativas-heartbeat-implementacao.md) §5.
- [x] Heartbeat: check-in periódico (ex.: CyberSec verifica padrões de injeção); documentado em 13-habilidades-proativas. **Ref:** [13-habilidades-proativas.md](../13-habilidades-proativas.md) §4 "Heartbeat (checklist periódico)", [habilidades-proativas-heartbeat-implementacao.md](../agents-devs/habilidades-proativas-heartbeat-implementacao.md) §6.
- [x] **ADL/VFM quantitativos:** VFM (fitness function, limite no Gateway; CEO VFM_CEO_score no raciocínio); ADL (auditoria de desvio no microADR por regex). **Ref:** [habilidades-proativas-heartbeat-implementacao.md](../agents-devs/habilidades-proativas-heartbeat-implementacao.md) §7, [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md), [05-seguranca-e-etica.md](../05-seguranca-e-etica.md), [microadr_generate.py](../../scripts/microadr_generate.py).
- [x] Checklist de migração de ferramentas (quando adicionar nova ferramenta) documentado. **Ref:** [13-habilidades-proativas.md](../13-habilidades-proativas.md) §3 "Checklist de migração de ferramentas", [habilidades-proativas-heartbeat-implementacao.md](../agents-devs/habilidades-proativas-heartbeat-implementacao.md) §8.

## Referências

- [13-habilidades-proativas.md](../13-habilidades-proativas.md)
- [06-operacoes.md](../06-operacoes.md) (Diversidade de ferramenta, persistência+FinOps)
- [10-self-improvement-agentes.md](../10-self-improvement-agentes.md)
