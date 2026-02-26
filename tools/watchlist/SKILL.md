# 📊 watchlist — Monitoramento, alertas e simulação

**Objetivo:** Manter acompanhamento de dados (Preços, Status de CI, PRs, métricas), configurar alertas por threshold ou tempo (cron), e realizar simulações locais (paper trading/backtesting).  
**Quando usar:** Quando um agente precisa reagir a mudanças de estado ou prever impactos antes de executar.  
**Referência:** `docs/26-dados-watchlist-alertas-simulacao.md`

---

## ─── 1. Watchlist (Acompanhamento) ───────────────────────

A watchlist armazena itens que precisam de consulta recorrente.

```python
# Exemplo de estrutura de Watchlist no Redis
# key: watchlist:agent_name
# value: [ { "source": "github_pr", "id": "42", "last_status": "open" }, ... ]
```

### Agentes:
- **PO:** Monitora status de PRs e Issues.
- **DevOps:** Monitora estabilidade do cluster e orçamento de degradação.
- **CyberSec:** Monitora alertas de segurança e novos commits.

---

## ─── 2. Alertas (Threshold & Cron) ──────────────────────────

### Alerta por Threshold (Gatilho)
Reagir quando um valor ultrapassa um limite.

```python
# scripts/alert_check.py
def check_threshold(current_value, limit, alert_msg):
    if current_value >= limit:
        # Enviar alerta via Telegram (conforme scripts/auto-update.sh logic)
        send_telegram(f"⚠️ **ALERTA**: {alert_msg} ({current_value} >= {limit})")
```

### Alerta por Cron (Digest)
Resumo em horários pré-definidos.

```bash
# Exemplo: Digest diário do PO às 09:00
0 9 * * 1-5 python scripts/po_digest.py
```

---

## ─── 3. Simulação (Paper Trailing) ─────────────────────────

Antes de executar uma mudança de alto risco, os agentes devem simular localmente.

### Quando simular:
- **Developer:** Testar mudança de versão de biblioteca em sandbox isolado.
- **Architect:** Simular impacto de nova arquitetura no custo de tokens.
- **DevOps:** Simular escalonamento de pods antes de aplicar HPA.

### Como simular:
1. **Ambiente Isolado:** Use o pod `sandbox` (namespace `ai-agents-quarantine`).
2. **Dados de Teste:** Use `memory/cold/` para carregar cenários passados.
3. **Validação:** Obtenha um "Success Score" antes de propor ao Diretor.

---

## ─── 4. Calendário e Prazos ────────────────────────────────

O enxame deve ter consciência de tempo e deadliness.

| Artefato | Localização |
|----------|-------------|
| **Sprint Goals** | `docs/backlog/SPRINT.md` |
| **Deadlines** | `docs/backlog/MILESTONES.md` |
| **Recorrências** | `k8s/devops/cronjob-*.yaml` |

---

## Uso por agente

| Agente | Exemplo de Uso |
|--------|----------------|
| **CEO** | Watchlist de orçamento diário; Alerta se custo > $4.00. |
| **PO** | Alerta se Issue está em `strike 3` de draft; Digest de PRs abertos. |
| **DevOps** | Watchlist de erros 500 no gateway; Reinício auto se heartbeat falhar. |
| **QA** | Watchlist de falhas intermitentes (flaky tests). |

---

## Boas práticas

- **Evitar ruído:** Não configure alertas para eventos triviais. Use thresholds inteligentes.
- **Canal de Saída:** Por padrão, use logs estruturados. Alertas críticos vão para o Telegram do Diretor.
- **Persistência:** Watchlists devem ser persistidas no Redis ou LanceDB para sobreviver a restarts de pod.
- **Simulação obrigatória:** Mudanças que alteram o `agents-config.yaml` devem passar por simulação.
