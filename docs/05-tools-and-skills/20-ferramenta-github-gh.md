# Ferramenta GitHub (gh CLI)

Os agentes interagem com o GitHub por meio do **GitHub CLI** (`gh`). Uso de `gh issue`, `gh pr`, `gh run` e `gh api` para Issues, Pull Requests, execuções de CI e consultas avançadas. Relevante para **PO** (backlog, Issues, Projects), **Developer** (PRs, Issues), **Architect** (revisão e merge de PRs), **DevOps/SRE** (repositórios, CI/CD, workflows), **QA** (status de checks, falhas), **CyberSec** (auditoria de PRs e configurações), **DBA** (revisão de PRs na camada de dados, comentários em migrations/queries) e **Governance Proposer** (criar PR no repo dedicado de governança; pull pós-merge; nunca fazer merge — ver [35-governance-proposer.md](35-governance-proposer.md)).

**Requisito:** `gh` instalado e autenticado (`gh auth login`). Sempre usar `--repo owner/repo` quando o comando não for executado dentro de um repositório git, ou usar URLs diretas quando aplicável.

**Autenticação no host (recomendado: SSH):** Use chave SSH para git (clone, push, pull). Crie a chave e registre no GitHub: [21-github-ssh-setup.md](21-github-ssh-setup.md). No `.env` defina `GIT_SSH_KEY_PATH=~/.ssh/id_ed25519_github` (ou o caminho da sua chave). Para `gh` no host, use `gh auth login -h github.com -p ssh` e selecione a chave. O `.env` não deve ser commitado (está no `.gitignore`). Ver [.env.example](../../.env.example).

**Token (alternativa e pods):** Para scripts que usam `gh` sem SSH ou para os **pods** (CEO, PO, DevOps, etc.), use `GH_TOKEN`/`GITHUB_TOKEN` no `.env`; o script `scripts/cluster/secrets-from-env.sh` cria o Secret `clawdevs-github-secret` no cluster. O Secret também inclui `GITHUB_USER`, `GITHUB_ORG` e `GITHUB_SSH_PRIVATE_KEY` (chave SSH base64 para o pod DevOps).

**Segurança:** Nunca expor tokens em chat, logs ou repositório. Seguir postura Zero Trust e validação em runtime ([05-seguranca-e-etica.md](05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md)) ao executar comandos que acessam recursos externos.

**Identificação no histórico:** Sempre que um agente criar issue, PR ou comentário no GitHub, deve **identificar-se no conteúdo** para constar no histórico. Incluir no corpo (ex.: no final) a linha: `— Criado por [Nome do agente, função] — ClawDevs` (ex.: "— Criada por Marina, PO — ClawDevs"). Assim fica registrado no histórico do repo quem (qual agente) criou ou alterou o item.

**URLs — case-sensitive:** Links do GitHub exigem caminho em **minúsculo**. Usar `/issues`, `/pulls`, não `/Issues` nem `/Pulls` (evita 404). Ex.: lista de issues = `https://github.com/clawdevs-ai/clawdevs/issues`.

---

## Pull Requests

### Status de CI em um PR

```bash
gh pr checks 55 --repo owner/repo
```

### Listar execuções recentes de workflow

```bash
gh run list --repo owner/repo --limit 10
```

### Ver uma execução e identificar etapas que falharam

```bash
gh run view <run-id> --repo owner/repo
```

### Ver logs apenas das etapas que falharam

```bash
gh run view <run-id> --repo owner/repo --log-failed
```

---

## API para consultas avançadas

O comando `gh api` acessa dados que não estão disponíveis nos subcomandos de alto nível.

### Obter PR com campos específicos

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

---

## Saída JSON

A maioria dos comandos suporta `--json` para saída estruturada. Usar `--jq` para filtrar:

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

---

## Quem pode usar

| Agente      | Uso principal                                                                 |
|-------------|-------------------------------------------------------------------------------|
| **PO**      | Listar/criar Issues (ou solicitar criação ao DevOps), Kanban/Projects.       |
| **Developer** | Capturar Issues, abrir PRs, ver status de checks; não fazer merge.         |
| **Architect** | Revisar PRs, aprovar/merge quando em conformidade.                         |
| **DevOps/SRE** | Criar/gerenciar repositórios, proteção de branches, webhooks, CI/CD; `gh run`, `gh api`. |
| **QA**      | Verificar status de checks em PRs, falhas de workflow, criar Issues de bug.  |
| **CyberSec** | Auditoria de PRs, configurações de repo, bloqueio de merge se inseguro.    |
| **DBA**      | Revisar PRs (migrations, queries, schema), comentar e bloquear merge quando violar normas de banco ou performance. |
| **Governance Proposer** | Criar PR no repo dedicado de governança (rules, soul, skills, task, configs); pull da main pós-merge; nunca fazer merge. Ver [35-governance-proposer.md](35-governance-proposer.md). |

---

## Relação com a documentação

- [02-agentes.md](02-agentes.md) — Permissões e restrições por agente (ex.: PO sem permissão de escrita solicita criação de Issue ao DevOps).
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Zero Trust, credenciais, nunca expor tokens.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validar comandos e URLs antes de executar.
- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — Skills do ecossistema (ex.: skill "github") podem estar integradas e documentadas aqui como capacidade padrão do time.
- [skills/github/SKILL.md](skills/github/SKILL.md) — Skill **github** para DevOps: `gh` (issues, PRs, runs, api), criação de repositórios na org `$GITHUB_ORG`, verificação antes de afirmar sucesso, path `/workspace/repos/`, link real ao usuário.
- [github-org-clawdevs-ai.md](github-org-clawdevs-ai.md) — Dados da organização clawdevs-ai e resolução de OAuth App restrictions.
