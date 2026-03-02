# Fase 2 — Segurança (k8s/security)

Recursos Kubernetes para a **Fase 2 — Segurança**: configuração central e whitelist de egress. Todo o ecossistema é **automatizável** (scripts não interativos, config via env).

## Manifestos

| Arquivo | Uso |
|---------|-----|
| **phase2-config-configmap.yaml** | Config central: token bucket, entropia, reputação domínio, kill switch, orquestrador 017, preditivo, flags PHASE2_* |
| **egress-whitelist-configmap.yaml** | Whitelist global estática de domínios (ALLOWED_DOMAINS, TRUSTED_PUBLISHERS) |
| **rotation-rbac.yaml** | ServiceAccount + Role + RoleBinding para CronJob de rotação de tokens |
| **cronjob-token-rotation.yaml** | CronJob (a cada 3 min): sincroniza openclaw-telegram-rotation-source → openclaw-telegram |
| **job-url-sandbox.yaml** | Job template: fetch de URL em sandbox (URL_SANDBOX_TARGET); resultado em digest:daily |
| **trusted-packages-configmap.yaml** | Opcional: lista TRUSTED_PACKAGES (matriz de confiança) |
| **finops-config-configmap.yaml** | truncamento-finops — FinOps e truncamento: MAX_TOKENS_PER_REQUEST_*, PREFLIGHT_SUMMARIZE_MIN_INTERACTIONS, TRUNCATE_BORDER_*, WORKING_BUFFER_TTL_SEC, tags CRITERIOS_ACEITE e INVARIANTE |
| **agent-profiles-configmap.yaml** | config-perfis — Perfis por agente (modelo, temperature, skills, constraint) para Gateway/orquestrador |

## Aplicar

```bash
make phase2-apply
```

Ou: `kubectl apply -f k8s/security/`

O `make up` já aplica este diretório quando existir.

## Uso em pods

Para pods que precisam das variáveis da Fase 2 (Gateway, orquestrador, jobs de quarentena):

```yaml
envFrom:
  - configMapRef:
      name: phase2-config
```

Exemplo: deployment do gateway-redis-adapter usa `envFrom: phase2-config` (optional: true para não falhar se o ConfigMap não existir).

## Contrato de automação

Ver **[docs/44-fase2-seguranca-automacao.md](../../docs/44-fase2-seguranca-automacao.md)** — tabelas de quando chamar cada script, chaves Redis, e garantia de que nenhum passo exige intervenção manual.
