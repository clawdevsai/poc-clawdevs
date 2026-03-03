# [team-devs-ai] QA como auditor da dívida técnica (após aprovação por omissão cosmética)

**Fase:** 3 — Operações  
**Labels:** ops, qa, technical-debt  
**Depende de:** [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md), [033-aprovacao-omissao-cosmetica.md](033-aprovacao-omissao-cosmetica.md)

## Descrição

Garantir que o agente **QA** atue como **auditor da dívida técnica** nas áreas onde a **aprovação por omissão cosmética** foi acionada (CEO escolheu rota conservadora por ausência de resposta do Diretor no timer de 6 h). Objetivo: testes exploratórios **estritamente** nessas áreas para verificar que a decisão rápida não quebrou integrações futuras.

## Critérios de aceite

- [x] **Registro de áreas com aprovação por omissão cosmética:** orquestrador (ou MEMORY.md) expõe de forma consultável as issues/PRs e **arquivos ou módulos** envolvidos em cada aprovação por omissão cosmética. QA deve poder listar "áreas a auditar". **Ref:** [docs/agents-devs/areas-for-qa-audit.md](../agents-devs/areas-for-qa-audit.md) (gerado por `cosmetic_omission.py write-qa-file`); [MEMORY.md](../agents-devs/MEMORY.md) registra decisões por omissão; QA consulta esses artefatos para priorizar testes exploratórios.
- [x] **Prompt/instrução do QA:** o agente QA recebe lista de áreas (arquivos, módulos ou issues) onde houve aprovação por omissão cosmética e executa **testes exploratórios** priorizando essas áreas. **Ref:** [QA-AUDITOR-INSTRUCOES.md](../agents-devs/QA-AUDITOR-INSTRUCOES.md), [areas-for-qa-audit.md](../agents-devs/areas-for-qa-audit.md); [06-operacoes.md](../06-operacoes.md), [02-agentes.md](../02-agentes.md) (Agente QA).
- [x] **Resultado da auditoria:** QA registra resultado (pass/fail, resumo) em artefato auditável (ex.: comentário no issue, relatório em `docs/agents-devs/` ou digest). **Ref:** Doc 035 e [06-operacoes.md](../06-operacoes.md); integração com digest (036) opcional.
- [ ] Integração com fluxo de digest diário (issue 036) opcional: incluir resumo da auditoria de dívida no digest quando houver itens auditados.

## Referências

- [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md)
- [06-operacoes.md](../06-operacoes.md) (QA auditor da dívida técnica)
- [02-agentes.md](../02-agentes.md) (Agente QA)
