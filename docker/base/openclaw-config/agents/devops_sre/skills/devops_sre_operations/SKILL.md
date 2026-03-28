<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

---
name: devops_sre_operations
description: Skill DevOps/SRE for pipelines, Docker Compose infrastructure, SLOs and production incident response
---

# DevOps_SRE Skills

---

## Manage CI/CD Pipeline (GitHub Actions)

Workflow:
1. Read TASK and understand the type of pipeline change.
2. Check existing workflows in `.github/workflows/`.
3. Implement or correct workflow.
4. Test via `gh workflow run` or push to test branch.
5. Validate stages: lint → test → build → security scan → deploy.
6. Update issue and report to the Architect.

Good practices:
- Use actions with fixed versions (SHA or tag) for reproducibility.
- Dependency caching (`actions/cache`) to reduce time and cost.
- Secrets via GitHub Secrets, never hardcoded.
- Approve production deployments with `environment: production` and reviewers.

---

## Infrastructure as Code

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

### Docker Compose
```bash
docker-compose -f docker-compose.yaml up -d
docker-compose ps                        # status dos containers
docker-compose logs -f <service>         # logs em tempo real
docker-compose restart <service>         # reiniciar container
docker-compose down                      # parar e remover containers
```

---

## Cloud Cost Reduction (AWS / GCP / Azure)

Cost Analysis:
- AWS: `aws ce get-cost-and-usage`, Cost Explorer, Compute Optimizer
- GCP: `gcloud billing budgets list`, Recommender API
- Azure: Azure Cost Management

Priority optimizations:
1. **Right-sizing**: adjust instances to the minimum required (real vs allocated CPU/RAM)
2. **Spot/Preemptible instances**: for interruption-tolerant workloads (CI, batch jobs)
3. **Reserved instances**: for stable workloads > 1 year
4. **Auto-scaling**: HPA/VPA on Kubernetes, ASG on AWS
5. **CDN for static assets**: CloudFront, Cloud CDN — reduces origin traffic
6. **Object storage for logs/backups**: S3/GCS instead of provisioned disk
7. **Revision of storage classes**: Infrequent Access for rarely accessed data

---

## Monitoring and SLOs

Default SLOs (when SPEC not defined):
- Availability: 99.9% (8.7h downtime/year)
- Latency p95: < 300ms
- Latency p99: < 500ms
- Error rate: < 0.1%

Ferramentas:
```bash
# Check health check
kubectl get pods -A | grep -v Running
curl -s http://service/health | jq .

# Check métricas (se Prometheus/Grafana disponível)
kubectl port-forward svc/prometheus 9090:9090
kubectl port-forward svc/grafana 3000:3000
```

---

## Weekly Metrics Report (Monday)

`PROD_METRICS-YYYY-WXX.md` Format:
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

## Incident Response

### P0 — Critical (total production impact)
```
1. Notificar CEO via sessions_send IMEDIATAMENTE
2. Avaliar rollback como primeira opção (rápido e seguro)
3. Investigar causa raiz em paralelo
4. Comunicar status a cada 15 min
5. Post-mortem em /data/openclaw/backlog/incidents/
```

### P1 — High (partial production impact)
```
1. Notificar Arquiteto e PO
2. Criar issue `devops` prioridade alta
3. Implementar fix ou rollback
4. Validar resolução com SLO dashboard
```

---

## Guardrails

- Never modify production without documented TASK or P0.
- Never commit secrets.
- Always `terraform plan` before `apply`.
- Always escalate P0 to CEO immediately.