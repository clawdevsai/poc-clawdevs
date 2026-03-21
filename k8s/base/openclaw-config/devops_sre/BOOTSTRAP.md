# BOOTSTRAP.md - DevOps_SRE

1. Carregar env:
   - `GITHUB_ORG`
   - `ACTIVE_GITHUB_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT`
2. Ler `README.md` do repositório para entender stack e infra.
3. Detectar stack de infra por arquivos:
   - `.github/workflows/` → GitHub Actions
   - `terraform/` ou `infra/` → Terraform
   - `helm/` ou `charts/` → Helm
   - `k8s/` → Kubernetes manifests
   - `docker-compose.yml` → Docker Compose
4. Detectar cloud provider por variáveis de ambiente ou arquivos de configuração.
5. Verificar toolchain no PATH: `kubectl`, `terraform`, `helm`, `docker`, `aws/gcloud/az`.
6. Configurar logger com `task_id` e `infra_type`.
7. Habilitar pesquisa técnica na internet para boas práticas de infra e cloud.
8. Validar autenticação `gh` e permissões do repositório ativo.
9. Configurar agendamento:
   - intervalo fixo: 30 minutos
   - origem de trabalho: issues GitHub label `devops` + monitoramento de produção
10. Pronto.
