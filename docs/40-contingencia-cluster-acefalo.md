# Contingência cluster acéfalo (124) — Implementação

Implementação do **protocolo de fallback 100% local** quando CEO/PO estão na nuvem e a internet cai: detecção por heartbeat no Redis, ação imediata (branch efêmera, snapshot da fila, pausa de consumo), health check contínuo e **retomada automática** sem comando humano. Especificação em [06-operacoes.md](06-operacoes.md) (seção *Contingência: cluster acéfalo*) e [issues/124-contingencia-cluster-acefalo.md](issues/124-contingencia-cluster-acefalo.md).

## Chaves Redis

| Chave | Descrição |
|-------|-----------|
| `ceo:last_strategy_ts` | Timestamp do último heartbeat (comando estratégico ou health check externo). Atualizado pelo **heartbeat writer** quando há conectividade. |
| `cluster:pause_consumption` | `1` = consumidores devem pausar (não consumir fila GPU); `0` = retomada. |
| `cluster:contingency_acefalo` | `1` quando contingência está ativa (espelho de pause). |

## Scripts (raiz do repositório)

| Script | Uso |
|--------|-----|
| [scripts/acefalo_redis.py](../scripts/acefalo_redis.py) | Utilitários: heartbeat, pause, export/restore streams para JSON. |
| [scripts/acefalo_heartbeat_writer.py](../scripts/acefalo_heartbeat_writer.py) | Roda junto ao CEO/PO (gateway): a cada `ACEFALO_HEARTBEAT_INTERVAL_SEC` (padrão 60 s) testa `ACEFALO_HEALTH_CHECK_URL`; se OK, atualiza `ceo:last_strategy_ts`. Quando a internet cai, deixa de atualizar. |
| [scripts/acefalo_monitor.py](../scripts/acefalo_monitor.py) | Roda **localmente** (no cluster): a cada minuto verifica se `ceo:last_strategy_ts` está há mais de `ACEFALO_TIMEOUT_MIN` (padrão 5 min) sem atualização; se sim, dispara contingência (branch efêmera, snapshot fila, pausa). Em pausa: health check a cada 5 min; após 3 ciclos consecutivos OK, executa retomada (checkout limpo, clear pausa). |
| [scripts/acefalo_contingency.py](../scripts/acefalo_contingency.py) | Ação imediata: cria branch `recovery-failsafe-YYYYMMDD-HHMMSS` (se `ACEFALO_REPO_PATH` tiver .git), exporta streams para JSON em `ACEFALO_SNAPSHOT_DIR`, define `cluster:pause_consumption=1`. |
| [scripts/acefalo_retomada.py](../scripts/acefalo_retomada.py) | Retomada: checkout limpo para branch principal, opcionalmente restaura fila do último snapshot (`ACEFALO_RESTORE_FROM_SNAPSHOT=1`), limpa pausa. |

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `REDIS_HOST` | `redis-service.ai-agents.svc.cluster.local` | Host do Redis. |
| `REDIS_PORT` | `6379` | Porta do Redis. |
| `ACEFALO_TIMEOUT_MIN` | `5` | Minutos sem heartbeat para considerar cluster acéfalo. |
| `ACEFALO_HEALTH_CHECK_URL` | `https://www.google.com/generate_204` | URL para testar conectividade (sem tokens). |
| `ACEFALO_HEARTBEAT_INTERVAL_SEC` | `60` | Intervalo do heartbeat writer. |
| `ACEFALO_HEALTH_CHECK_INTERVAL_SEC` | `300` | Intervalo do health check durante pausa (5 min). |
| `ACEFALO_STABLE_CYCLES` | `3` | Ciclos consecutivos OK para retomada. |
| `ACEFALO_REPO_PATH` | (vazio) | Caminho do repositório de trabalho para branch efêmera (opcional). |
| `ACEFALO_SNAPSHOT_DIR` | `/tmp/acefalo_snapshot` | Diretório para salvar snapshot da fila (JSON). |
| `ACEFALO_RESTORE_FROM_SNAPSHOT` | `0` | Se `1`, retomada restaura fila do último snapshot. |

## Consumidores e pausa

O slot **Revisão pós-Dev** ([scripts/slot_revisao_pos_dev.py](../scripts/slot_revisao_pos_dev.py)) e qualquer outro consumidor da fila que disputa o GPU Lock devem **respeitar** `cluster:pause_consumption`: se `1`, dormir (ex.: 60 s) e não consumir até a retomada. O script do slot já consulta `acefalo_redis.is_consumption_paused()` no loop.

## Persistência da fila (LanceDB)

A especificação prevê persistência no **LanceDB**. Na Fase 0 a implementação usa **JSON** em disco (`ACEFALO_SNAPSHOT_DIR`) para snapshot e restauração. Em fase posterior (memória Elite / warm store) o LanceDB pode substituir o JSON para o mesmo fim.

## Notificação ao Diretor

O protocolo exige **notificação assíncrona** (Telegram/Slack ou digest) informando que a contingência foi acionada, tempo de inatividade e resultado da retomada. Na implementação atual o monitor registra em log; a integração com Telegram/digest fica para o orquestrador ou um job de notificação (Fase 1).

## Kubernetes (opcional Fase 0)

- **Heartbeat writer:** pode rodar como sidecar ou job no mesmo namespace do gateway OpenClaw (onde há egress); atualiza `ceo:last_strategy_ts` apenas quando o health check externo passar.
- **Monitor:** pode rodar como Deployment no namespace `ai-agents`, com acesso ao Redis e, se desejar, volume para `ACEFALO_SNAPSHOT_DIR` e `ACEFALO_REPO_PATH` (workspace git).

Scripts podem ser montados via ConfigMap (ex.: `make acefalo-configmap`) ou executados fora do cluster com `kubectl port-forward` ao Redis.
