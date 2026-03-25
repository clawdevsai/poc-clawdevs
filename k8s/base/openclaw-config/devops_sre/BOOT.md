# BOOT.md - DevOps_SRE

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação, stack e infraestrutura.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json`.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/devops_sre/MEMORY.md` — resgatar aprendizados próprios de infraestrutura relevantes.
8. Validar `/data/openclaw/` e workspace de infraestrutura.
9. Detectar stack de infra: Kubernetes manifests, Terraform, Helm, GitHub Actions workflows.
10. Verificar ferramentas no PATH: `kubectl`, `terraform`, `helm`, `gh`, `git`.
11. Verificar cloud CLI disponível: `aws`, `gcloud`, `az`.
12. Validar variáveis via `/data/openclaw/contexts/active_repository.env`: `ACTIVE_GITHUB_REPOSITORY`.
13. Verificar SLOs e alertas ativos em `/data/openclaw/backlog/status/`.
14. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/devops_sre/MEMORY.md`.
15. Pronto para receber tasks do Arquiteto ou incidentes de produção.

## healthcheck
- `/data/openclaw/` acessível? ✅
- INPUT_SCHEMA.json carregado? ✅
- Stack de infra detectada? ✅
- Ferramentas `kubectl`, `gh`, `terraform` disponíveis? ✅ (warn se ausentes, não falhar)
- SHARED_MEMORY.md e MEMORY.md (devops_sre) lidos? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅
