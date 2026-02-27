# [team-devs-ai] Kill switch (Q-Suite) e NetworkPolicy

**Fase:** 2 — Segurança  
**Labels:** security, ci-cd, k8s

## Descrição

Pipeline de CI/CD com Q-Suite (kill switch de segurança): capacidade de parar ou reverter ações do enxame em caso de risco. NetworkPolicy no Kubernetes para restringir tráfego entre pods e egress; alerta ao Diretor via Telegram em eventos críticos.

## Critérios de aceite

- [ ] Q-Suite ou equivalente: mecanismo (ex.: pipeline GitHub Actions, webhook) que permite kill switch (pausar agentes, reverter deploy, bloquear merge).
- [ ] **Gatilho 80°C (pré-crítico):** DevOps injeta evento de prioridade máxima no Redis ordenando **commit do estado atual em branch efêmera de recuperação** (ex.: `recovery-failsafe-<timestamp>`) no repositório de trabalho (checkpoint transacional); **não** derruba pods ainda. **82°C:** Q-Suite pausa todos os agentes locais.
- [ ] **Redis Streams idempotente:** consumidor **não** envia ACK até o trabalho estar **100% concluído em disco**; em pausa brusca a mensagem permanece na fila para reentrega.
- [ ] **Recuperação automática:** quando temperatura voltar a ~65°C, orquestrador acorda pods, executa **checkout limpo**; se houver divergência no índice ou conflitos, **Architect (tarefa prioridade zero)** resolve na branch de recuperação; Redis reentrega tarefa pendente — **sem** fases 1–3 do manual no terminal. Ver [06-operacoes.md](../06-operacoes.md).
- [ ] NetworkPolicy aplicada no namespace do enxame: regras de ingress/egress (ex.: apenas APIs permitidas para pods que precisam de internet).
- [ ] Alerta ao Diretor (ex.: Telegram) em eventos críticos (ex.: PR bloqueado por segurança, temperatura GPU alta, custo acima do threshold).
- [ ] Documentação de como acionar o kill switch e quais eventos disparam alerta.

## Implementação (início Fase 2)

- **Convenções Redis e kill switch:** [27-kill-switch-redis.md](../27-kill-switch-redis.md) — chave **cluster:pause_consumption** (1 = pausar consumidores); gatilho **80°C** = checkpoint em branch efêmera; **82°C** = set pause (Q-Suite). Recuperação: checkout limpo + clear pause; Architect para conflitos.
- **Scripts:** [acefalo_redis.py](../../scripts/acefalo_redis.py) (`set_pause_consumption`, `is_consumption_paused`), [acefalo_retomada.py](../../scripts/acefalo_retomada.py). Consumidores (slot, developer, etc.) já respeitam `is_consumption_paused(r)`.
- **Comando manual:** `redis-cli SET cluster:pause_consumption 1` (pausar) ou `0` (retomar). NetworkPolicy do time técnico: [k8s/development-team/networkpolicy.yaml](../../k8s/development-team/networkpolicy.yaml).

## Referências

- [02-agentes.md](../02-agentes.md) (DevOps: Q-Suite)
- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (kill switch, NetworkPolicy)
- [06-operacoes.md](../06-operacoes.md)
