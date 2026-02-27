# Autonomia nível 4 e matriz de escalonamento (017)

Sistema **silencioso por padrão**: CEO filtra o ruído; o Diretor é acionado apenas para decisões estratégicas ou impasses. **Matriz de escalonamento** define o que é autônomo, o que gera notificação (digest) e o que exige interrupção (chamada ao Diretor). Referência: [docs/issues/017-autonomia-nivel-4-matriz-escalonamento.md](issues/017-autonomia-nivel-4-matriz-escalonamento.md).

## Matriz de escalonamento

| Tipo | Exemplos | Ação |
|------|----------|------|
| **Decisões autônomas** | Bibliotecas compatíveis, bugs de UI, queries otimizadas, mudanças cosméticas (CSS, markdown) | Agentes resolvem; sem notificação imediata. |
| **Notificação (digest diário)** | Mudança de cronograma, grandes features, FinOps (gasto próximo do limite), aprovação por omissão cosmética (registro em MEMORY.md) | Agrupado em digest assíncrono; Diretor audita depois. |
| **Interrupção (alerta imediato)** | Mudança radical de escopo, orçamento ($5/dia ou freio), privacidade/segurança crítica, deadlock (5º strike + escalação falhou), violação de segurança | Telegram (ou canal crítico); Diretor deve decidir. |

## CEO como juiz de desempate

Em impasses **puramente técnicos** (Developer vs Architect), o **CEO** pode avaliar pelo **impacto no valor de negócio** e destravar antes de escalar ao Diretor.

- **Regra:** O CEO **não** tem autoridade sobre **segurança**. Se a recusa do Architect tiver **tag de vulnerabilidade crítica (cybersec)**, o CEO **não** pode forçar merge; o impasse escala para o Diretor. Ver [01-visao-e-proposta.md](01-visao-e-proposta.md) e [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md).

## Digest diário e alerta imediato

- **Digest diário:** Notificações não críticas (mudança de cronograma, grandes entregas, FinOps, decisões por omissão cosmética) agrupadas em **um resumo assíncrono** (ex.: fim do dia).
- **Alerta imediato (Telegram):** Apenas para **violações de segurança** ou **estouro do freio de gastos** (ex.: $5/dia). Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

## Five strikes e fallback contextual

- **2º strike:** Orquestrador injeta **prompt de compromisso** no Architect (gerar o código exato que aprovaria o PR).
- **5º strike:** Empacotar contexto e **escalação para arbitragem na nuvem** (modelo superior reescreve). Se falhar, issue **volta ao backlog do PO**; Developer pega próxima tarefa. **Tarefa não se perde:** PO analisa histórico com Architect e tarefa **retorna ao desenvolvimento**. Ver [06-operacoes.md](06-operacoes.md) (seção *Prevenção de deadlock*).

## Aprovação por omissão (apenas cosmético)

- **Timer duro (ex.: 6 h):** Apenas para impasses **estritamente cosméticos** (diff só CSS, UI isolada, markdown). Classificação **determinística** (sem LLM para "baixo risco"). CEO aprova por omissão a rota conservadora, destrava e **registra em MEMORY.md**.
- **Código lógico/backend:** Não usar timer; aplicar **5 strikes** e devolver issue ao backlog do PO. Ver [06-operacoes.md](06-operacoes.md) (seção *Aprovação por omissão*).

## Orçamento de degradação e freio de mão

- **Métrica:** Contagem acumulativa de 5º strike e aprovação por omissão cosmética. Ao atingir **10–15%** das tarefas do sprint na rota de fuga, acionar **loop de consenso automatizado (pré-freio de mão)** — QA + Architect propõem ajuste e testam em uma tarefa crítica.
- **Freio de mão:** Só se o loop falhar; então DevOps dispara alerta e **pausa a esteira**. **Workflow de recuperação:** relatório de degradação, Diretor revisa MEMORY.md e config, **comando explícito de desbloqueio** (ex.: `./scripts/unblock-degradation.sh`) para retomar. Ver [06-operacoes.md](06-operacoes.md) (Orçamento de degradação, Loop de consenso, Workflow de recuperação pós-degradação).

## Implementação de referência (orquestrador 017)

O script [scripts/orchestrator_autonomy.py](../scripts/orchestrator_autonomy.py) implementa a lógica de **orçamento de degradação** e **digest** em modo referência:

- Lê do Redis as chaves `project:v1:orchestrator:five_strikes_count`, `omission_cosmetic_count` e `sprint_task_count`.
- Ao atingir o percentual configurável (ex.: 10–15%, variável `DEGRADATION_THRESHOLD_PCT`), define `orchestration:pause_degradation` e publica em `digest:daily` para notificação.
- Outros componentes (DevOps, gateway) devem respeitar `orchestration:pause_degradation` e acionar o workflow de recuperação; o script de referência não executa o loop de consenso nem o freio de mão — apenas sinaliza.

Variáveis de ambiente: `REDIS_HOST`, `REDIS_PORT`, `KEY_PREFIX_PROJECT`, `DEGRADATION_THRESHOLD_PCT`, `ORCHESTRATOR_INTERVAL_SEC`, `STREAM_DIGEST`.

## Referências

- [01-visao-e-proposta.md](01-visao-e-proposta.md) — Autonomia nível 4, aprovação por omissão.
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Freio $5/dia, alertas.
- [06-operacoes.md](06-operacoes.md) — Five strikes, orçamento degradação, workflow recuperação.
- [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) — FinOps, métricas configuráveis.
