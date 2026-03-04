# [team-devs-ai] Criação de skills (anatomia, processo 6 passos)

**Fase:** 8 — Skills e ambiente  
**Labels:** skills, process

## Descrição

Quando não houver skill no ecossistema e a necessidade for recorrente, criar e evoluir skills. Princípios (concisão, grau de liberdade), anatomia (SKILL.md, scripts/, references/, assets/), processo em 6 passos, padrões de fluxo e saída. Alinhado a FEATURE_REQUESTS e descoberta de skills.

## Critérios de aceite

- [ ] Anatomia documentada: SKILL.md (objetivo, quando usar, passos), scripts/, references/, assets/.
- [ ] Processo em 6 passos documentado (descoberta da necessidade → desenho → implementação → teste → documentação → publicação ou uso interno).
- [ ] Padrões de fluxo e saída (ex.: saída em markdown, códigos de retorno) documentados.
- [ ] Integração com .learnings/FEATURE_REQUESTS.md: necessidades recorrentes podem virar skill.
- [ ] Quem pode criar/publicar (Developer, DevOps, etc.) e guardrails (Zero Trust, revisão) documentados.

## Referências

- [29-criacao-de-skills.md](../../05-tools-and-skills/29-criacao-de-skills.md)

## Verificação (Fase 8)

- Anatomia e processo em 6 passos: [29-criacao-de-skills.md](../../05-tools-and-skills/29-criacao-de-skills.md).
- Integração com .learnings/FEATURE_REQUESTS.md: doc 29 tem seção "Integração com .learnings/FEATURE_REQUESTS.md" e relação com [10-self-improvement-agentes.md](../../03-agents/10-self-improvement-agentes.md).
- Quem pode criar/publicar e guardrails: tabela "Quem pode usar" em 29 e referência a 19 (Zero Trust, aprovação).
- Referência em SOUL: agentes em [soul/](../../03-agents/soul/) referenciam criação de skills (29) quando recorrente.
