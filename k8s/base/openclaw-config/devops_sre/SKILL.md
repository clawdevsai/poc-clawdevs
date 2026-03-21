# Skills do DevOps_SRE

---

## Gerenciar Pipeline CI/CD (GitHub Actions)

Workflow:
1. Ler TASK e entender o tipo de mudança de pipeline.
2. Verificar workflows existentes em `.github/workflows/`.
3. Implementar ou corrigir workflow.
4. Testar via `gh workflow run` ou push em branch de teste.
5. Validar stages: lint → test → build → security scan → deploy.
6. Atualizar issue e reportar ao Arquiteto.

Boas práticas:
- Usar actions com versões fixas (SHA ou tag) para reprodutibilidade.
- Cache de dependências (`actions/cache`) para reduzir tempo e custo.
- Secrets via GitHub Secrets, nunca hardcoded.
- Aprovar deploys de produção com `environment: production` e reviewers.

---

## Infraestrutura como Código

### Terraform
```bash
terraform init
terraform plan -out=tfplan
terraform apply tfplan
terraform destroy -auto-approve  # SOMENTE com TASK explícita
```

### Helm
```bash
helm lint ./charts/myapp
helm upgrade --install myapp ./charts/myapp --values values.prod.yaml
helm rollback myapp 1              # rollback para revisão anterior
```

### Kubernetes
```bash
kubectl apply -k k8s/
kubectl rollout status deployment/myapp
kubectl rollout undo deployment/myapp   # rollback
kubectl top pod                          # monitoramento de recursos
```

---

## Redução de Custo Cloud (AWS / GCP / Azure)

Análise de custo:
- AWS: `aws ce get-cost-and-usage`, Cost Explorer, Compute Optimizer
- GCP: `gcloud billing budgets list`, Recommender API
- Azure: Azure Cost Management

Otimizações prioritárias:
1. **Right-sizing**: ajustar instâncias para o mínimo necessário (CPU/RAM reais vs alocados)
2. **Spot/Preemptible instances**: para workloads tolerantes a interrupção (CI, jobs batch)
3. **Reserved instances**: para workloads estáveis > 1 ano
4. **Auto-scaling**: HPA/VPA no Kubernetes, ASG na AWS
5. **CDN para assets estáticos**: CloudFront, Cloud CDN — reduz tráfego de origem
6. **Object storage para logs/backups**: S3/GCS em vez de disco provisionado
7. **Revisão de storage classes**: Infrequent Access para dados raramente acessados

---

## Monitoramento e SLOs

SLOs padrão (quando SPEC não definir):
- Disponibilidade: 99.9% (8.7h downtime/ano)
- Latência p95: < 300ms
- Latência p99: < 500ms
- Taxa de erro: < 0.1%

Ferramentas:
```bash
# Verificar health check
kubectl get pods -A | grep -v Running
curl -s http://service/health | jq .

# Verificar métricas (se Prometheus/Grafana disponível)
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000
```

---

## Relatório Semanal de Métricas (Segunda-feira)

Formato de `PROD_METRICS-YYYY-WXX.md`:
```markdown
# PROD_METRICS-2025-W12

## Período: 2025-03-17 a 2025-03-23

## SLOs
| Métrica | Meta | Real | Status |
|---------|------|------|--------|
| Disponibilidade | 99.9% | 99.97% | ✅ |
| Latência p95 | <300ms | 187ms | ✅ |
| Latência p99 | <500ms | 312ms | ✅ |
| Taxa de erro | <0.1% | 0.03% | ✅ |

## Deployment Frequency
- Deploys na semana: 7
- Deploys com rollback: 0

## Custo Cloud
- Total: $XXX
- vs semana anterior: -5% (otimização de instâncias)

## Incidentes
- P0: 0
- P1: 1 (resolvido em 23 min)

## Recomendações para CEO
- [feature X] teve 40% de uso — oportunidade de investimento
- Custo de DB aumentou 15% — revisar queries ineficientes com DBA
```

---

## Resposta a Incidentes

### P0 — Crítico (impacto total de produção)
```
1. Notificar CEO via sessions_send IMEDIATAMENTE
2. Avaliar rollback como primeira opção (rápido e seguro)
3. Investigar causa raiz em paralelo
4. Comunicar status a cada 15 min
5. Post-mortem em /data/openclaw/backlog/incidents/
```

### P1 — Alto (impacto parcial de produção)
```
1. Notificar Arquiteto e PO
2. Criar issue `devops` prioridade alta
3. Implementar fix ou rollback
4. Validar resolução com SLO dashboard
```

---

## Guardrails

- Nunca modificar produção sem TASK ou P0 documentado.
- Nunca commitar secrets.
- Sempre `terraform plan` antes de `apply`.
- Sempre escalar P0 ao CEO imediatamente.
