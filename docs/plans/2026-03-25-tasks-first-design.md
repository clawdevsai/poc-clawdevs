# Design: Tasks-First — Control Panel como Source of Truth

**Data:** 2026-03-25
**Status:** Aprovado
**Autor:** Diretor + Claude

---

## Contexto

Atualmente o fluxo de desenvolvimento usa GitHub Issues como sistema central de rastreamento de tarefas. O Arquiteto cria issues com labels, e cada agente executor faz polling de `gh issue list --label <label>`.

A mudança elimina completamente a criação de GitHub Issues pelos agentes. O Control Panel passa a ser o único source of truth de tarefas. Issues do GitHub deixam de existir como mecanismo de orquestração; `gh` continua sendo usado apenas para git (commits, branches, PRs, workflows).

---

## Objetivo

- Usuário (ou agentes) criam tarefas no Inbox do control-panel
- Agentes executores leem tarefas via API REST do control-panel
- Suporte a múltiplos repositórios por task
- Zero criação de GitHub Issues pelos agentes
- Aprovações críticas continuam via Telegram → /approvals (sem mudança)

---

## Decisões de Design

| Decisão | Escolha | Motivo |
|---------|---------|--------|
| Roteamento de agentes | Campo `label` na Task | Mantém mesma lógica dos labels do GitHub, só muda o transporte |
| Gestão de repositórios | Tabela `repositories` no banco + UI em Settings | Flexível, sem redeploy para adicionar repos |
| Auth dos agentes | JWT de longa duração (30 dias) via `POST /auth/agent-token` | Agentes usam `curl`, precisam de token estável |
| Injeção de credenciais | Env vars `PANEL_API_URL` + `PANEL_TOKEN` nos pods via K8s Secret | Seguro, sem hardcode |

---

## Arquitetura

### Fluxo Novo

```
Usuário cria Task (Inbox) ─────────────────────────────┐
Arquiteto cria Task via API ───────────────────────────►│ Control Panel Tasks DB
                                                        │  - label: back_end/front_end/...
                                                        │  - github_repo: org/repo
                                                        │  - status: inbox/in_progress/done
Dev_Backend poll GET /tasks?status=inbox&label=back_end◄┘
Dev_Backend PATCH /tasks/{id} status=in_progress
Dev_Backend faz o trabalho (git, gh pr, commits no repo)
Dev_Backend PATCH /tasks/{id} status=done
QA_Engineer poll GET /tasks?status=done&label=tests
...
```

### O que NÃO muda

- `gh pr create`, `gh commit`, `gh workflow`, `gh run view` pelos agentes
- Estrutura de sessions / sessions_spawn entre agentes
- SDD artifacts (BRIEF, SPEC, PLAN, TASK, VALIDATE)
- Flow de Approvals via Telegram → /approvals
- HEARTBEAT, IDENTITY, SOUL, BOOTSTRAP de cada agente

---

## Mudanças no Banco de Dados

### Nova tabela `repositories`

```sql
CREATE TABLE repositories (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           VARCHAR NOT NULL,           -- display name (ex: "ClawDevs API")
    full_name      VARCHAR NOT NULL UNIQUE,    -- org/repo (ex: "clawdevs/api")
    description    VARCHAR,
    default_branch VARCHAR DEFAULT 'main',
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT now(),
    updated_at     TIMESTAMP DEFAULT now()
);
```

### Mudanças na tabela `tasks`

```sql
ALTER TABLE tasks ADD COLUMN label VARCHAR;
-- valores: back_end | front_end | mobile | tests | devops | dba | security | ux | NULL
-- github_repo já existe, será preenchido com full_name do repo selecionado
```

---

## API Backend

### Novos endpoints `/repositories`

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| GET | `/repositories` | Listar repos (is_active por padrão) | Bearer |
| POST | `/repositories` | Cadastrar repo | Bearer |
| PATCH | `/repositories/{id}` | Editar nome, branch, ativar/desativar | Bearer |
| DELETE | `/repositories/{id}` | Remover repo | Bearer |

### Endpoint de token para agentes

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/agent-token` | Gera JWT de 30 dias para uso dos agentes (admin only) |

### Mudanças em `/tasks`

**POST /tasks** — novos campos aceitos:
```json
{
  "title": "string",
  "description": "string|null",
  "priority": "medium",
  "label": "back_end|front_end|mobile|tests|devops|dba|security|ux|null",
  "github_repo": "org/repo|null",
  "assigned_agent_id": "uuid|null"
}
```

**GET /tasks** — novo filtro:
```
?status=inbox&label=back_end
```

**PATCH /tasks/{id}** — novos campos atualizáveis:
```json
{
  "status": "string|null",
  "priority": "string|null",
  "label": "string|null",
  "github_repo": "string|null",
  "assigned_agent_id": "uuid|null",
  "title": "string|null",
  "description": "string|null"
}
```

**TaskResponse** — novo campo:
```json
{ "label": "back_end" }
```

---

## Frontend

### Create Task Dialog — novos campos

1. **Repositório** — dropdown populado de `GET /repositories`
   - Obrigatório quando label técnico selecionado
   - Placeholder: "Selecionar repositório..."

2. **Label/Track** — dropdown
   - Opções: `(nenhum) | back_end | front_end | mobile | tests | devops | dba | security | ux`

### Task Card (board)

- Substituir link GitHub issue por pill colorida com o label
- Exibir `github_repo` em texto menor abaixo do título
- Remover ícone ExternalLink de issue do GitHub

### Task List (tabela)

- Substituir coluna "Issue" por coluna "Label"
- Adicionar coluna "Repositório"

### Settings — Seção "Repositórios"

Nova seção na página `/settings`:
- Lista: nome, `org/repo`, branch default, status ativo/inativo
- Botão "Add Repository" com form inline
- Toggle ativo/inativo por repo
- Botão remover com confirmação

---

## Agentes — Mudanças nos arquivos de configuração

### Env vars injetadas em todos os pods

```yaml
# k8s Secret: panel-agent-credentials
PANEL_API_URL: http://clawdevs-panel-backend:8000/api
PANEL_TOKEN: <jwt-30-dias gerado via /auth/agent-token>
```

### Arquiteto — SKILL.md e TOOLS.md

**Antes:**
```bash
gh issue create --repo "$ACTIVE_GITHUB_REPOSITORY" \
  --title "TASK-XXX: ..." --label "back_end,task,P1" --body-file /tmp/task.md
```

**Depois:**
```bash
TASK_BODY=$(cat /tmp/task.md)
curl -s -X POST \
  -H "Authorization: Bearer $PANEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"TASK-XXX: ...\",\"label\":\"back_end\",\"github_repo\":\"$ACTIVE_GITHUB_REPOSITORY\",\"description\":\"$TASK_BODY\"}" \
  "$PANEL_API_URL/tasks"
```

Remover todas as referências a `gh issue create` de SKILL.md, TOOLS.md e AGENTS.md do Arquiteto.
Manter: `gh pr create`, `gh label`, `gh workflow`, `gh run view`.

### Agentes executores (Dev_Backend, Dev_Frontend, Dev_Mobile, QA_Engineer, DevOps_SRE, DBA_DataEngineer, Security_Engineer, UX_Designer)

**Poll de fila — Antes:**
```bash
gh issue list --state open --label back_end --limit 20 --repo "$ACTIVE_GITHUB_REPOSITORY"
```

**Poll de fila — Depois:**
```bash
curl -s -H "Authorization: Bearer $PANEL_TOKEN" \
  "$PANEL_API_URL/tasks?status=inbox&label=back_end&page_size=20" | jq '.items[]'
```

**Marcar em andamento — Antes:**
```bash
gh issue edit <number> --add-label "in-progress" --repo "$ACTIVE_GITHUB_REPOSITORY"
```

**Marcar em andamento — Depois:**
```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $PANEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}' \
  "$PANEL_API_URL/tasks/<task_id>"
```

**Concluir — Antes:**
```bash
gh issue close <number> --repo "$ACTIVE_GITHUB_REPOSITORY"
```

**Concluir — Depois:**
```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $PANEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"done"}' \
  "$PANEL_API_URL/tasks/<task_id>"
```

**Repo ativo — fonte de verdade:**
O campo `github_repo` da task substitui `active_repository.env`.
Agentes leem `task.github_repo` e usam em todos os comandos `gh --repo "$TASK_GITHUB_REPO"`.

### Labels por agente (mapeamento)

| Label na Task | Agente executor |
|---------------|-----------------|
| `back_end` | Dev_Backend |
| `front_end` | Dev_Frontend |
| `mobile` | Dev_Mobile |
| `tests` | QA_Engineer |
| `devops` | DevOps_SRE |
| `dba` | DBA_DataEngineer |
| `security` | Security_Engineer |
| `ux` | UX_Designer |

---

## Kubernetes

### Novo Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: panel-agent-credentials
  namespace: default
type: Opaque
stringData:
  PANEL_API_URL: "http://clawdevs-panel-backend:8000/api"
  PANEL_TOKEN: "<gerado via POST /auth/agent-token>"
```

### Patch nos pods de agentes

Adicionar `envFrom` referenciando `panel-agent-credentials` em todos os pods OpenClaw.

---

## Critérios de Aceitação

- [ ] Usuário cria task com título, descrição, label e repositório pelo control-panel
- [ ] Agentes criam tasks via `curl $PANEL_API_URL/tasks` com PANEL_TOKEN
- [ ] Agentes executores fazem poll via `GET /tasks?status=inbox&label=<label>`
- [ ] Agentes atualizam status via `PATCH /tasks/{id}` sem usar `gh issue`
- [ ] Repositórios cadastrados e gerenciados na tela de Settings
- [ ] Repos aparecem no dropdown do Create Task dialog
- [ ] Nenhum agente cria `gh issue` (verificável via exec audit log)
- [ ] `gh pr create`, `gh commit`, `gh workflow` continuam funcionando
- [ ] Token de agente (30 dias) gerado e injetado nos pods via Secret K8s
