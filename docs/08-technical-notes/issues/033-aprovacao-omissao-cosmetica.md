# [team-devs-ai] Aprovação por omissão apenas cosmética (timer 6 h)

**Fase:** 3 — Operações  
**Labels:** ops, autonomy, cosmetic  
**Depende de:** [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md), [032-five-strikes-fallback-arbitragem.md](032-five-strikes-fallback-arbitragem.md)

## Descrição

Implementar aprovação por omissão **somente** para impasses **estritamente cosméticos** (diff só CSS, UI isolada ou markdown), com timer duro de **6 h** e regra **determinística** (sem LLM para classificar "baixo risco"). Se o Diretor não responder no prazo, CEO aprova por omissão a rota mais conservadora, destrava a esteira e **registra em MEMORY.md**. Impasses de código lógico/backend **não** usam timer: orquestrador aplica **5 strikes** e a issue volta ao backlog do PO (ver 032).

## Critérios de aceite

- [ ] **Definição determinística de "cosmético":** regra aplicável sem LLM — ex.: diff restrito a extensões `.css`, `.scss`, `.md`, `.html` (apenas trechos sem lógica), ou heurística de linhas alteradas (ex.: só arquivos de assets). Documentar em [06-operacoes.md](../06-operacoes.md) e config (ex.: [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md)).
- [ ] **Timer 6 h:** quando o CEO envia alerta de impasse **classificado como cosmético**, inicia timer de 6 h. Se o Diretor não responder (sem comando explícito no canal configurado), CEO aprova por omissão a **rota mais conservadora** (ex.: manter versão atual, sem merge do PR disputado), destrava esteira e **registra em MEMORY.md** (data, issue, decisão, arquivos envolvidos). Diretor audita pelo histórico.
- [ ] **Impasse lógico/backend:** não usar timer; orquestrador aplica fluxo **five strikes** (issue 032) e a issue **volta ao backlog do PO**. PO + Architect definem solução; tarefa retorna ao desenvolvimento.
- [ ] **MEMORY.md:** formato e local (ex.: `docs/agents-devs/MEMORY.md` ou repositório) definido; cada aprovação por omissão cosmética gera entrada auditável. Referência em [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) se existir.
- [ ] Contagem de aprovações por omissão cosmética integrada ao **orçamento de degradação** (issue 034): entram na métrica acumulativa que pode acionar loop de consenso e freio de mão.

## Referências

- [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md)
- [06-operacoes.md](../06-operacoes.md) (Aprovação por omissão cosmética)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Configuração timer e critérios)
