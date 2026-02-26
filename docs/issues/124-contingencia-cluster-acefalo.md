# [team-devs-ai] Contingência: cluster acéfalo (queda de conectividade CEO/PO na nuvem)

**Fase:** 0 — Fundação / Operações  
**Labels:** resilience, operations, contingency

## Descrição

Implementar o **protocolo de fallback 100% local e determinístico** quando CEO e PO estão na nuvem e a **internet cai**: o fluxo estratégico para, mas os agentes locais não podem continuar consumindo a fila do Redis sem novo comando — risco de esgotar a GPU em tarefas desalinhadas e corromper o estado. A detecção, a ação e a **retomada** devem ser **automáticas**; **nenhum comando manual** do Diretor para destravar após cluster acéfalo (autonomia nível 4). Especificação completa em [06-operacoes.md](../06-operacoes.md) (seção *Contingência: cluster acéfalo*).

## Critérios de aceite

- [ ] **Heartbeat / detecção no Redis local:** Orquestrador (ou componente de borda) monitora o Redis; se **nenhum comando com tag de estratégia do CEO** for recebido por um **time-out configurável** (ex.: **5 minutos**), considerar "nuvem inacessível". O valor do time-out deve ser configurável (variável de ambiente ou chave no config JSON).
- [ ] **Quem age:** O **DevOps local** é acionado (via evento de prioridade máxima no Redis) quando o time-out estoura. Detecção é automática (sem bater em LLM).
- [ ] **Ação imediata ao estourar o time-out:** DevOps **não** usa git stash. DevOps: (1) **executa commit do estado atual** (quebrado ou não) em **branch dedicada efêmera** (ex.: `recovery-failsafe-YYYYMMDD-HHMMSS`), isolando o estado de forma rastreável; (2) **persiste o estado da fila do Redis** no banco vetorial **LanceDB**; (3) **pausa instantaneamente** o consumo da fila que disputa o lock de GPU (agentes locais deixam de consumir novos eventos até a retomada). Mesma mecânica aplica-se ao **checkpoint de pausa térmica 80°C** — ver [06-operacoes.md](../06-operacoes.md) e [027-kill-switch-networkpolicy.md](027-kill-switch-networkpolicy.md).
- [ ] **Health check contínuo:** Durante a pausa, orquestrador executa **health check** (ping em endpoints, ex.: API Gemini, serviços de autenticação) a cada **5 minutos**, **sem consumir tokens** (apenas teste de rede).
- [ ] **Retomada automática:** Quando a conectividade estiver estável por **3 ciclos consecutivos** (evitar flapping), orquestrador **acorda automaticamente** o DevOps e executa o script de retomada: **checkout limpo** (volta à branch de trabalho principal a partir da branch efêmera). Se houver **divergência no índice** ou conflitos na branch de recuperação, orquestrador aciona **Architect (tarefa prioridade zero)** para inspecionar e resolver conflito na branch de recuperação; se a resolução ficar dentro do limite de 5 strikes, restaura estado da fila a partir do LanceDB e **retoma o consumo** da fila automaticamente. **Nenhuma intervenção humana** para destravar.
- [ ] **Notificação assíncrona ao Diretor:** Orquestrador envia notificação **assíncrona** (Telegram/Slack ou digest diário) ao Diretor com: (a) que a contingência foi acionada, (b) **tempo de inatividade**, (c) confirmação de que a **retomada automática** foi concluída com sucesso (ou que houve necessidade de Architect e o resultado). O Diretor **não** é bloqueio ativo.
- [ ] Documentação em [06-operacoes.md](../06-operacoes.md), [03-arquitetura.md](../03-arquitetura.md) e [04-infraestrutura.md](../04-infraestrutura.md) reflete o protocolo (já atualizada; validar consistência).

## Referências

- [06-operacoes.md](../06-operacoes.md) (seção *Contingência: cluster acéfalo*)
- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (riscos residuais)
- [03-arquitetura.md](../03-arquitetura.md) (Blackboard e resiliência)
- [04-infraestrutura.md](../04-infraestrutura.md) (tabela de riscos)
- [123-falhas-riscos-fracasso-projeto.md](123-falhas-riscos-fracasso-projeto.md) (risco 1)
