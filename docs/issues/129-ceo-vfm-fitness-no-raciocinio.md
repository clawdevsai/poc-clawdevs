# [team-devs-ai] CEO: fitness function de custo-benefício no raciocínio (VFM antes do Gateway)

**Fase:** 2 — Segurança / Configuração  
**Labels:** finops, ceo, vfm, governance

## Descrição

Integrar **aptidão financeira (fitness function)** diretamente no **raciocínio** do Agente CEO, **antes** de qualquer envio de evento de estratégia ao Gateway. A contenção de custos hoje depende sobretudo de barreiras na infraestrutura (token bucket, $5/dia, degradação por eficiência); esses controles atuam **depois** ou **enquanto** o CEO já decidiu agir — os tokens na nuvem já foram cobrados. Para prevenir desperdício na **raiz cognitiva**, o CEO deve realizar **autoavaliação econômica obrigatória** no system prompt e descartar internamente ideias com custo-benefício negativo, sem nunca enviá-las ao Gateway. As barreiras de infraestrutura permanecem como **rede de proteção redundante**.

## Critérios de aceite

- [ ] **Artefato estruturado (VFM_CEO_score):** Sempre que o CEO formular uma ideia para enviar ao Product Owner via evento de estratégia (ex.: CMD_strategy), o CEO deve **gerar internamente** um artefato estruturado (ex.: `VFM_CEO_score.json`) com estimativa numérica: **custo em tokens de nuvem** vs **horas salvas pelo time local** (ou equivalente).
- [ ] **Descarte interno:** O CEO deve **submeter a própria ideia** a essa métrica no mesmo momento. Se o cálculo indicar **threshold negativo** (custo em tokens maior que o valor estimado), o CEO **descarta o evento internamente** e **não** o envia ao Gateway.
- [ ] **Documentação:** Incluir a regra de aptidão financeira no system prompt / SOUL do CEO. Documentar em [soul/CEO.md](../soul/CEO.md), [13-habilidades-proativas.md](../13-habilidades-proativas.md) (Guardrails VFM), [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) e [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).
- [ ] **Consistência:** Manter referências cruzadas entre "fitness no raciocínio" (CEO) e controles na borda (token bucket, $5/dia) em [06-operacoes.md](../06-operacoes.md) (Governança do CEO), [issues/126-token-bucket-degradacao-eficiencia.md](126-token-bucket-degradacao-eficiencia.md) e [041-truncamento-contexto-finops.md](041-truncamento-contexto-finops.md).

## Referências

- [soul/CEO.md](../soul/CEO.md) (Aptidão financeira)
- [13-habilidades-proativas.md](../13-habilidades-proativas.md) (Guardrails ADL e VFM, VFM no CEO)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Limite VFM, Gateway)
- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Evolução e valor VFM quantitativo)
- [126-token-bucket-degradacao-eficiencia.md](126-token-bucket-degradacao-eficiencia.md) (token bucket e degradação por eficiência)
