# HEARTBEAT.md

A cada ciclo de heartbeat:
1. Verificar backlog/status e alertas ativos.
2. Confirmar se ha bloqueios de prazo, custo, seguranca ou dependencia.
3. Reforcar delegacao para PO quando houver trabalho pendente.
4. Se nao houver acao necessaria, responder HEARTBEAT_OK.

Sinais de atencao imediata:
- risco critico de seguranca/compliance
- custo acima do limite acordado
- atraso com impacto direto no objetivo de negocio
- perda de rastreabilidade entre brief, US e task
- incidente P0 reportado pelo DevOps_SRE (responder imediatamente, nao aguardar proximo ciclo)

Loop producao->produto:
- verificar se existe PROD_METRICS-YYYY-WXX.md novo em /data/openclaw/backlog/status/
- se existir: ler metricas e considerar na priorizacao do proximo BRIEF
- se incidente P0 aberto > 1h sem resolucao: escalar ao Diretor
