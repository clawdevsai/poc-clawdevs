# Fase 1 — Agentes: SOUL, pods e fluxo E2E

Roteiro da **Fase 1** do ClawDevs: definição canônica dos 9 agentes, SOUL (identidade e prompts), pods CEO/PO (nuvem) e técnicos (100% offline), código de conduta e fluxo evento-driven com exemplo E2E (Operação 2FA). Issues **010–019** em [docs/issues/README.md](issues/README.md).

## Escopo (issues 010–019)

| Issue | Título | Entregável |
|-------|--------|------------|
| **010** | Definição canônica dos nove agentes | [02-agentes.md](02-agentes.md); função, restrições, line-up, conflitos. |
| **011** | SOUL — identidade e prompts | Um SOUL por agente em [docs/soul/](soul/); integração com OpenClaw (SOUL.md no workspace ou por agente). |
| **012** | Pods CEO e PO (nuvem) | Deployment management-team com OpenClaw; Telegram; provedores nuvem (secrets). |
| **013** | Pod Developer (OpenCode + Ollama) | Deployment com OpenCode, PVC, GPU Lock; consumo Redis/eventos. |
| **014** | Pods Architect, QA, CyberSec, UX | Deployments ou Jobs event-driven; Ollama + GPU Lock; Redis Streams (ex.: code:ready). |
| **015** | Código de conduta e restrições | Regras "nunca fazer" por agente; [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md); guardrails VFM/ADL (ref.). |
| **016** | E2E Operação 2FA | Cenário documentado; fases (planejamento → fechamento); Redis; riscos. Ver [42-fluxo-e2e-operacao-2fa.md](42-fluxo-e2e-operacao-2fa.md). |
| **017** | Autonomia nível 4 | Matriz de escalonamento, CEO desempate, digest diário, five strikes, orçamento degradação (doc/operacional). |
| **018** | Fluxo evento-driven mínimo (Redis) | Contrato de publicação em streams; script [scripts/publish_event_redis.py](../scripts/publish_event_redis.py); doc [38-redis-streams-estado-global.md](38-redis-streams-estado-global.md) (§2). |
| **019** | Validação management nuvem + line-up | Doc em [37-deploy-fase0-telegram-ceo-ollama.md](37-deploy-fase0-telegram-ceo-ollama.md); line-up abaixo; [validacao-fase1-019.md](issues/validacao-fase1-019.md). |

## Line-up (modelo por agente — Fase 1, issue 019)

Configuração em [k8s/llm-providers-configmap.yaml](../k8s/llm-providers-configmap.yaml) (provedor) e no config do OpenClaw (ID do modelo por agente). Sugestão para Fase 1:

| Agente | Provedor (padrão) | Modelo sugerido (ex.) |
|--------|-------------------|------------------------|
| CEO | ollama_local ou ollama_cloud | Phi3 Mini / Ministral 3 (respostas curtas); glm-5:cloud se nuvem |
| PO | ollama_local ou ollama_cloud | glm-5:cloud ou qwen2.5 para backlog |
| DevOps, Architect, Developer, QA, CyberSec, UX, DBA | ollama_local | Ollama GPU no cluster (ex.: llama3:8b, deepseek-coder:6.7b para Developer) |
| Governance Proposer | ollama_local (CPU) | qwen2.5:7b (não disputa GPU) |

Para trocar CEO/PO para nuvem: editar `llm-providers-configmap.yaml` (`agent_ceo`, `agent_po`), criar secrets correspondentes e reiniciar o deployment. Ver [37-deploy-fase0-telegram-ceo-ollama.md](37-deploy-fase0-telegram-ceo-ollama.md) (§ Management-team com provedor nuvem).

## Estado atual (início da Fase 1)

- **010:** Definição em [02-agentes.md](02-agentes.md) e issues; tabela de conflitos referenciada.
- **011:** SOUL por escopo: [docs/soul/](soul/) é a fonte. **Management:** CEO e PO em [k8s/management-team/soul/](../k8s/management-team/soul/) (soul-management-agents). **Development:** [k8s/development-team/soul/](../k8s/development-team/soul/) (soul-development-agents). Templates MEMORY/working-buffer em [workspace-ceo-configmap.yaml](../k8s/management-team/openclaw/workspace-ceo-configmap.yaml). Gateway monta ambos em `/workspace/soul` via initContainer soul-merge.
- **012:** [k8s/management-team/](../k8s/management-team/) com deployment openclaw-management (CEO/PO), workspace CEO, secrets Telegram; provedor nuvem via llm-providers e secrets.
- **013:** Pod Developer em [k8s/development-team/developer/](../k8s/development-team/developer/) (PVC, consumer task:backlog, GPU Lock); `make developer-configmap` + `kubectl apply -f k8s/development-team/developer/`. OpenCode: integrar na imagem ou como evolução.
- **014:** Slot único Revisão pós-Dev (125) em [k8s/development-team/revisao-pos-dev/](../k8s/development-team/revisao-pos-dev/) implementa **Architect, QA, CyberSec e DBA** em sequência (um consumidor de code:ready, GPU Lock uma vez). Pods separados por agente (Architect, QA, CyberSec, UX como deployments individuais) são evolução opcional; hoje o slot atende 014.
- **015:** [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) com resumo por agente e link para soul/ e 02-agentes.
- **016:** [08-exemplo-de-fluxo.md](08-exemplo-de-fluxo.md) e [42-fluxo-e2e-operacao-2fa.md](42-fluxo-e2e-operacao-2fa.md) com fases, Redis e riscos.
- **017:** Documentação em 06-operacoes e issues; mecanismos (five strikes, digest) para implementação operacional.
- **018:** Contrato de publicação em [38-redis-streams-estado-global.md](38-redis-streams-estado-global.md) (§2); script [scripts/publish_event_redis.py](../scripts/publish_event_redis.py) para testes.
- **019:** Management com nuvem documentado em [37-deploy-fase0-telegram-ceo-ollama.md](37-deploy-fase0-telegram-ceo-ollama.md); line-up acima; checklist em [validacao-fase1-019.md](issues/validacao-fase1-019.md).

## Topologia alvo (Fase 1)

- **Pods CEO/PO (nuvem):** Um deployment OpenClaw (management-team) com canal Telegram e provedores em nuvem (Ollama Cloud, OpenRouter, OpenAI, etc.). Único ponto de contato com o Diretor.
- **Pods técnicos (100% offline):** Um ou mais deployments/jobs com OpenClaw sub-agents (Developer, Architect, QA, CyberSec, UX, DBA, DevOps) usando apenas Ollama no cluster e Redis; NetworkPolicy sem egress. Slot único de revisão (code:ready) já implementado na Fase 0.
- **Fluxo:** Diretor → Telegram → CEO → PO → Redis (cmd:strategy, task:backlog, draft.2.issue, code:ready) → consumidores técnicos → GPU Lock → Ollama → resultado de volta ao Redis/CEO.

## Workspace SOUL por agente (Fase 1 — implementado)

**Implementado:** Cada agente tem **workspace próprio** com seu SOUL: `/workspace/ceo`, `/workspace/po`, `/workspace/developer`, etc. O initContainer `soul-merge` copia os ConfigMaps soul-management-agents e soul-development-agents para `/workspace/soul/*.md` e em seguida cria `/workspace/<id>/SOUL.md` para cada agente (ceo, po, devops, architect, developer, qa, cybersec, ux, dba). O OpenClaw está configurado com `agents.list[].workspace: "/workspace/<id>"`. Assim, no Slack cada agente responde com sua identidade (Ricardo/CEO, Marina/PO, Lucas/Developer, Rafael/QA, etc.). Variáveis de ambiente (um app Slack por agente): [.env.example](../.env.example). Tokens: [42-slack-tokens-setup.md](42-slack-tokens-setup.md). Governance Proposer usa ConfigMap soul-governance-agents (`governance_proposer.md`).

## Próximos passos (evoluções já implementadas para fechar Fase 1)

1. ~~**SOUL workspace por agente**~~ — Implementado: /workspace/ceo, /workspace/po, … com SOUL.md cada um; config openclaw com workspace por agente; agentes no Slack validados (nomes e funções corretos).
2. **Management nuvem:** Documentação e line-up feitos (019); checklist em [validacao-fase1-019.md](issues/validacao-fase1-019.md).
3. **Pods separados (014):** Implementados em [k8s/development-team/architect/](../k8s/development-team/architect/), [qa/](../k8s/development-team/qa/), [cybersec/](../k8s/development-team/cybersec/), [dba/](../k8s/development-team/dba/) (replicas: 0; ativar com pipeline de streams). Script [scripts/slot_agent_single.py](../scripts/slot_agent_single.py).
4. **017 no orquestrador:** Script de referência [scripts/orchestrator_autonomy.py](../scripts/orchestrator_autonomy.py) (five strikes, orçamento degradação, digest); doc [43-autonomia-nivel-4-matriz-escalonamento.md](43-autonomia-nivel-4-matriz-escalonamento.md).
5. **Publicação Redis pelo gateway:** Adapter HTTP [scripts/gateway_redis_adapter.py](../scripts/gateway_redis_adapter.py) (POST /publish → XADD); OpenClaw pode chamar esse endpoint. Deployment opcional em [k8s/development-team/gateway-redis-adapter/](../k8s/development-team/gateway-redis-adapter/).
6. **OpenCode no Developer:** Dockerfile em [k8s/development-team/developer/Dockerfile](../k8s/development-team/developer/Dockerfile); documentação em [issues/013-pods-tecnicos-developer-opencode.md](issues/013-pods-tecnicos-developer-opencode.md).

Referências: [.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md](../.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md), [docs/issues/README.md](issues/README.md).

---

**Fase 1 considerada fechada no repositório.** Todos os itens 010–019 têm entregáveis em código e documentação; as evoluções opcionais (workspace SOUL por agente, pods separados por agente, 017 no orquestrador, publicação automática Redis pelo gateway, OpenCode no Developer) foram implementadas ou documentadas conforme acima. Validação: [validacao-fase1-completa.md](issues/validacao-fase1-completa.md).
