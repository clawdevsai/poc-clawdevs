# 📉 Matriz de Riscos e Falhas do Projeto

Este documento detalha os cenários de risco que podem levar ao fracasso do projeto ClawDevs e as mitigações implementadas. Todo agente (especialmente CEO, Architect e CyberSec) deve consultar esta matriz ao tomar decisões de alto impacto.

---

## ─── 1. Mapa de Riscos Críticos ─────────────────────────────

| ID | Risco | Impacto | Probabilidade | Mitigação Principal |
|----|-------|---------|---------------|-----------------------|
| **R01** | Cluster Acéfalo (CEO/Cloud Offline) | Crítico | Média | `HeadlessClusterWatchdog` + Branch efêmera de recuperação + Auto-resume. |
| **R02** | Estouro de Orçamento (FinOps) | Alto | Alta | `TokenBucket` + `EfficiencyDegradation` + Freio de $5/dia. |
| **R03** | Alucinação de Escopo (PO/RAG) | Médio | Média | `DraftRejectedCircuitBreaker` + RAG Health Check determinístico. |
| **R04** | Vazamento de Segredos (Secrets) | Crítico | Baixa | `gitleaks` no CI + Zero Trust (Secrets apenas no K8s). |
| **R05** | Deadlock GPU/Local Saturação | Alto | Média | `FreeRide` (Fallback hierárquico Nuvem → GPU → CPU). |
| **R06** | Degradação da "Alma" (Escrita IA) | Baixo | Alta | `governance/escrita-humanizada.md` + Revisão aleatória. |

---

## ─── 2. Cenários de "Fracasso do Projeto" ─────────────────

O projeto é considerado em falha se:

1. **Inércia Total:** O orçamento de degradação é estourado em 3 sprints consecutivos sem solução humana.
2. **Deriva Técnica:** O código gerado torna-se imantenível (Architect rejeita > 50% dos PRs por falha estrutural).
3. **Comprometimento de Segurança:** Um segredo crítico é exposto publicamente ou um agente escapa do sandbox.
4. **Custo Inviável:** O ROI (Value-for-Money) calculado pelo CEO torna-se negativo por mais de 7 dias.

---

## ─── 3. Protocolo de Escalação (Human-in-the-Loop) ─────────

Se um risco crítico se materializa:

1. **Detecção Automática:** O `Orchestrator Gateway` ou `Watcher` detecta o limite.
2. **Pausa de Segurança:** A esteira é bloqueada (`emergency_brake_active`).
3. **Relatório Pós-Morte:** Um arquivo `memory/cold/POST-MORTEM-<TS>.md` é gerado.
4. **Alerta Telegram:** Notificação urgente ao Diretor Humano.
5. **Comando Humano:** A retomada **EXIGE** o comando `./scripts/unblock-degradation.sh` após revisão humana.

---

## ─── 4. Mitigações de Sobrevivência (Fail-Safe) ──────────

- **Context Overload:** Atuamos com janelas deslizantes e `ContextTruncator`. "Memória infinita" é proibida.
- **Skill Loops:** Cada skill chamada por tarefa tem um `max_calls=3` e `timeout=60s`.
- **RAG Integrity:** Se os critérios de aceite forem perdidos no truncamento, o PO tem o Payload Duplo (criteria intacto).

---

## 📝 Declaração de Compromisso

Os agentes ClawDevs comprometem-se a PRIORIZAR a estabilidade e a segurança sobre a velocidade de entrega. Em caso de dúvida sobre a integridade do sistema, o agente deve **Parar e Escalar**.
