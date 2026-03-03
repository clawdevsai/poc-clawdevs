# [team-devs-ai] Digest diário e alertas imediatos (matriz de escalonamento)

**Fase:** 3 — Operações  
**Labels:** ops, autonomy, notifications  
**Depende de:** [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md)

## Descrição

Implementar **digest diário** para notificações não críticas (agrupadas e enviadas de forma assíncrona) e **alerta imediato** (ex.: Telegram) **apenas** para violações de segurança ou estouro do freio de gastos (ex.: $5/dia). Alinhado à matriz de escalonamento: decisões autônomas vs notificação (relatório/digest) vs interrupção (chamada ao Diretor).

## Critérios de aceite

- [ ] **Digest diário:** notificações não críticas (mudança de cronograma, conclusão de tarefas, resumo de strikes, aprovações por omissão cosmética, auditoria QA da dívida técnica quando houver) agrupadas em **um único digest** por dia (ex.: enviado em horário configurável, ex.: 18h ou após fim da janela de trabalho). Canal configurável (Telegram, e-mail ou arquivo em `docs/agents-devs/`). Documentar em [06-operacoes.md](../06-operacoes.md) e [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).
- [ ] **Alerta imediato (exceções):** **Telegram** (ou canal de alerta crítico) acionado **somente** para: (a) violações de segurança (ex.: tag de vulnerabilidade crítica pelo CyberSec, falha de quarentena); (b) estouro do freio de gastos (ex.: $5/dia); (c) freio de mão acionado (degradação). Documentar em 05 e 06.
- [ ] **Matriz de escalonamento referenciada:** documento ou config que defina claramente: autônomo (sem notificação), digest (incluir no diário), interrupção (alerta imediato). Manter alinhado a [01-visao-e-proposta.md](../01-visao-e-proposta.md) e [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md).
- [x] Implementação: script ou job (ex.: CronJob no cluster) que agrega eventos do dia e publica digest; gateway ou adaptador que envia alertas imediatos conforme regras acima. **Ref:** [scripts/digest_daily.py](../../scripts/digest_daily.py), [k8s/orchestrator/cronjob-digest-daily.yaml](../../k8s/orchestrator/cronjob-digest-daily.yaml); alertas imediatos: gateway/orquestrador (consumer Slack, FinOps). Ver [036-digest-implementacao.md](036-digest-implementacao.md).

## Referências

- [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md) (Digest diário, CEO desempate)
- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Alertas de segurança e gastos)
- [06-operacoes.md](../06-operacoes.md) (Matriz, notificações)
