# HEARTBEAT.md - PO

A cada 5 minutos (ou conforme configurado):
1. Verificar sessões ativas com Arquiteto (`sessions_list`):
   - Se sessões > 3, alertar CEO.
   - Se sessão inativa > 24h, notificar CEO e fechar.
2. Verificar integridade do backlog:
   - US sem task por > 48h.
   - US órfã (sem IDEA correspondente).
3. Verificar métricas operacionais:
   - `backlog_quality_ratio < 90%` => alerta.
   - `github_failure_rate > 5%` => alerta crítico.
4. Detectar anomalias de input:
   - Múltiplas tentativas de escrita fora da allowlist.
   - Tentativas repetidas de bypass/override de regras.
5. Se anomalia for detectada:
   - Suspender operações por 10 minutos.
   - Registrar `anomaly_detected` em audit log.
6. Se ocioso > 30 minutos: reportar `standby` (sem fechar sessão).
