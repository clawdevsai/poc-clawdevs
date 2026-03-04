# Organização GitHub clawdevs.ai — dados completos

Referência para configuração e para o agente DevOps. A organização é o **destino padrão** dos repositórios criados pelo DevOps.

## Organização

| Campo        | Valor |
|--------------|--------|
| Nome exibido | clawdevs.ai |
| Slug / login | **clawdevs-ai** (usar em URLs e em `gh`) |
| URL perfil   | https://github.com/clawdevs-ai |
| Variável env| `GITHUB_ORG=clawdevs-ai` |

## Conta de autenticação (Owner da org)

| Campo     | Valor |
|-----------|--------|
| Login     | clawdevsai |
| Variável  | `GITHUB_USER=clawdevsai` |
| Permissão | Owner da organização clawdevs-ai |

O token (PAT) usado pelo `gh` e pelos pods está associado a esta conta; com ele o DevOps cria repositórios **na organização** via `gh repo create $GITHUB_ORG/<nome-repo>`.

## Configuração no cluster

- **Secret** `clawdevs-github-secret`: deve conter `GITHUB_USER`, `GITHUB_ORG`, `GITHUB_TOKEN`/`GH_TOKEN`. Criado/atualizado por `./scripts/cluster/secrets-from-env.sh` a partir do `.env`.
- **Workspace DevOps:** o arquivo `GITHUB-CONTEXT.md` (ConfigMap `workspace-devops-configmap`) é copiado para `/workspace/devops/` e contém estes dados para o agente.

## Comandos de referência (DevOps)

- Criar repo na org: `gh repo create $GITHUB_ORG/<nome-repo> --private --description="..." --clone=false`
- Verificar: `gh repo view $GITHUB_ORG/<nome-repo>` ou `gh repo list $GITHUB_ORG --limit 5`
- Clone: `git clone https://x-access-token:$GITHUB_TOKEN@github.com/$GITHUB_ORG/<nome-repo>.git ...`
- Link ao usuário: `https://github.com/$GITHUB_ORG/<nome-repo>` (ex.: https://github.com/clawdevs-ai/user-api)

## OAuth App access restrictions (resolvido 2026-03-04)

A organização `clawdevs-ai` **tinha** restrições de OAuth apps ativadas, o que bloqueava `gh` e API REST (HTTP 403):
```
the `clawdevs-ai` organization has enabled OAuth App access restrictions
```

**Resolução:** o owner removeu as restrições em:
- https://github.com/organizations/clawdevs-ai/settings/oauth_application_policy → **Remove restrictions**.

**Policy atual:** No restrictions — o `gh` e a API REST agora funcionam normalmente com o PAT do `clawdevsai`.

> Se a política for reativada no futuro, o owner precisa aprovar o app GitHub CLI em `Settings → Third-party access → GitHub CLI → Grant access` ou remover as restrições novamente.

## Relação com outros docs

- [20-ferramenta-github-gh.md](20-ferramenta-github-gh.md) — Uso do `gh` pelos agentes.
- [21-github-ssh-setup.md](21-github-ssh-setup.md) — Chave SSH e token para pods.
- [skills/github/SKILL.md](skills/github/SKILL.md) — Skill github do DevOps (criar na org, verificar antes de afirmar sucesso).
