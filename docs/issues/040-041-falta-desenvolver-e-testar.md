# config-perfis / truncamento-finops — O que ainda falta desenvolver e testar

Resumo do que falta para fechar desenvolvimento e validação (perfis por agente e truncamento/FinOps).

Ref: [040-perfis-agente-manifesto-config.md](040-perfis-agente-manifesto-config.md), [041-truncamento-contexto-finops.md](041-truncamento-contexto-finops.md), [040-041-pendentes.md](040-041-pendentes.md).

---

## 1. O que ainda falta DESENVOLVER

### 1.1 config-perfis — Perfis por agente

| Item | Situação | Ação |
|------|----------|------|
| **Ler agent-profiles no Gateway/Orquestrador** | **Implementado** | `gateway_redis_adapter.py` lê env do ConfigMap `agent-profiles` (`_get_profile_json`); resposta `/publish-to-cloud` inclui `profile_suggestion`; deployment usa envFrom agent-profiles. |
| **Constraints aplicadas por agente** | Parcial | Architect 80% cobertura: já via prompt no slot; DevOps 82°C: phase2-config; outras constraints (ex.: CEO no_code, PO draft_cycle) dependem do OpenClaw/orquestrador externo aplicar as regras ao interpretar o perfil |

### 1.2 truncamento-finops — Truncamento e FinOps

| Item | Situação | Ação |
|------|----------|------|
| **OpenClaw aplicar MAX_TOKENS ao enviar ao provedor** | Config (finops-config) está no deployment; código do OpenClaw é **fora do repo** | No código do OpenClaw (externo): antes de chamar API do provedor, capar o payload com `MAX_TOKENS_PER_REQUEST_*` conforme perfil; ou sempre enviar via adapter usando `POST /publish-to-cloud` |
| **OpenClaw usar `/publish-to-cloud`** | Rota existe no adapter; quem chama é o OpenClaw | Configurar o OpenClaw para usar `POST /publish-to-cloud` (com `profile` e `preflight`) em vez de `/publish` quando o evento for destinado à nuvem |
| **Pipeline PO: chamar validate_reverse_po** | **Implementado** | [validate_reverse_po_after_summary.sh](../../scripts/validate_reverse_po_after_summary.sh); doc [integracao-040-041-gateway-orquestrador.md](integracao-040-041-gateway-orquestrador.md). Pipeline que gera resumo deve chamar o script; exit 1 → não substituir buffer. |
| **DevOps: usar devops_compact_safe.sh no cron** | **Implementado** | [devops-compact-cronjob-example.yaml](../../k8s/development-team/devops-compact-cronjob-example.yaml), [devops-compactacao-buffer.md](devops-compactacao-buffer.md); `make devops-compact-configmap`. |
| **Acelerador preditivo** | Documentado em 07/05; **não implementado** no adapter/orquestrador | Se desejado: ao prever estouro (ex.: por tamanho do diff ou histórico de tokens), rotear para modelo local em CPU em vez de só acionar freio (usar PREDICTIVE_LOCAL_THRESHOLD_DIFF_LINES do phase2-config) |

### 1.3 Resumo desenvolvimento

- **No repositório (concluído):** ler `agent-profiles` no adapter; wrapper `validate_reverse_po_after_summary.sh` e doc de pipeline; CronJob exemplo e doc para compactação DevOps.
- **Fora do repositório:** OpenClaw usar `/publish-to-cloud` e aplicar MAX_TOKENS ao provedor; aplicar constraints de negócio (CEO, PO) conforme perfis.

---

## 2. O que ainda falta TESTAR

### 2.1 Testes unitários / de contrato (sem Redis/Ollama)

| Script / módulo | O que testar | Prioridade |
|-----------------|--------------|------------|
| **truncate_payload_border.py** | `truncate_payload()` com texto grande; preserva head/tail; `estimate_tokens` | Alta |
| **compact_preserve_protected.py** | Blocos `CRITERIOS_ACEITE` e `INVARIANTE_NEGOCIO` preservados; resto truncado | Alta |
| **validate_reverse_po.py** | `extract_criteria()`, `summary_mentions()`; exit 0/1 conforme resumo cobre critérios | Alta |
| **finops_attempt_cost.py** | `should_stop_task()` para attempt &gt;= max e para custo &gt;= cap; `increment_attempt` (com Redis mock ou integração) | Alta |
| **preflight_summarize.py** | `count_interactions()` para payload com messages/history; pass-through quando &lt;= N ou sem Ollama | Média |
| **apply_max_tokens.py** | Saída truncada ao limite por perfil (CEO, PO, default) | Média |
| **context_validation_hook.py** | Heurística de detecção de regras (nunca, sempre, deve) e proposta de tag | Baixa |
| **redis_buffer_writer.py** | `write_working_buffer()` (com Redis mock ou integração) | Média |
| **gateway_redis_adapter** | `_apply_preflight_and_max_tokens()` com payload mock; rota `/publish-to-cloud` retorna 200 e aplica limite | Média |
| **developer_worker** | Com mock de `finops_attempt_cost`: quando `should_stop_task` True, não entra no GPULock e emite evento | Média |

### 2.2 Testes de integração (com Redis e, opcionalmente, Ollama)

| Cenário | Objetivo |
|---------|----------|
| **Adapter: POST /publish-to-cloud** | Payload com &gt;3 interações e Ollama ligado: resposta contém resumo; payload publicado no Redis com tamanho limitado |
| **Developer worker + FinOps** | Publicar tarefa com issue_id; incrementar attempt até FINOPS_MAX_ATTEMPTS; verificar que worker faz XACK e emite `task_returned_to_po` sem processar |
| **Working buffer TTL** | Escrever com `write_working_buffer`; verificar TTL da chave no Redis |
| **Compactação segura** | Arquivo com blocos protegidos; rodar `devops_compact_safe.sh`; verificar que blocos permanecem no .compact |

### 2.3 Testes manuais / checklist

- [ ] `kubectl apply -f k8s/security/` aplica finops-config e agent-profiles sem erro.
- [ ] Gateway-redis-adapter sobe com envFrom finops-config e nodeSelector cpu-only (ou sem nodeSelector se nó não tiver label).
- [ ] Chamada `POST /publish-to-cloud` com body válido retorna 200 e `id` no stream.
- [ ] Validação reversa: arquivo de critérios + resumo que omite critério → exit 1; resumo que cobre → exit 0.

---

## 3. Próximos passos sugeridos

1. **Rodar `scripts/test_config_finops.py`** — testes de contrato para truncate_payload_border, compact_preserve_protected, validate_reverse_po, finops_attempt_cost (e gateway/developer_worker).
2. **Implementar leitura de agent-profiles** no gateway_redis_adapter (ou em um módulo compartilhado) para que `/publish-to-cloud` use modelo/limite do perfil quando disponível.
3. **Documentar ou implementar** um passo de pipeline que chame `validate_reverse_po` após gerar resumo (ex.: em script que invoca preflight e grava em arquivo).
4. **CronJob ou doc** para o DevOps: exemplo de CronJob que chama `devops_compact_safe.sh` nos paths de buffer.

Com isso, config-perfis / truncamento-finops ficam com desenvolvimento e testes explícitos no repo; o que depender do OpenClaw continua como contrato/documentação.
