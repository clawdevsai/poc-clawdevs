# 🚩 war-room — Dashboard de controle, métricas e caos

**Objetivo:** Monitorar a saúde do enxame, visualizar o orçamento de degradação, gerenciar incidentes (Chaos Engineering) e visualizar métricas de FinOps em tempo real.  
**Quando usar:** Para auditoria de sprint, resposta a incidentes graves ou revisão de performance de agentes.  
**Referência:** `docs/120-war-room-dashboard.md`

---

## ─── 1. Métricas Críticas (War Room Dashboard) ─────────────

A visualização deve focar no "Semáforo" de saúde:

| Métrica | Bom (Verde) | Atenção (Amarelo) | Crítico (Vermelho) |
|---------|------------|-------------------|-------------------|
| **Custo Diário** | < $2.00 | $2.00 - $4.00 | > $5.00 (Brake) |
| **Razão CEO/PO** | > 0.50 | 0.30 - 0.50 | < 0.30 (Downgrade) |
| **Drift rejected loop** | 0 - 1 | 2 | 3+ (Circuit Breaker) |
| **Memory usage** | < 16GB | 16GB - 24GB | > 28GB (OOM Risk) |
| **GPU Lock Wait** | < 2 min | 2 - 10 min | > 10 min (Deadlock?) |

---

## ─── 2. Chaos Engineering para IA ─────────────────────────

O DevOps pode introduzir falhas controladas para testar a resiliência do enxame.

### Experimentos de Caos:
1. **Cloud Downtime:** Desabilitar `CEO_CLOUD_MODEL` e forçar `local_phi3` em todo o enxame.
2. **GPU Starvation:** Bloquear o GPU Lock propositalmente por 15 minutos e observar o HeadlessClusterWatchdog.
3. **Context Limit:** Reduzir `GATEWAY_MAX_TOKENS` para 1000 e verificar se os agentes conseguem operar via sumarização agressiva.
4. **Latency Injection:** Adicionar delays artificiais nas chamadas ao Redis para testar timeouts.

---

## ─── 3. Resposta a Incidentes (War Room Mode) ─────────────

Ao detectar falha crítica (5º Strike ou Emergency Brake):

1. **Lockdown:** O Orchestrator Gateway congela todos os novos eventos.
2. **Evidence Collection:** Captura logs de todos os agentes nos últimos 10 minutos.
3. **State Mirroring:** Salva o dump do Redis e do LanceDB para análise pós-mortem.
4. **Escalation:** Notifica o Diretor via Telegram com o "Relatório de Degradação Automático".

---

## ─── 4. Auditoria de Sprint ─────────────────────────────

Uso das ferramentas `gh api` e `memory/cold/` para gerar o relatório final:
- Total de Issues concluídas vs falhadas.
- Economia gerada pelo FreeRide/Local-GPU vs estimativa Cloud.
- Principais "Learnings" recorrentes que viraram skills.
- Pontuação de "Escrita Humanizada" média (auditoria aleatória).

---

## Uso por agente

| Agente | Operação |
|--------|----------|
| **DevOps** | Executa experimentos de caos e monitora infra. |
| **CyberSec** | Audita acessos e tentativas de quebra de sandbox durante o caos. |
| **Architect** | Analisa os gargalos de performance detectados no dashboard. |
| **CEO/PO** | Revisam métricas de custo e produtividade. |
