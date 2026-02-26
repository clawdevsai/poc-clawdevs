# [team-devs-ai] Código de conduta e restrições por agente

**Fase:** 1 — Agentes  
**Labels:** agents, governance

## Descrição

Implementar as restrições e o código de conduta (o que NUNCA fazer) por agente. Garantir que as regras sejam aplicáveis via config, prompts ou guardrails (ex.: Developer não pode fazer merge; CyberSec bloqueia PR com chave exposta). Incluir **guardrails de evolução quantitativos** (VFM por fitness function, ADL por auditoria regex) para que limites de evolução e valor não dependam de justificativa em texto livre.

## Critérios de aceite

- [ ] Regras "nunca fazer" por agente aplicadas (CEO: não escrever código, não aprovar PRs, **não criar tarefas/visão em excesso sem filtrar** — risco de colapso financeiro da API; PO: não mudar requisitos em desenvolvimento exceto sob technical_blocker do Architect; Developer: não merge, não instalar pacotes sem autorização; Architect: não reescrever código; DevOps: não ultrapassar 65% sem comando, zero binários em skills; QA: não consertar bugs; CyberSec: não vazar chaves; UX: não sugerir mudanças pesadas sem Architect).
- [ ] Fluxo Zero Trust referenciado (PARAR → PENSAR → VERIFICAR → PERGUNTAR → AGIR → REGISTRAR) antes de ações externas.
- [ ] Mecanismo de bloqueio ou alerta quando restrição for violada (ex.: tentativa de merge pelo Developer).
- [ ] **VFM quantitativo (fitness function):** Propostas de evolução exigem artefato estruturado (ex.: vfmscore.json) com variáveis para fórmula rígida (ex.: horas_salvas × frequência_mensal − custo_tokens); cálculo e decisão no Gateway/orquestrador; bloqueio na borda se pontuação < threshold configurado. Ver [13-habilidades-proativas.md](../13-habilidades-proativas.md), [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md), [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).
- [ ] **ADL por regex:** MicroADR com seção obrigatória de auditoria de desvio; regex contra lista negra de justificativas fracas ("parece melhor", "intuição sugere", "código mais limpo" sem métrica); rejeição em tempo de execução na máquina local se casar. Ver [13-habilidades-proativas.md](../13-habilidades-proativas.md), [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md).

## Referências

- [02-agentes.md](../02-agentes.md) (Código de conduta)
- [13-habilidades-proativas.md](../13-habilidades-proativas.md) (Guardrails ADL/VFM)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Gateway, microADR, limite VFM)
