# Validação Fase 2 — Segurança (020–029, 126, 128)

**Objetivo:** Confirmar que o escopo da Fase 2 (Segurança) está implementado e integrado no repositório.

Ref: [44-fase2-seguranca-automacao.md](../44-fase2-seguranca-automacao.md), [README.md](README.md) (Fase 2).

---

## Checklist por bloco

### Configuração e automação

| Item | Entregável | Status |
|------|------------|--------|
| Config central | ConfigMap **phase2-config** ([k8s/security/phase2-config-configmap.yaml](../../k8s/security/phase2-config-configmap.yaml)); `make phase2-apply` | OK |
| Egress whitelist | ConfigMap **egress-whitelist** ([k8s/security/egress-whitelist-configmap.yaml](../../k8s/security/egress-whitelist-configmap.yaml)) | OK |
| Contrato automação | [docs/44-fase2-seguranca-automacao.md](../44-fase2-seguranca-automacao.md) — tabelas de uso dos scripts, chaves Redis | OK |

### Token bucket e degradação (126)

| Item | Entregável | Status |
|------|------------|--------|
| Script | [scripts/gateway_token_bucket.py](../../scripts/gateway_token_bucket.py) — check_bucket, record, check_degrade | OK |
| Integração Gateway | [scripts/gateway_redis_adapter.py](../../scripts/gateway_redis_adapter.py): POST /publish para **cmd:strategy** aplica token bucket; 429 se limite excedido; resposta inclui **degrade_ceo** | OK |
| ConfigMap adapter | `make gateway-redis-adapter-configmap` inclui gateway_token_bucket.py | OK |

### Egress e reputação de domínio (020, 024)

| Item | Entregável | Status |
|------|------------|--------|
| Script reputação | [scripts/check_domain_reputation.py](../../scripts/check_domain_reputation.py) — exit 0 allow, 1 block | OK |
| Endpoint egress | GET **/check_egress?domain=** no adapter: whitelist (ALLOWED_DOMAINS) + opcional reputação; 403 se fora da lista ou bloqueado | OK |
| Deployment adapter | envFrom **egress-whitelist** + **phase2-config**; ConfigMap adapter inclui check_domain_reputation.py | OK |

### Quarentena e entropia (128)

| Item | Entregável | Status |
|------|------------|--------|
| Script entropia | [scripts/quarantine_entropy.py](../../scripts/quarantine_entropy.py) — &lt;dir&gt; → exit 0 pass, 1 fail | OK |
| Pipeline doc | [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md); contrato em doc 44 § 2.2 | OK |
| Sandbox seccomp | [k8s/sandbox/](../../k8s/sandbox/) — job-install-sandbox, seccomp-install-sandbox.json (028) | OK |

### Kill switch (027)

| Item | Entregável | Status |
|------|------------|--------|
| Chave Redis | **cluster:pause_consumption** (1 = pausar); [docs/27-kill-switch-redis.md](../27-kill-switch-redis.md) | OK |
| Consumidores | slot_revisao_pos_dev, slot_agent_single, acefalo_* usam **is_consumption_paused(r)** | OK |
| Config | KEY_PAUSE_CONSUMPTION, THERMAL_* em phase2-config | OK |

### Orquestrador autonomia (017)

| Item | Entregável | Status |
|------|------------|--------|
| Script | [scripts/orchestrator_autonomy.py](../../scripts/orchestrator_autonomy.py) — loop Redis + digest:daily | OK |
| Config | DEGRADATION_THRESHOLD_PCT, ORCHESTRATOR_INTERVAL_SEC, STREAM_DIGEST em phase2-config | OK |

### 022 OWASP e codificação segura

| Item | Entregável | Status |
|------|------------|--------|
| Processo e checklist | [15-seguranca-aplicacao-owasp.md](../15-seguranca-aplicacao-owasp.md) — checklist OWASP, formato relatório, matriz por agente | OK |
| Git hooks (segredos) | [scripts/owasp-pre-commit.sh](../../scripts/owasp-pre-commit.sh) — segredos em staged; opcional gitleaks | OK |
| Bloqueio merge | Doc 15: bloquear merge se Critical/High em aberto | OK |

### 023 CISO habilidades

| Item | Entregável | Status |
|------|------------|--------|
| Auditoria, conformidade, IR, fornecedores | [16-ciso-habilidades.md](../16-ciso-habilidades.md) — checklists e templates | OK |
| Varredura local | [scripts/ciso_local_scan.sh](../../scripts/ciso_local_scan.sh) — somente leitura, .env/.gitignore, permissões | OK |

### 025 Rotação tokens / service account

| Item | Entregável | Status |
|------|------------|--------|
| Service account zerada | [k8s/management-team/openclaw/serviceaccount.yaml](../../k8s/management-team/openclaw/serviceaccount.yaml); deployment usa serviceAccountName: openclaw-router | OK |
| Doc rotação e sandbox | [25-rotacao-tokens-service-account.md](../25-rotacao-tokens-service-account.md) | OK |
| make up | Aplica serviceaccount antes do deployment OpenClaw | OK |

### 026 Detecção injeção de prompt

| Item | Entregável | Status |
|------|------------|--------|
| Lista de padrões e script | [scripts/prompt_injection_detector.py](../../scripts/prompt_injection_detector.py) — detect(text), CLI; PROMPT_INJECTION_EXTRA_PATTERNS | OK |
| Integração doc 14 | Referência em [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) § 1.4 | OK |

### Docs e issues

| # | Issue | Doc / artefato |
|---|-------|----------------|
| 020 | Zero Trust fluxo | [20-zero-trust-fluxo.md](../20-zero-trust-fluxo.md), [020-zero-trust-fluxo-classificacao.md](020-zero-trust-fluxo-classificacao.md) |
| 021 | Segurança runtime / quarentena | [21-quarentena-disco-pipeline.md](../21-quarentena-disco-pipeline.md), [021-seguranca-runtime-validacao.md](021-seguranca-runtime-validacao.md) |
| 022 | OWASP / codificação segura | [15-seguranca-aplicacao-owasp.md](../15-seguranca-aplicacao-owasp.md), owasp-pre-commit.sh |
| 023 | CISO habilidades | [16-ciso-habilidades.md](../16-ciso-habilidades.md), ciso_local_scan.sh |
| 024 | Egress / reputação | check_domain_reputation.py, /check_egress, [024-skills-terceiros-checklist-egress.md](024-skills-terceiros-checklist-egress.md) |
| 025 | Rotação tokens / service account | [25-rotacao-tokens-service-account.md](../25-rotacao-tokens-service-account.md), serviceaccount.yaml |
| 026 | Detecção injeção prompt | prompt_injection_detector.py, [026-detecao-injecao-prompt.md](026-detecao-injecao-prompt.md) |
| 027 | Kill switch | [27-kill-switch-redis.md](../27-kill-switch-redis.md), [027-kill-switch-networkpolicy.md](027-kill-switch-networkpolicy.md) |
| 028 | Sandbox seccomp | [k8s/sandbox/](../../k8s/sandbox/), [028-sandbox-seccomp-ebpf-kernel.md](028-sandbox-seccomp-ebpf-kernel.md) |
| 126 | Token bucket / degradação | gateway_token_bucket.py, adapter POST /publish cmd:strategy, [126-token-bucket-degradacao-eficiencia.md](126-token-bucket-degradacao-eficiencia.md) |
| 128 | SAST / entropia quarentena | quarantine_entropy.py, [128-sast-entropia-quarentena.md](128-sast-entropia-quarentena.md) |

---

## Como validar no cluster

1. **Aplicar Fase 2:** `make phase2-apply` (ou `make up`, que já aplica `k8s/security/`).
2. **Adapter com Fase 2:**  
   `make gateway-redis-adapter-configmap`  
   Aplicar deployment: `kubectl apply -f k8s/development-team/gateway-redis-adapter/deployment.yaml`  
   Escalar: `kubectl scale deployment gateway-redis-adapter -n ai-agents --replicas=1`
3. **Token bucket:**  
   Várias publicações em cmd:strategy (POST /publish com stream cmd:strategy) até exceder TOKEN_BUCKET_MAX_PER_HOUR; esperar 429.  
   Resposta de sucesso deve trazer `degrade_ceo` (true/false).
4. **Check egress:**  
   `curl "http://<adapter-svc>:5000/check_egress?domain=github.com"` → 200 com allow: true.  
   `curl "http://<adapter-svc>:5000/check_egress?domain=evil.example"` → 403.
5. **Kill switch:**  
   `kubectl exec -n ai-agents deploy/redis -- redis-cli SET cluster:pause_consumption 1`  
   Consumidores (slot revisão, etc.) devem parar de consumir; retomar com `SET cluster:pause_consumption 0`.

6. **Rotação de tokens:**  
   `./scripts/validate-token-rotation.sh` — verifica ConfigMap rotation-scripts, RBAC (SA/Role/RoleBinding), CronJob e Secrets. Para testar um run: `kubectl create job -n ai-agents token-rotation-manual --from=cronjob/token-rotation`.

---

## Evoluções opcionais (implementadas)

| Evolução | Entregável | Status |
|----------|------------|--------|
| Rotação automática tokens (025) | rotate_gateway_token.py, rotation-rbac.yaml, cronjob-token-rotation.yaml, make rotation-configmap | OK |
| Pipeline quarentena (semgrep + entropia) (128) | quarantine_pipeline.py, job-quarantine-pipeline.yaml, make quarantine-pipeline-configmap | OK |
| Sandbox URLs desconhecidas (020) | url_sandbox_fetch.py, job-url-sandbox.yaml, make url-sandbox-configmap | OK |
| Matriz de confiança / assinaturas (128) | trusted_package_verify.py, trusted-packages-configmap.yaml | OK |
| Acelerador preditivo tokens | gateway_token_bucket.py (KEY_PREDICTIVE_DIFF_LINES, PREDICTIVE_LOCAL_THRESHOLD_DIFF_LINES), phase2-config | OK |

Ref: [44-fase2-seguranca-automacao.md](../44-fase2-seguranca-automacao.md) § 7.

---

## Conclusão

**Fase 2 (020–029, 126, 128) considerada implementada no repositório**, incluindo **evoluções opcionais**: rotação automática de tokens (CronJob + script), pipeline de quarentena (SAST + entropia), sandbox para URLs, matriz de confiança (trusted_package_verify) e acelerador preditivo (Redis + check_degrade). Núcleo e issues 022, 023, 025, 026 conforme tabelas acima. Ref: [.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md](../../.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md).
