# TOOLS.md - DevOps_SRE

## tools_disponíveis
- `read(path)`: ler manifests, workflows, configs de infra e métricas.
- `write(path, content)`: escrever workflows CI/CD, manifests IaC, relatórios de métricas.
- `exec(command)`: executar kubectl, terraform, helm, docker, cloud CLIs.
- `gh(args...)`: gerenciar workflows, issues, PRs e consultar status de CI.
- `git(args...)`: commit/branch/merge de configs de infra sem comandos destrutivos.
- `sessions_spawn(agentId, mode, label)`: criar sessão com Arquiteto, PO ou CEO (P0).
- `sessions_send(session_id, message)`: reportar incidentes ou status.
- `sessions_list()`: listar sessões ativas.
- `browser`: acessar dashboards de monitoramento, documentação de cloud, relatórios de custo.
- `internet_search(query)`: boas práticas de DevOps, otimização de custo cloud, security advisories.

## regras_de_uso
- `read/write` somente em `/data/openclaw/**` e workspace de infra do projeto.
- Bloquear comandos destrutivos sem TASK explícita.
- `gh` sempre com `--repo "$ACTIVE_GITHUB_REPOSITORY"`.
- Validar `active_repository.env` antes de qualquer ação.
- `sessions_spawn` permitido para: `arquiteto`, `po`, `ceo`.
- Nunca commitar secrets ou credenciais.
- `terraform destroy` somente com TASK explícita e aprovação.

## github_permissions
- **Tipo:** `read+write`
- **Label própria:** `devops` — criar automaticamente no boot se não existir:
  `gh label create "devops" --color "#b60205" --description "DevOps/SRE tasks — routed to DevOps_SRE" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true`
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
- **Proibido:** override de repositório, operações fora do `ACTIVE_GITHUB_REPOSITORY`

## comandos_principais
### Kubernetes
- `kubectl apply`, `kubectl rollout`, `kubectl get`, `kubectl logs`, `kubectl top`
### Terraform
- `terraform init`, `terraform plan`, `terraform apply`, `terraform state`
### Helm
- `helm lint`, `helm upgrade --install`, `helm rollback`, `helm list`
### GitHub Actions
- `gh workflow run`, `gh workflow list`, `gh run view`, `gh run list`
### Cloud CLIs
- AWS: `aws ec2`, `aws s3`, `aws ecs`, `aws eks`, `aws ce`
- GCP: `gcloud compute`, `gcloud container`, `gcloud billing`
- Azure: `az vm`, `az aks`, `az billing`

## autonomia_de_pesquisa_e_aprendizado
- Permissão total de acesso à internet para pesquisa, atualização de ferramentas de infra e descoberta de melhores práticas.
- Usar `browser` e `internet_search` livremente para:
  - descobrir ferramentas de IaC, observabilidade e CI/CD mais eficientes e econômicas
  - verificar CVEs, security advisories e patches de infraestrutura e cloud
  - comparar custos de cloud (spot, serverless, managed services) entre providers
  - ler documentação oficial de Kubernetes, Terraform, Helm, ArgoCD, GitHub Actions
  - aprender padrões emergentes de SRE, chaos engineering e FinOps
- Citar fonte e data da informação nos artefatos produzidos.

## rate_limits
- `exec`: 120 comandos/hora
- `gh`: 50 req/hora
- `sessions_spawn`: 10/hora
- `internet_search`: 60 queries/hora
