# Kill switch (Q-Suite) e convenções Redis (Fase 2 — 027)

Mecanismo para **pausar** agentes locais e **checkpoint** em caso de risco (temperatura GPU, segurança, custo). Os consumidores (slot revisão, developer, etc.) respeitam a chave **cluster:pause_consumption** (1 = pausar). Ref: [06-operacoes.md](06-operacoes.md), [02-agentes.md](02-agentes.md) (DevOps), [scripts/acefalo_redis.py](../scripts/acefalo_redis.py).

## Chaves Redis

| Chave | Uso |
|-------|-----|
| **cluster:pause_consumption** | `1` = consumidores devem pausar (não consumir fila GPU); `0` = retomar. Usado por contingência acéfalo (124) e por **kill switch térmico (82°C)**. |
| **cluster:contingency_acefalo** | Espelho da pausa (1/0) para auditoria. |
| **orchestration:thermal_80_triggered** | (Opcional) Marcar que o gatilho 80°C foi acionado (checkpoint em branch efêmera). |
| **orchestration:pause_degradation** | Pausa por orçamento de degradação (017); ver [orchestrator_autonomy.py](../scripts/orchestrator_autonomy.py). |

## Gatilhos térmicos (DevOps)

- **80°C (pré-crítico):** DevOps injeta evento de prioridade máxima no Redis e executa **commit do estado atual em branch efêmera de recuperação** (ex.: `recovery-failsafe-YYYYMMDD-HHMMSS`). **Não** derruba pods ainda; consumidores continuam até concluir a mensagem em curso. Redis: consumidor só envia **ACK após trabalho 100% em disco** (idempotência).
- **82°C:** DevOps chama **set_pause_consumption(True)** (ou `redis-cli SET cluster:pause_consumption 1`). **Q-Suite** — todos os agentes locais pausam (slot, developer, etc. deixam de consumir).

## Recuperação

Quando temperatura voltar a ~65°C (ou após intervenção do Diretor): executar **checkout limpo** e **set_pause_consumption(False)**. Se houver conflitos no índice, orquestrador aciona **Architect (prioridade zero)** na branch de recuperação. Mensagens pendentes na fila são reentregues. Ver [06-operacoes.md](06-operacoes.md) e [acefalo_retomada.py](../scripts/acefalo_retomada.py).

## Acionar kill switch manualmente

```bash
# Pausar consumidores (ex.: emergência)
kubectl exec -n ai-agents deploy/redis -- redis-cli SET cluster:pause_consumption 1

# Retomar
kubectl exec -n ai-agents deploy/redis -- redis-cli SET cluster:pause_consumption 0
```

Ou usar o helper em Python: `from acefalo_redis import set_pause_consumption; set_pause_consumption(True)`.

## Alertas ao Diretor

Disparar alerta **imediato** (ex.: Telegram) para: PR bloqueado por CyberSec, temperatura GPU alta (82°C), custo acima do threshold ($5/dia), violação de segurança. Ref: [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

## Issue

[027-kill-switch-networkpolicy.md](issues/027-kill-switch-networkpolicy.md)
