# Fase 2 — Segurança: configuração e automação

Todo o ecossistema Fase 2 está preparado para **automação total**: scripts não interativos, configuração via variáveis de ambiente (ConfigMap **phase2-config**), chaves Redis documentadas e contrato claro para o orquestrador/Gateway. Nenhum passo depende de intervenção manual em tempo de execução.

Ref: [docs/issues/README.md](issues/README.md) (Fase 2: 020–029, 126, 128), [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

---

## 1. Configuração central (Phase 2)

O ConfigMap **phase2-config** (namespace **ai-agents**) concentra todas as variáveis acionáveis:

| Variável | Uso | Padrão |
|----------|-----|--------|
| **Token bucket (126)** | |
| TOKEN_BUCKET_MAX_PER_HOUR | Máximo eventos cmd:strategy por hora | 5 |
| EFFICIENCY_RATIO_MIN | Razão mínima PO/CEO para não degradar CEO para local | 0.2 |
| KEY_STRATEGY_COUNT, KEY_CEO_IDEAS, KEY_PO_APPROVED | Chaves Redis para contadores | gateway:* |
| **Quarentena (128)** | |
| QUARANTINE_MAX_ENTROPY_PLAINTEXT | Entropia máx. (bits/byte) para texto esperado | 5.5 |
| QUARANTINE_MAX_ENTROPY_HIGH | Entropia máx. para extensões toleradas (.map, .wasm, …) | 7.9 |
| QUARANTINE_HIGH_ENTROPY_EXT | Extensões com tolerância alta (CSV) | .map,.wasm,.min.js,... |
| **Reputação domínio (024)** | |
| CHECK_DOMAIN_NO_API | Sem API: block \| allow | block |
| **Kill switch (027)** | |
| KEY_PAUSE_CONSUMPTION | Chave Redis de pausa | cluster:pause_consumption |
| THERMAL_THRESHOLD_CHECKPOINT_C | Temperatura para checkpoint (branch efêmera) | 80 |
| THERMAL_THRESHOLD_PAUSE_C | Temperatura para Q-Suite (pausar tudo) | 82 |
| THERMAL_THRESHOLD_RECOVERY_C | Temperatura para retomar | 65 |
| **Orquestrador 017** | |
| DEGRADATION_THRESHOLD_PCT | % tarefas na rota de fuga para emitir pause/digest | 12.0 |
| ORCHESTRATOR_INTERVAL_SEC | Intervalo do loop (s) | 60 |
| STREAM_DIGEST | Stream para digest diário | digest:daily |
| **Flags de automação** | |
| PHASE2_TOKEN_BUCKET_ENABLED | 1 = aplicar token bucket antes de cmd:strategy | 1 |
| PHASE2_QUARANTINE_ENTROPY_ENABLED | 1 = aplicar entropia no pipeline de quarentena | 1 |
| PHASE2_DOMAIN_REPUTATION_ENABLED | 1 = checar reputação antes de liberar egress | 1 |
| PHASE2_PAUSE_RESPECT_ENABLED | 1 = consumidores respeitam cluster:pause_consumption | 1 |

Aplicar: `kubectl apply -f k8s/security/phase2-config-configmap.yaml` (ou `make phase2-apply`).

---

## 2. Contrato de automação (orquestrador / Gateway)

O orquestrador e o Gateway devem seguir estes passos **sem interação humana**. Todos os scripts aceitam argumentos/env e retornam exit code (0 = sucesso/permitir, 1 = bloquear/degradar, 2 = erro de uso).

### 2.1 Publicação em cmd:strategy (CEO)

| Ordem | Ação | Comando / lógica | Exit / resultado |
|-------|------|-------------------|------------------|
| 1 | Verificar se pode emitir evento de estratégia | `python scripts/gateway_token_bucket.py check_bucket` | 0 = pode; 1 = limite excedido (enfileirar ou devolver erro ao CEO) |
| 2 | Se 0: publicar no Redis (cmd:strategy) | Gateway XADD ou adapter POST /publish | — |
| 3 | Registrar evento (contador) | `python scripts/gateway_token_bucket.py record` | 0 |
| 4 | Decidir roteamento CEO (nuvem vs local) | `python scripts/gateway_token_bucket.py check_degrade` | 0 = nuvem OK; 1 = forçar CEO em modelo local (CPU) |

Variáveis: REDIS_HOST, REDIS_PORT, TOKEN_BUCKET_MAX_PER_HOUR, EFFICIENCY_RATIO_MIN (ou envFrom: phase2-config).

### 2.2 Quarentena de disco (resultado do sandbox npm/pip)

| Ordem | Ação | Comando / lógica | Exit / resultado |
|-------|------|-------------------|------------------|
| 1 | Diff de caminhos | Script determinístico (apenas arquivos esperados) | Rejeitar se fora do escopo |
| 2 | Assinaturas (matriz de confiança) | Verificar hash vs registro oficial | Se OK, dispensar entropia restritiva para o pacote |
| 3 | SAST no sandbox | `semgrep scan --config auto --strict` (ou equivalente) | Violação → rejeitar + alerta |
| 4 | Entropia contextual | `python scripts/quarantine_entropy.py <dir_sandbox>` | 0 = passou; 1 = algum arquivo falhou |

Variáveis: QUARANTINE_MAX_ENTROPY_PLAINTEXT, QUARANTINE_HIGH_ENTROPY_EXT (ou envFrom: phase2-config).

### 2.3 Egress (domínio solicitado)

| Ordem | Ação | Comando / lógica | Exit / resultado |
|-------|------|-------------------|------------------|
| 1 | Domínio na whitelist? | Consultar ConfigMap egress-whitelist (ALLOWED_DOMAINS) | Fora da lista → bloquear + alerta |
| 2 | Reputação | `python scripts/check_domain_reputation.py <dominio>` | 0 = allow; 1 = block |

Variáveis: VIRUSTOTAL_API_KEY (opcional), CHECK_DOMAIN_NO_API (block | allow).

### 2.4 Kill switch e pausa

| Gatilho | Ação automatizada | Redis / script |
|---------|-------------------|-----------------|
| Temperatura ≥ THERMAL_THRESHOLD_CHECKPOINT_C (80°C) | DevOps: commit em branch efêmera (recovery-failsafe-*) | Evento prioridade máxima; não setar pausa ainda |
| Temperatura ≥ THERMAL_THRESHOLD_PAUSE_C (82°C) | DevOps: pausar consumidores | `SET cluster:pause_consumption 1` (ou set_pause_consumption(True)) |
| Temperatura ≤ THERMAL_THRESHOLD_RECOVERY_C (65°C) | Retomada: checkout limpo + clear pausa | `SET cluster:pause_consumption 0`; se conflitos → Architect prioridade zero |
| Manual (emergência) | Pausar / retomar | `redis-cli SET cluster:pause_consumption 1` ou `0` |

Consumidores (slot revisão, developer, pods architect/qa/cybersec/dba) já chamam **is_consumption_paused(r)** e não consomem quando True (scripts acefalo_redis, slot_revisao_pos_dev, slot_agent_single).

### 2.5 Orquestrador autonomia (017)

Loop contínuo (ex.: CronJob ou daemon): `python scripts/orchestrator_autonomy.py`. Lê contagens no Redis (five_strikes, omission_cosmetic, sprint_task_count); se % ≥ DEGRADATION_THRESHOLD_PCT, seta orchestration:pause_degradation e publica em digest:daily. Variáveis: REDIS_HOST, DEGRADATION_THRESHOLD_PCT, ORCHESTRATOR_INTERVAL_SEC (ou envFrom: phase2-config).

---

## 3. Chaves Redis (Fase 2)

| Chave | Uso |
|-------|-----|
| cluster:pause_consumption | 1 = pausar consumidores; 0 = retomar |
| cluster:contingency_acefalo | Espelho da pausa (auditoria) |
| gateway:strategy_events_count:hour | Sorted set (timestamp) para token bucket |
| gateway:ceo_ideas_count | Contador ideias CEO (degradação por eficiência) |
| gateway:po_approved_count | Contador tarefas aprovadas PO |
| project:v1:orchestrator:five_strikes_count | Orquestrador 017 |
| project:v1:orchestrator:omission_cosmetic_count | Orquestrador 017 |
| project:v1:orchestrator:sprint_task_count | Orquestrador 017 |
| orchestration:pause_degradation | Pausa por orçamento de degradação (017) |

Não é necessário criar as chaves manualmente; os scripts criam/atualizam no primeiro uso.

---

## 4. Scripts: não interativos (100% automatizáveis)

Todos os scripts abaixo **não** leem stdin nem pedem confirmação; leem config via **variáveis de ambiente** e argumentos posicionais. Podem ser invocados por CronJob, Job, Gateway ou orquestrador sem intervenção humana.

| Script | Uso em automação |
|--------|-------------------|
| gateway_token_bucket.py | check_bucket / record / check_degrade |
| check_domain_reputation.py | <domain> → exit 0 allow, 1 block |
| quarantine_entropy.py | <dir> [dir2 ...] → exit 0 pass, 1 fail |
| orchestrator_autonomy.py | Loop contínuo (Redis + digest) |
| acefalo_redis.py | set_pause_consumption, is_consumption_paused (import) |
| acefalo_contingency.py | Contingência: branch + snapshot + pause |
| acefalo_retomada.py | Retomada: checkout + clear pause |
| gateway_redis_adapter.py | POST /publish (HTTP) para XADD |

---

## 5. Aplicar Fase 2 no cluster

```bash
# Tudo de segurança e config Phase 2
make phase2-apply
```

Ou manualmente:

```bash
kubectl apply -f k8s/security/
```

Isso aplica: **egress-whitelist**, **phase2-config**. O Job do sandbox (seccomp) e o perfil seccomp no nó são opcionais e aplicados conforme [k8s/sandbox/README.md](../k8s/sandbox/README.md).

---

## 6. Resumo

- **Configuração:** ConfigMap **phase2-config** + **egress-whitelist**; pods que precisam de config Fase 2 usam `envFrom: configMapRef: phase2-config`.
- **Automação:** Contrato acima; scripts com exit codes e env; nenhum passo exige OK manual em tempo de execução.
- **Kill switch:** Uma chave Redis (cluster:pause_consumption); consumidores já integrados.
- **Referências:** [20-zero-trust-fluxo.md](20-zero-trust-fluxo.md), [21-quarentena-disco-pipeline.md](21-quarentena-disco-pipeline.md), [27-kill-switch-redis.md](27-kill-switch-redis.md), [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) § 2.1.
