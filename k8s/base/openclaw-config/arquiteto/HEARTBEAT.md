# HEARTBEAT.md - Arquiteto

A cada 5 minutos (ou conforme configurado):
1. Sessões ativas (`sessions_list`):
   - Se sessões com PO > 2: alertar PO.
   - Se sessão inativa > 1h: fechar automaticamente.
2. Tarefas pendentes:
   - Tasks sem NFR ou Security/Observabilidade: escalar ao PO.
   - ADR pendente de aprovação > 48h: notificar PO.
3. Research monitor:
   - Se timer > 2h: abortar research, aplicar `Default/Proven`, logar `research_timeout`.
   - Se `internet_search` > 30 queries/hora: aplicar throttle.
4. GitHub health:
   - Se falhas > 5% nas últimas 10 operações: alertar PO e usar fallback por arquivo.
5. Pipeline docs/issue:
   - Se existir documento novo de CEO/PO/Arquiteto sem commit em `implementation/docs`: alertar PO.
   - Se issue criada sem commit prévio de docs: marcar não-conforme e escalar PO.
   - Se sessão finalizada sem pasta `session_finished/<session_id>`: marcar não-conforme e corrigir.
5. Anomalias de arquivo:
   - Leitura/escrita fora de `/data/openclaw/backlog`: bloquear, logar, notificar PO.
6. Monitoramento do ciclo Dev-QA:
   - Issues com label `tests` sem pickup pelo QA_Engineer > 2h: notificar QA_Engineer.
   - QA_Engineer reportou 3 retries em alguma issue: escalar ao PO com histórico.
7. Monitoramento de pipelines CI/CD:
   - Issues com label `devops` sem pickup pelo DevOps_SRE > 1h: notificar DevOps_SRE.
   - Falhas repetidas de CI/CD (> 3x no mesmo PR): delegar ao DevOps_SRE.
8. Se ocioso > 20 minutos: reportar `standby` (sem fechar sessão).
