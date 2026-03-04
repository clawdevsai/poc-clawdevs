# Fase 4 — O que ainda falta para finalizar

Consolidado a partir do plano, `040-041-pendentes.md`, `040-041-falta-desenvolver-e-testar.md`, scripts, k8s e docs.

Ref: [.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md](../../.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md), [040-perfis-agente-manifesto-config.md](040-perfis-agente-manifesto-config.md), [041-truncamento-contexto-finops.md](041-truncamento-contexto-finops.md).

---

## Escopo da Fase 4 (plano)

- **Issues:** 040 (perfis por agente) e 041 (truncamento/FinOps).
- **Já entregue:** ConfigMaps finops-config e agent-profiles; truncamento na borda (publish_event_redis, gateway_redis_adapter); preflight_summarize; apply_max_tokens; working_buffer_ttl; compact_preserve_protected; validate_reverse_po; microadr_generate no slot; finops_attempt_cost no developer_worker; rota `/publish-to-cloud`; docs (07, operacoes-limite-gastos-provedor, SOUL PO, exemplos agents-devs). Testes unitários em `scripts/test_config_finops.py`.

---

## 1. No repositório (implementado)

| # | Item | Onde | Status |
|---|------|------|--------|
| 1 | **Ler agent-profiles no adapter** | `scripts/gateway_redis_adapter.py` + deployment envFrom `agent-profiles` | Feito: `_get_profile_json(profile)` lê env; resposta `/publish-to-cloud` inclui `profile_suggestion` com modelo/temperature/constraint quando disponível. |
| 2 | **Pipeline que chama validate_reverse_po** | `scripts/validate_reverse_po_after_summary.sh` + [integracao-040-041-gateway-orquestrador.md](integracao-040-041-gateway-orquestrador.md) | Feito: wrapper `SUMMARY_FILE CRITERIA_FILE` propaga exit code; doc atualizado. |
| 3 | **CronJob ou doc para compactação DevOps** | [docs/issues/devops-compactacao-buffer.md](devops-compactacao-buffer.md) + [k8s/development-team/devops-compact-cronjob-example.yaml](../../k8s/development-team/devops-compact-cronjob-example.yaml) + `make devops-compact-configmap` | Feito: doc com uso manual e agendamento; exemplo CronJob; target Makefile para ConfigMap. |
| 4 | **Marcar Fase 4 concluída no plano** | `.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md` | Feito: todo fase4-config-finops com status completed. |

---

## 2. Fora do repositório (contrato / OpenClaw)

| # | Item | Responsável | Ação |
|---|------|-------------|------|
| 5 | **OpenClaw usar `/publish-to-cloud`** | Código do OpenClaw | Para eventos destinados à nuvem, chamar `POST /publish-to-cloud` (com `profile`, `preflight`) em vez de `POST /publish`. |
| 6 | **OpenClaw aplicar MAX_TOKENS ao provedor** | Código do OpenClaw | Se não passar pelo adapter, antes de enviar ao provedor (Gemini, etc.) capar o payload com `MAX_TOKENS_PER_REQUEST_*` conforme perfil (finops-config já no deployment). |
| 7 | **Constraints CEO/PO no comportamento** | OpenClaw / orquestrador | Aplicar regras do perfil (ex.: CEO sem código, freio $5/dia; PO draft_cycle, technical_blocker) ao interpretar agent-profiles. |

---

## 3. Opcional (melhorias)

| # | Item | Onde |
|---|------|------|
| 8 | **Acelerador preditivo** | gateway-redis-adapter ou orquestrador: ao prever estouro (diff/tokens), rotear para modelo local em CPU (PREDICTIVE_LOCAL_THRESHOLD_DIFF_LINES no phase2-config). |
| 9 | **Integração memória em camadas / RAG** | Fase 5 (Warm Store). |

---

## 4. Checklist rápido de validação

- [ ] `kubectl apply -f k8s/security/` aplica sem erro (finops-config, agent-profiles).
- [ ] `python3 scripts/test_config_finops.py` — todos os testes passam.
- [ ] **Script único:** `./scripts/run_validacao_finops_po.sh` — roda test_config_finops e validate_reverse_po (exit 0/1 conforme critérios).
- [ ] Gateway-redis-adapter sobe com envFrom finops-config (e opcional nodeSelector cpu-only).
- [ ] `POST /publish-to-cloud` com body válido retorna 200 e publica no Redis.
- [ ] Validação reversa: `validate_reverse_po.py --summary X --criteria Y` → exit 0 quando resumo cobre critérios; exit 1 quando omite.

---

## 5. Resumo

Para **finalizar a Fase 4** no repo:

1. Implementar **leitura de agent-profiles** no adapter (ou módulo compartilhado) para `/publish-to-cloud`.
2. Adicionar **passo de pipeline** (ou script/doc) que chame **validate_reverse_po** após gerar resumo.
3. Criar **CronJob ou doc** para o DevOps usar **devops_compact_safe.sh** na higiene de buffers.
4. Atualizar o **plano** (Fase 4 concluída) quando 1–3 estiverem fechados.

O restante depende do **OpenClaw** (usar `/publish-to-cloud`, aplicar MAX_TOKENS e constraints de perfil).
