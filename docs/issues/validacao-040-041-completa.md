# Validação config-perfis / truncamento-finops — Configuração (perfis e FinOps/truncamento)

**Objetivo:** Confirmar que o escopo config-perfis / truncamento-finops (Configuração e FinOps/truncamento) está implementado e integrado no repositório.

Ref: [docs/07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md), [README.md](README.md).

---

## Checklist config-perfis — Perfis por agente (manifesto)

| Item | Entregável | Status |
|------|------------|--------|
| ConfigMap perfis | [k8s/security/agent-profiles-configmap.yaml](../../k8s/security/agent-profiles-configmap.yaml) — CEO, PO, Developer, Architect, DevOps, QA, CyberSec, UX, DBA (modelo, temperature, skills, constraint) | OK |
| Doc 07 | [docs/07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) — Perfis canônicos e constraints por agente | OK |
| Aplicação | `kubectl apply -f k8s/security/` inclui agent-profiles | OK |

---

## Checklist truncamento-finops — Truncamento e FinOps

| Item | Entregável | Status |
|------|------------|--------|
| Config central config-perfis / truncamento-finops | [k8s/security/finops-config-configmap.yaml](../../k8s/security/finops-config-configmap.yaml) — MAX_TOKENS_PER_REQUEST_CEO/PO, PREFLIGHT_SUMMARIZE_MIN_INTERACTIONS, TRUNCATE_BORDER_*, WORKING_BUFFER_TTL_SEC, CRITERIOS_ACEITE_TAG, INVARIANT_TAG | OK |
| Truncamento na borda | [scripts/truncate_payload_border.py](../../scripts/truncate_payload_border.py) — limite de tokens antes de enfileirar; mantém cabeçalho e cauda | OK |
| TTL working buffer | [scripts/working_buffer_ttl.py](../../scripts/working_buffer_ttl.py) — contrato SET key EX ttl; --scan aplica TTL a chaves existentes | OK |
| Pre-flight Summarize | Documentado em 07 e 041: PREFLIGHT_SUMMARIZE_MIN_INTERACTIONS=3; orquestrador aplica sumarização local para >3 interações antes da nuvem | OK |
| Max tokens no Gateway | ConfigMap finops-config: MAX_TOKENS_PER_REQUEST_CEO/PO; Gateway deve aplicar antes de enviar ao provedor (contrato doc 07) | OK |
| Segregação critérios de aceite | Tag `<!-- CRITERIOS_ACEITE -->` / `<!-- /CRITERIOS_ACEITE -->`; [docs/agents-devs/CRITERIOS_ACEITE-example.md](../agents-devs/CRITERIOS_ACEITE-example.md); [scripts/compact_preserve_protected.py](../../scripts/compact_preserve_protected.py) preserva blocos | OK |
| Validação reversa (PO) | Documentado em 07 e 041: PO compara resumo com critérios intactos; rejeita truncamento se omitir critério; exemplo em CRITERIOS_ACEITE-example.md | OK |
| MicroADR | [docs/agents-devs/microADR-template.json](../agents-devs/microADR-template.json) — Architect gera ao aprovar PR; nunca sumarizado; anexar ao Warm Store | OK |
| Invariantes de negócio | Tag `<!-- INVARIANTE_NEGOCIO -->`; [docs/agents-devs/SESSION-STATE.example.md](../agents-devs/SESSION-STATE.example.md); compact_preserve_protected preserva | OK |
| Gancho validação contexto | [scripts/context_validation_hook.py](../../scripts/context_validation_hook.py) — varredura local (stub heurístico); propostas de extração para SESSION-STATE | OK |
| Freio $5/dia e token bucket | Já na Fase 2 (phase2-config, gateway_token_bucket, 07) | OK |
| Doc causa raiz | 07-configuracao-e-prompts.md § Causa raiz do custo (inchaço de contexto, risco OOM, alucinação de escopo) | OK |
| **Truncamento integrado no fluxo** | [publish_event_redis.py](../../scripts/publish_event_redis.py) e [gateway_redis_adapter.py](../../scripts/gateway_redis_adapter.py) truncam payloads grandes; ConfigMap adapter inclui truncate_payload_border.py | OK |
| **Pre-flight Summarize** | [scripts/preflight_summarize.py](../../scripts/preflight_summarize.py) — Ollama local para >N interações; orquestrador/gateway invocam no pipeline | OK |
| **Max tokens (script)** | [scripts/apply_max_tokens.py](../../scripts/apply_max_tokens.py) — aplicar limite por perfil; OpenClaw deployment tem envFrom finops-config | OK |
| **MicroADR no Architect** | [scripts/microadr_generate.py](../../scripts/microadr_generate.py) chamado em [slot_revisao_pos_dev.py](../../scripts/slot_revisao_pos_dev.py) ao aprovar; armazenado no Redis | OK |
| **Validação reversa PO** | [scripts/validate_reverse_po.py](../../scripts/validate_reverse_po.py) + [soul/PO.md](../soul/PO.md) | OK |
| **Limpeza DevOps segura** | [scripts/devops_compact_safe.sh](../../scripts/devops_compact_safe.sh) (wrapper compact_preserve_protected) | OK |
| **TTL na escrita do buffer** | [working_buffer_ttl.py](../../scripts/working_buffer_ttl.py) — função `set_buffer_key(r, key, value, ttl)` | OK |
| **Persistência + FinOps** | [scripts/finops_attempt_cost.py](../../scripts/finops_attempt_cost.py) — contador tentativas, interromper e devolver ao PO | OK |
| **Doc limite gastos provedor** | [docs/operacoes-limite-gastos-provedor.md](../operacoes-limite-gastos-provedor.md) — OpenRouter, OpenAI, Google Cloud, Ollama Cloud | OK |
| **Node selector CPU-only** | gateway-redis-adapter deployment com nodeSelector workload-type: cpu-only | OK |

---

## Resumo

- **config-perfis:** Manifesto de perfis em ConfigMap agent-profiles e em doc 07; constraints por agente (CEO, PO, técnicos, CPU-only para DevOps/UX).
- **truncamento-finops:** Config FinOps e truncamento (ConfigMap finops-config); script truncamento na borda; TTL working buffer; tags CRITERIOS_ACEITE e INVARIANTE_NEGOCIO; script compact_preserve_protected; microADR template; SESSION-STATE.example; gancho context_validation_hook; pre-flight e validação reversa documentados.

Próxima fase: Self-improvement e memória conforme [README.md](README.md).
