# Fase 2 — Segurança (k8s/security)

Recursos Kubernetes para a **Fase 2 — Segurança**: configuração central e whitelist de egress. Todo o ecossistema é **automatizável** (scripts não interativos, config via env).

## Manifestos

| Arquivo | Uso |
|---------|-----|
| **phase2-config-configmap.yaml** | Config central: token bucket, entropia, reputação domínio, kill switch, orquestrador 017, flags PHASE2_* |
| **egress-whitelist-configmap.yaml** | Whitelist global estática de domínios (ALLOWED_DOMAINS, TRUSTED_PUBLISHERS) |

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
