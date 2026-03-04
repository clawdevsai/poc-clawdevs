# Investigação: DevOps não preenche ~/clawdevs-shared/repos e repo não aparece no GitHub

**Data:** 2026-03-04

## Sintoma

- Usuário pediu ao DevOps (via Slack) criar o repositório **user-api** (privado, descrição "Gerenciado de cadastro de usuario", estrutura inicial).
- O DevOps respondeu que iria: criar no GitHub, clonar em `/workspace/repos/user-api`, adicionar estrutura e fazer push.
- **Nada apareceu** em `~/clawdevs-shared/repos` no host nem o repositório **user-api** na conta [clawdevsai no GitHub](https://github.com/clawdevsai?tab=repositories) (que tem acesso total via token/SSH).

## Causa raiz

### 1. `gh` CLI não está instalado na imagem do gateway OpenClaw

O **TOOLS.md** do workspace DevOps (ConfigMap `workspace-devops-configmap`) instrui:

1. **Criar no GitHub:** `gh repo create <owner>/<nome-repo> --private --description="..." --clone=false`
2. Clonar em `/tmp/<nome-repo>` e mover para `/workspace/repos/<nome-repo>`
3. Commit e push

O **Dockerfile** do OpenClaw (`k8s/management-team/openclaw/Dockerfile`) instala apenas:

- `curl`, `git`  
- **Não instala `gh`** (GitHub CLI).

Quando o agente tenta executar `gh repo create ...`, o comando **não existe** no container. O passo 1 falha; o repositório nunca é criado no GitHub e o fluxo não avança. Nada é clonado em `/workspace/repos/`, então nada aparece em `~/clawdevs-shared/repos` no host.

### 2. Path e mount (já corretos)

- O deployment usa o PVC `openclaw-shared-workspace-pvc` → PV com `hostPath: /agent-shared`.
- O host monta `~/clawdevs-shared` em `/agent-shared` no Minikube via `make shared` (minikube mount).
- Dentro do pod, `/workspace` = conteúdo de `/agent-shared` = `~/clawdevs-shared` no host.
- `/workspace/repos/` no pod = `~/clawdevs-shared/repos/` no host.

Se o DevOps tivesse conseguido criar e clonar o repo em `/workspace/repos/user-api`, o conteúdo apareceria no host. O problema não é o path nem o mount e sim a falha no primeiro passo (`gh` inexistente).

### 3. GitHub

- A conta clawdevsai tem 1 repositório listado (**clawdevs**, privado). O **user-api** não foi criado porque `gh repo create` nunca rodou com sucesso.
- O Secret `clawdevs-github-secret` (GITHUB_TOKEN / GH_TOKEN) está disponível no pod; quando `gh` estiver instalado, ele usará automaticamente `GH_TOKEN`/`GITHUB_TOKEN` para autenticação.

## Correções aplicadas

1. **Instalar `gh` (GitHub CLI) na imagem OpenClaw**  
   - No Dockerfile: instalar `gh` (ex.: via script oficial ou pacote) para que o fluxo documentado no TOOLS.md do DevOps funcione.
2. **Opcional – fallback no TOOLS.md:**  
   - Se `gh` não estiver disponível ou falhar, instruir o agente a criar o repositório via **GitHub API** com `curl` e `GITHUB_TOKEN`, depois usar `git clone`/`git push` em `/workspace/repos/<nome-repo>`.

## Como validar após a correção

1. Rebuild da imagem e restart do deployment:
   ```bash
   eval $(minikube docker-env)
   docker build -f k8s/management-team/openclaw/Dockerfile -t openclaw-gateway:local k8s/management-team/openclaw
   kubectl rollout restart deployment/openclaw -n ai-agents
   ```
2. Confirmar que `gh` existe no pod:
   ```bash
   kubectl exec -n ai-agents deploy/openclaw -c gateway -- which gh && gh auth status
   ```
   (Com `GITHUB_TOKEN`/`GH_TOKEN` no ambiente, `gh` usa o token automaticamente.)
3. Pedir novamente ao DevOps (Slack) para criar um repositório (ex.: user-api) e conferir:
   - Repo criado em https://github.com/clawdevsai?tab=repositories
   - Conteúdo em `~/clawdevs-shared/repos/<nome-repo>` no host (com `make shared` ativo).

## Referências

- `k8s/management-team/openclaw/Dockerfile` — imagem do gateway (antes: sem `gh`).
- `k8s/management-team/openclaw/workspace-devops-configmap.yaml` — TOOLS.md que manda usar `gh repo create`.
- `docs/05-tools-and-skills/20-ferramenta-github-gh.md` — requisito de `gh` instalado e autenticado nos agentes.
- `docs/08-technical-notes/workspace-compartilhado-repositorio-ceo.md` — path `/workspace/repos` e mount host.
