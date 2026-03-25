# Tasks-First Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Substituir GitHub Issues por Control Panel Tasks como source of truth de orquestração dos agentes, com suporte a múltiplos repositórios.

**Architecture:** Nova tabela `repositories` no banco + campo `label` em `tasks`. Backend expõe `/repositories` CRUD e filtro por label em `/tasks`. Frontend ganha dropdowns de repo/label no Create Task e seção Repositories em Settings. Todos os AGENTS.md/TOOLS.md dos agentes trocam `gh issue` por `curl $PANEL_API_URL/tasks`.

**Tech Stack:** FastAPI + SQLModel + Alembic (backend), Next.js + React Query + Tailwind (frontend), YAML (K8s), Markdown (agent configs)

---

## Task 1: Migration — tabela `repositories` + coluna `label` em `tasks`

**Files:**
- Create: `control-panel/backend/migrations/versions/0004_repositories_and_task_label.py`

**Step 1: Criar arquivo de migration**

```python
"""repositories table and task label column

Revision ID: 0004
Revises: 0003_sessions_schema_update
Create Date: 2026-03-25
"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'repositories',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('default_branch', sa.String(), nullable=False, server_default='main'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('full_name'),
    )
    op.create_index('ix_repositories_is_active', 'repositories', ['is_active'])

    op.add_column('tasks', sa.Column('label', sa.String(), nullable=True))
    op.create_index('ix_tasks_label', 'tasks', ['label'])


def downgrade() -> None:
    op.drop_index('ix_tasks_label', 'tasks')
    op.drop_column('tasks', 'label')
    op.drop_index('ix_repositories_is_active', 'repositories')
    op.drop_table('repositories')
```

**Step 2: Verificar que a migration anterior existe**

```bash
ls control-panel/backend/migrations/versions/
```
Esperado: ver `0003_sessions_schema_update.py` listado.

**Step 3: Verificar `down_revision` correto**

Abrir `control-panel/backend/migrations/versions/0003_sessions_schema_update.py` e confirmar que `revision = '0003'`. Ajustar `down_revision` no arquivo novo se necessário.

**Step 4: Commit**

```bash
git add control-panel/backend/migrations/versions/0004_repositories_and_task_label.py
git commit -m "feat(db): add repositories table and task label column"
```

---

## Task 2: Model — `Repository` SQLModel

**Files:**
- Create: `control-panel/backend/app/models/repository.py`
- Modify: `control-panel/backend/app/models/__init__.py`

**Step 1: Criar o model**

```python
# control-panel/backend/app/models/repository.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Repository(SQLModel, table=True):
    __tablename__ = "repositories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    full_name: str = Field(unique=True, index=True)  # org/repo
    description: Optional[str] = None
    default_branch: str = Field(default="main")
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Step 2: Adicionar ao `__init__.py`**

Abrir `control-panel/backend/app/models/__init__.py` e adicionar:
```python
from .repository import Repository
```
E adicionar `"Repository"` ao `__all__`.

**Step 3: Commit**

```bash
git add control-panel/backend/app/models/repository.py \
        control-panel/backend/app/models/__init__.py
git commit -m "feat(models): add Repository SQLModel"
```

---

## Task 3: Model — adicionar campo `label` ao `Task`

**Files:**
- Modify: `control-panel/backend/app/models/task.py`

**Step 1: Adicionar o campo**

No arquivo `control-panel/backend/app/models/task.py`, localizar a linha:
```python
    github_repo: Optional[str] = None
```
E adicionar logo abaixo:
```python
    label: Optional[str] = Field(default=None, index=True)  # back_end|front_end|mobile|tests|devops|dba|security|ux
```

**Step 2: Commit**

```bash
git add control-panel/backend/app/models/task.py
git commit -m "feat(models): add label field to Task"
```

---

## Task 4: API — `/repositories` CRUD

**Files:**
- Create: `control-panel/backend/app/api/repositories.py`

**Step 1: Criar o router completo**

```python
# control-panel/backend/app/api/repositories.py
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.core.database import get_session
from app.api.deps import CurrentUser
from app.models import Repository

router = APIRouter()

VALID_LABELS = ["back_end", "front_end", "mobile", "tests", "devops", "dba", "security", "ux"]


class RepositoryResponse(BaseModel):
    id: str
    name: str
    full_name: str
    description: str | None
    default_branch: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CreateRepositoryRequest(BaseModel):
    name: str
    full_name: str  # org/repo
    description: str | None = None
    default_branch: str = "main"


class UpdateRepositoryRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    default_branch: str | None = None
    is_active: bool | None = None


class RepositoriesListResponse(BaseModel):
    items: list[RepositoryResponse]
    total: int


def _to_response(r: Repository) -> RepositoryResponse:
    return RepositoryResponse(
        id=str(r.id), name=r.name, full_name=r.full_name,
        description=r.description, default_branch=r.default_branch,
        is_active=r.is_active, created_at=r.created_at, updated_at=r.updated_at,
    )


@router.get("", response_model=RepositoriesListResponse)
async def list_repositories(
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
    include_inactive: bool = False,
):
    query = select(Repository).order_by(Repository.name)
    if not include_inactive:
        query = query.where(Repository.is_active == True)
    result = await session.exec(query)
    repos = result.all()
    return RepositoriesListResponse(items=[_to_response(r) for r in repos], total=len(repos))


@router.post("", response_model=RepositoryResponse, status_code=201)
async def create_repository(
    body: CreateRepositoryRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime, timezone
    # Check unique
    result = await session.exec(select(Repository).where(Repository.full_name == body.full_name))
    if result.first():
        raise HTTPException(status_code=409, detail="Repository already exists")
    repo = Repository(
        name=body.name,
        full_name=body.full_name,
        description=body.description,
        default_branch=body.default_branch,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(repo)
    await session.commit()
    await session.refresh(repo)
    return _to_response(repo)


@router.patch("/{repo_id}", response_model=RepositoryResponse)
async def update_repository(
    repo_id: str,
    body: UpdateRepositoryRequest,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    from datetime import datetime, timezone
    result = await session.exec(select(Repository).where(Repository.id == UUID(repo_id)))
    repo = result.first()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    if body.name is not None:
        repo.name = body.name
    if body.description is not None:
        repo.description = body.description
    if body.default_branch is not None:
        repo.default_branch = body.default_branch
    if body.is_active is not None:
        repo.is_active = body.is_active
    repo.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(repo)
    return _to_response(repo)


@router.delete("/{repo_id}", status_code=204)
async def delete_repository(
    repo_id: str,
    _: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.exec(select(Repository).where(Repository.id == UUID(repo_id)))
    repo = result.first()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    await session.delete(repo)
    await session.commit()
```

**Step 2: Commit**

```bash
git add control-panel/backend/app/api/repositories.py
git commit -m "feat(api): add /repositories CRUD endpoint"
```

---

## Task 5: API — Atualizar `/tasks` (label + novos campos)

**Files:**
- Modify: `control-panel/backend/app/api/tasks.py`

**Step 1: Adicionar `label` ao `TaskResponse`**

Localizar a classe `TaskResponse` e adicionar campo:
```python
    label: str | None
```

**Step 2: Adicionar campos ao `CreateTaskRequest`**

Localizar a classe `CreateTaskRequest` e adicionar:
```python
    label: str | None = None
    github_repo: str | None = None
```

**Step 3: Atualizar `UpdateTaskRequest`**

Adicionar os novos campos à classe:
```python
    title: str | None = None
    description: str | None = None
    label: str | None = None
    github_repo: str | None = None
```

**Step 4: Atualizar `list_tasks` — filtro por label**

Localizar a função `list_tasks`. Adicionar parâmetro:
```python
    label: Optional[str] = Query(None),
```
E adicionar filtro após o filtro de status existente:
```python
    if label:
        query = query.where(Task.label == label)
```

**Step 5: Atualizar `create_task` — salvar label e github_repo**

Na função `create_task`, após `priority=body.priority,` adicionar:
```python
        label=body.label,
        github_repo=body.github_repo,
```

**Step 6: Atualizar `update_task` — salvar novos campos**

Na função `update_task`, antes do `task.updated_at = ...` adicionar:
```python
    if body.title is not None:
        task.title = body.title
    if body.description is not None:
        task.description = body.description
    if body.label is not None:
        task.label = body.label
    if body.github_repo is not None:
        task.github_repo = body.github_repo
```

**Step 7: Adicionar `label` em todos os `TaskResponse(...)` nas funções**

Em cada lugar que constrói `TaskResponse(...)` nas três funções (`list_tasks`, `create_task`, `update_task`), adicionar:
```python
            label=t.label,  # ou task.label
```

**Step 8: Commit**

```bash
git add control-panel/backend/app/api/tasks.py
git commit -m "feat(api): add label filter and new fields to /tasks"
```

---

## Task 6: API — Endpoint `POST /auth/agent-token`

**Files:**
- Modify: `control-panel/backend/app/api/auth.py`

**Step 1: Adicionar o endpoint no `auth.py`**

Após o import de `create_access_token`, adicionar:
```python
from datetime import timedelta
```
(verificar se já existe; se sim, pular)

Localizar o final do arquivo e adicionar:
```python
@router.post("/agent-token", response_model=TokenResponse)
async def create_agent_token(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Gera JWT de 30 dias para uso dos agentes OpenClaw via curl."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    token = create_access_token(
        data={"sub": current_user.username, "type": "agent"},
        expires_delta=timedelta(days=30),
    )
    return TokenResponse(access_token=token)
```

**Step 2: Commit**

```bash
git add control-panel/backend/app/api/auth.py
git commit -m "feat(auth): add POST /auth/agent-token for 30-day agent JWT"
```

---

## Task 7: Registrar router `repositories` no `main.py`

**Files:**
- Modify: `control-panel/backend/app/main.py`

**Step 1: Adicionar import**

Localizar o bloco de imports de API e adicionar:
```python
from app.api import repositories as repositories_api
```

**Step 2: Registrar o router**

Logo após a linha `app.include_router(tasks_api.router, ...)`, adicionar:
```python
app.include_router(repositories_api.router, prefix="/repositories", tags=["repositories"])
```

**Step 3: Commit**

```bash
git add control-panel/backend/app/main.py
git commit -m "feat(app): register /repositories router"
```

---

## Task 8: Frontend — Seção Repositories na página Settings

**Files:**
- Modify: `control-panel/frontend/src/app/settings/page.tsx`

**Step 1: Adicionar tipos no topo do arquivo**

Após os tipos existentes (`SettingsInfo`, `ClusterInfo`, etc.), adicionar:
```typescript
interface Repository {
  id: string
  name: string
  full_name: string
  description?: string
  default_branch: string
  is_active: boolean
}

interface RepositoriesResponse {
  items: Repository[]
  total: number
}

interface CreateRepoPayload {
  name: string
  full_name: string
  description?: string
  default_branch: string
}
```

**Step 2: Adicionar fetchers**

Após os fetchers existentes, adicionar:
```typescript
const fetchRepositories = () =>
  customInstance<RepositoriesResponse>({
    url: "/repositories?include_inactive=true",
    method: "GET",
  })

const createRepository = (body: CreateRepoPayload) =>
  customInstance<Repository>({ url: "/repositories", method: "POST", data: body })

const updateRepository = (id: string, body: Partial<Repository>) =>
  customInstance<Repository>({ url: `/repositories/${id}`, method: "PATCH", data: body })

const deleteRepository = (id: string) =>
  customInstance<void>({ url: `/repositories/${id}`, method: "DELETE" })
```

**Step 3: Criar componente `RepositoriesSection`**

Adicionar antes do `export default function SettingsPage()`:
```typescript
function RepositoriesSection() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: "", full_name: "", description: "", default_branch: "main" })
  const [formError, setFormError] = useState("")

  const { data, isLoading } = useQuery({
    queryKey: ["repositories"],
    queryFn: fetchRepositories,
  })

  const createMutation = useMutation({
    mutationFn: createRepository,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repositories"] })
      setShowForm(false)
      setForm({ name: "", full_name: "", description: "", default_branch: "main" })
      setFormError("")
    },
    onError: () => setFormError("Falha ao criar repositório."),
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      updateRepository(id, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["repositories"] }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteRepository,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["repositories"] }),
  })

  const repos = data?.items ?? []

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-[hsl(var(--foreground))]">Repositórios cadastrados</span>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="px-3 py-1.5 text-xs rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 transition-opacity"
        >
          + Add Repository
        </button>
      </div>

      {showForm && (
        <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs text-[hsl(var(--muted-foreground))]">Nome *</label>
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="ClawDevs API"
                className="px-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-[hsl(var(--muted-foreground))]">org/repo *</label>
              <input
                value={form.full_name}
                onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
                placeholder="myorg/myrepo"
                className="px-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-[hsl(var(--muted-foreground))]">Branch default</label>
              <input
                value={form.default_branch}
                onChange={(e) => setForm((f) => ({ ...f, default_branch: e.target.value }))}
                placeholder="main"
                className="px-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-[hsl(var(--muted-foreground))]">Descrição</label>
              <input
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="Opcional"
                className="px-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
            </div>
          </div>
          {formError && <p className="text-xs text-red-400">{formError}</p>}
          <div className="flex gap-2 justify-end">
            <button
              onClick={() => { setShowForm(false); setFormError("") }}
              className="px-3 py-1.5 text-xs rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/30"
            >
              Cancelar
            </button>
            <button
              onClick={() => {
                if (!form.name.trim() || !form.full_name.trim()) {
                  setFormError("Nome e org/repo são obrigatórios.")
                  return
                }
                createMutation.mutate({
                  name: form.name.trim(),
                  full_name: form.full_name.trim(),
                  description: form.description.trim() || undefined,
                  default_branch: form.default_branch.trim() || "main",
                })
              }}
              disabled={createMutation.isPending}
              className="px-3 py-1.5 text-xs rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50"
            >
              {createMutation.isPending ? "Salvando…" : "Salvar"}
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="text-xs text-[hsl(var(--muted-foreground))]">Carregando…</div>
      ) : repos.length === 0 ? (
        <div className="text-xs text-[hsl(var(--muted-foreground))]">Nenhum repositório cadastrado.</div>
      ) : (
        <div className="flex flex-col gap-2">
          {repos.map((repo) => (
            <div
              key={repo.id}
              className="flex items-center justify-between rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-2.5"
            >
              <div className="flex flex-col">
                <span className="text-sm font-medium text-[hsl(var(--foreground))]">{repo.name}</span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {repo.full_name} · {repo.default_branch}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleMutation.mutate({ id: repo.id, is_active: !repo.is_active })}
                  className={`px-2 py-0.5 text-xs rounded-full transition-colors ${
                    repo.is_active
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      : "bg-[hsl(var(--muted))]/30 text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/50"
                  }`}
                >
                  {repo.is_active ? "Ativo" : "Inativo"}
                </button>
                <button
                  onClick={() => {
                    if (confirm(`Remover "${repo.name}"?`)) deleteMutation.mutate(repo.id)
                  }}
                  className="text-xs text-red-400 hover:text-red-300 transition-colors"
                >
                  Remover
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

**Step 4: Adicionar `useMutation` e `useQueryClient` nos imports**

Verificar se `useMutation` e `useQueryClient` já estão importados do `@tanstack/react-query`. Se não, adicionar.

**Step 5: Adicionar a seção `RepositoriesSection` no JSX da página**

Localizar onde os `<SectionDivider>` são renderizados no `return` do componente principal. Adicionar ao final, antes do fechamento do componente:
```tsx
<SectionDivider title="Repositórios" />
<RepositoriesSection />
```

**Step 6: Commit**

```bash
git add control-panel/frontend/src/app/settings/page.tsx
git commit -m "feat(frontend): add Repositories section to Settings page"
```

---

## Task 9: Frontend — Create Task Dialog com campos repo e label

**Files:**
- Modify: `control-panel/frontend/src/app/tasks/page.tsx`

**Step 1: Adicionar tipos**

Após a interface `Task` existente, adicionar:
```typescript
interface Repository {
  id: string
  name: string
  full_name: string
  default_branch: string
  is_active: boolean
}

interface RepositoriesResponse {
  items: Repository[]
  total: number
}
```

**Step 2: Atualizar `CreateTaskPayload`**

Localizar e atualizar:
```typescript
interface CreateTaskPayload {
  title: string
  description?: string
  priority?: string
  label?: string
  github_repo?: string
}
```

**Step 3: Adicionar fetcher de repositórios**

Após os fetchers existentes:
```typescript
const fetchRepositories = () =>
  customInstance<RepositoriesResponse>({ url: "/repositories", method: "GET" })
```

**Step 4: Definir labels disponíveis**

Após as constantes existentes:
```typescript
const LABELS = [
  { value: "", label: "(nenhum)" },
  { value: "back_end", label: "back_end" },
  { value: "front_end", label: "front_end" },
  { value: "mobile", label: "mobile" },
  { value: "tests", label: "tests" },
  { value: "devops", label: "devops" },
  { value: "dba", label: "dba" },
  { value: "security", label: "security" },
  { value: "ux", label: "ux" },
] as const

const LABEL_COLORS: Record<string, string> = {
  back_end: "#3B82F6",
  front_end: "#8B5CF6",
  mobile: "#EC4899",
  tests: "#10B981",
  devops: "#F59E0B",
  dba: "#6366F1",
  security: "#EF4444",
  ux: "#14B8A6",
}
```

**Step 5: Atualizar `CreateTaskDialog`**

Substituir toda a função `CreateTaskDialog` por versão com novos campos:
```typescript
function CreateTaskDialog({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [label, setLabel] = useState("")
  const [githubRepo, setGithubRepo] = useState("")
  const [error, setError] = useState("")

  const { data: reposData } = useQuery({
    queryKey: ["repositories"],
    queryFn: fetchRepositories,
  })
  const repos = reposData?.items ?? []

  const mutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => { onSuccess(); onClose() },
    onError: () => setError("Failed to create task. Please try again."),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) { setError("Title is required."); return }
    setError("")
    mutation.mutate({
      title: title.trim(),
      description: description.trim() || undefined,
      label: label || undefined,
      github_repo: githubRepo || undefined,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-[hsl(var(--foreground))]">Create Task</h2>
          <button onClick={onClose} className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]">
            <X className="h-4 w-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Title */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">
              Title <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Task title…"
              className="px-3 py-2 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
            />
          </div>

          {/* Label + Repo row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Label / Track</label>
              <select
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                className="px-3 py-2 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              >
                {LABELS.map((l) => (
                  <option key={l.value} value={l.value}>{l.label}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Repositório</label>
              <select
                value={githubRepo}
                onChange={(e) => setGithubRepo(e.target.value)}
                className="px-3 py-2 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              >
                <option value="">Selecionar…</option>
                {repos.map((r) => (
                  <option key={r.id} value={r.full_name}>{r.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Description */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description…"
              rows={4}
              className="px-3 py-2 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))] resize-none"
            />
          </div>

          {error && <p className="text-xs text-red-400">{error}</p>}
          <div className="flex items-center justify-end gap-2 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-lg border border-[hsl(var(--border))] text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/30"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="px-4 py-2 text-sm rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50"
            >
              {mutation.isPending ? "Creating…" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
```

**Step 6: Commit**

```bash
git add control-panel/frontend/src/app/tasks/page.tsx
git commit -m "feat(frontend): add label and repo fields to Create Task dialog"
```

---

## Task 10: Frontend — Task Card e List com label pill e repo; remover GitHub issue link

**Files:**
- Modify: `control-panel/frontend/src/app/tasks/page.tsx`

**Step 1: Atualizar a interface `Task`**

Adicionar o campo `label` e remover `github_issue_number` (ou manter como opcional):
```typescript
interface Task {
  id: string
  title: string
  description?: string
  status: "inbox" | "in_progress" | "done" | "cancelled"
  priority?: "critical" | "high" | "medium" | "low"
  assigned_agent_slug?: string
  github_repo?: string
  github_issue_number?: number  // manter por retrocompatibilidade, mas não exibir
  label?: string
  created_at: string
}
```

**Step 2: Atualizar `TaskCard` — substituir link GitHub por label pill e repo**

Substituir o bloco `{task.github_issue_number && ...}` no componente `TaskCard` por:
```tsx
{/* Label pill */}
{task.label && (
  <span
    className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium"
    style={{
      backgroundColor: `${LABEL_COLORS[task.label] ?? "#9CA3AF"}1A`,
      color: LABEL_COLORS[task.label] ?? "#9CA3AF",
      border: `1px solid ${LABEL_COLORS[task.label] ?? "#9CA3AF"}33`,
    }}
  >
    {task.label}
  </span>
)}
```

E após o título do card, adicionar:
```tsx
{task.github_repo && (
  <p className="text-[10px] text-[hsl(var(--muted-foreground))] truncate">{task.github_repo}</p>
)}
```

**Step 3: Atualizar List view — substituir coluna "Issue" por "Label" e adicionar "Repo"**

Na tabela (`<thead>` e `<tbody>`):
- Renomear `<th>Issue</th>` para `<th>Label</th>`
- Substituir célula de issue por:
```tsx
<td className="px-4 py-3">
  {task.label ? (
    <span
      className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
      style={{
        backgroundColor: `${LABEL_COLORS[task.label] ?? "#9CA3AF"}1A`,
        color: LABEL_COLORS[task.label] ?? "#9CA3AF",
        border: `1px solid ${LABEL_COLORS[task.label] ?? "#9CA3AF"}33`,
      }}
    >
      {task.label}
    </span>
  ) : (
    <span className="text-[hsl(var(--muted-foreground))] text-xs">—</span>
  )}
</td>
```

- Adicionar coluna `<th>Repo</th>` e célula correspondente:
```tsx
<td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))] truncate max-w-[120px]">
  {task.github_repo ?? "—"}
</td>
```

**Step 4: Remover o import de `ExternalLink` se não for mais usado**

Verificar se `ExternalLink` é referenciado em algum outro lugar. Se não, remover do import do lucide.

**Step 5: Commit**

```bash
git add control-panel/frontend/src/app/tasks/page.tsx
git commit -m "feat(frontend): replace github issue link with label pill and repo in task views"
```

---

## Task 11: Agent — Arquiteto: atualizar TOOLS.md, SKILL.md, AGENTS.md, HEARTBEAT.md

**Files:**
- Modify: `k8s/base/openclaw-config/arquiteto/TOOLS.md`
- Modify: `k8s/base/openclaw-config/arquiteto/SKILL.md`
- Modify: `k8s/base/openclaw-config/arquiteto/AGENTS.md`
- Modify: `k8s/base/openclaw-config/arquiteto/HEARTBEAT.md`

### TOOLS.md

**Step 1: Adicionar ferramentas de panel API**

Localizar a seção `## tools_disponiveis` e adicionar após `exec("gh <args>")`:
```markdown
- `exec("curl -s -X POST -H 'Authorization: Bearer $PANEL_TOKEN' -H 'Content-Type: application/json' -d '<json>' $PANEL_API_URL/tasks")`: Criar task no control panel.
- `exec("curl -s -H 'Authorization: Bearer $PANEL_TOKEN' '$PANEL_API_URL/tasks?status=inbox&label=<label>'")`: Listar tasks do panel.
- `exec("curl -s -X PATCH -H 'Authorization: Bearer $PANEL_TOKEN' -H 'Content-Type: application/json' -d '<json>' $PANEL_API_URL/tasks/<id>")`: Atualizar status/campos de task.
```

**Step 2: Atualizar regras de uso — substituir criação de issue por criação de task**

Localizar a linha:
```
- Ordem obrigatória de publicação: `docs -> commit -> issues -> validação -> session_finished`.
```
Substituir por:
```markdown
- Ordem obrigatória de publicação: `docs -> commit -> panel_task -> validação -> session_finished`.
- Criar tasks no control panel via `$PANEL_API_URL/tasks` (POST) — nunca `gh issue create`.
- Campos obrigatórios ao criar task: `title`, `label` (trilha), `github_repo` (repo ativo).
- Após criar task: registrar `task_id` retornado para atualizações posteriores.
- Usar `$PANEL_API_URL` e `$PANEL_TOKEN` das env vars — nunca hardcodar URL ou token.
```

**Step 3: Atualizar `github_permissions` — remover `gh issue create`**

Localizar:
```
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
```
Substituir por:
```markdown
- **Operações permitidas:** `gh pr`, `gh label`, `gh workflow`, `gh run view` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
- **Proibido:** `gh issue create`, `gh issue edit`, `gh issue close` — usar control panel API
```

**Step 4: Adicionar exemplo de criação de task via panel**

Na seção de exemplos ou após as regras, adicionar:
```markdown
## Criar task no control panel (substituiu gh issue create)

```bash
# Ler conteúdo da task
TASK_BODY=$(cat /data/openclaw/backlog/implementation/TASK-XXX.md | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")

# Criar task no control panel
TASK_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $PANEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"TASK-XXX: <slug>\",\"label\":\"back_end\",\"github_repo\":\"$ACTIVE_GITHUB_REPOSITORY\",\"description\":$TASK_BODY}" \
  "$PANEL_API_URL/tasks")

TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id')
echo "Task criada: $TASK_ID"
```
```

### SKILL.md

**Step 5: Localizar todas as ocorrências de `gh issue create` no SKILL.md**

```bash
grep -n "gh issue create" k8s/base/openclaw-config/arquiteto/SKILL.md
```

**Step 6: Para cada ocorrência, substituir pelo equivalente curl para panel API**

Padrão de substituição:
```bash
# ANTES:
gh issue create --repo "$GITHUB_REPOSITORY" \
  --title "TASK-XXX: ..." \
  --label "back_end,task,P1" \
  --body-file /tmp/task.md

# DEPOIS:
TASK_BODY=$(cat /tmp/task.md | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
curl -s -X POST \
  -H "Authorization: Bearer $PANEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"TASK-XXX: ...\",\"label\":\"back_end\",\"github_repo\":\"$ACTIVE_GITHUB_REPOSITORY\",\"description\":$TASK_BODY}" \
  "$PANEL_API_URL/tasks"
```

**Step 7: Atualizar fluxograma do SKILL.md que referencia criação de issue**

Localizar a linha com `gh issue create com labels e referências` no diagrama mermaid/dot e substituir por:
```
panel_task_create["POST $PANEL_API_URL/tasks com label e github_repo"]
```

### AGENTS.md

**Step 8: Atualizar `core_objectives`**

Localizar:
```
  - "Assumir ownership de TASK tecnica e GitHub issues"
```
Substituir por:
```yaml
  - "Assumir ownership de TASK tecnica e tasks no control panel"
```

**Step 9: Atualizar `docs_commit_issue_orchestration`**

Localizar quality_gates com `"ordem obrigatoria: docs -> commit -> issues -> ..."` e substituir:
```yaml
      - "ordem obrigatoria: docs -> commit -> panel_task -> validacao -> session_finished"
      - "nao criar panel_task antes do commit de docs"
      - "registrar task_id retornado pelo panel como evidencia"
```

**Step 10: Atualizar `github_integration` capability**

Remover referência a `gh issue create`. Manter apenas `gh pr`, `gh label`, `gh workflow`.

### HEARTBEAT.md

**Step 11: Atualizar referências a issues no heartbeat**

Localizar:
```
   - Issues com label `tests` sem pickup pelo QA_Engineer > 2h: notificar QA_Engineer.
```
Substituir por:
```markdown
   - Tasks do panel com label `tests` e status `inbox` > 2h sem mudança: notificar QA_Engineer.
   - Tasks do panel com label `devops` e status `inbox` > 1h sem mudança: notificar DevOps_SRE.
```

Localizar referência ao pipeline `docs/issue` e atualizar:
```markdown
5. Pipeline docs/task:
   - Se existir documento novo sem commit em `implementation/docs`: alertar PO.
   - Se task criada no panel sem commit prévio de docs: marcar não-conforme e escalar PO.
```

**Step 12: Commit**

```bash
git add k8s/base/openclaw-config/arquiteto/TOOLS.md \
        k8s/base/openclaw-config/arquiteto/SKILL.md \
        k8s/base/openclaw-config/arquiteto/AGENTS.md \
        k8s/base/openclaw-config/arquiteto/HEARTBEAT.md
git commit -m "feat(agents/arquiteto): replace gh issue create with panel API task creation"
```

---

## Task 12: Agentes executores — atualizar TOOLS.md de cada agente (8 agentes)

**Agentes:** `dev_backend`, `dev_frontend`, `dev_mobile`, `qa_engineer`, `devops_sre`, `dba_data_engineer`, `security_engineer`, `ux_designer`

**Files (cada agente):**
- Modify: `k8s/base/openclaw-config/<agente>/TOOLS.md`
- Modify: `k8s/base/openclaw-config/<agente>/AGENTS.md`

### Para cada agente, seguir os mesmos passos:

**Step 1: Atualizar `tools_disponiveis` no TOOLS.md**

Adicionar após `exec("gh <args>")`:
```markdown
- `exec("curl -s -H 'Authorization: Bearer $PANEL_TOKEN' '$PANEL_API_URL/tasks?status=inbox&label=<minha_label>&page_size=20'")`: Poll de fila de tasks no control panel.
- `exec("curl -s -X PATCH -H 'Authorization: Bearer $PANEL_TOKEN' -H 'Content-Type: application/json' -d '<json>' $PANEL_API_URL/tasks/<id>")`: Atualizar status da task.
- `exec("curl -s -X POST -H 'Authorization: Bearer $PANEL_TOKEN' -H 'Content-Type: application/json' -d '<json>' $PANEL_API_URL/tasks")`: Criar nova task (sub-tasks, bugs encontrados, etc.).
```

**Step 2: Atualizar `regras_de_uso` — substituir poll GitHub por poll panel**

Localizar o bloco de "Poll de fila GitHub" específico de cada agente. Exemplos:

Para `dev_backend`:
```markdown
# ANTES:
- Poll de fila GitHub 1x por hora:
  - exemplo: `gh issue list --state open --label back_end --limit 20 --repo "$ACTIVE_GITHUB_REPOSITORY"`
- Processar somente label `back_end`.

# DEPOIS:
- Poll de fila control panel 1x por hora:
  - exemplo: `curl -s -H "Authorization: Bearer $PANEL_TOKEN" "$PANEL_API_URL/tasks?status=inbox&label=back_end&page_size=20"`
- Ao pegar uma task: `PATCH /tasks/<id>` com `{"status":"in_progress"}` imediatamente.
- Ao concluir: `PATCH /tasks/<id>` com `{"status":"done"}`.
- Processar somente label `back_end`. TASK_GITHUB_REPO = campo `github_repo` da task.
```

Mapeamento de label por agente:
| Agente | Label |
|--------|-------|
| dev_backend | `back_end` |
| dev_frontend | `front_end` |
| dev_mobile | `mobile` |
| qa_engineer | `tests` |
| devops_sre | `devops` |
| dba_data_engineer | `dba` |
| security_engineer | `security` |
| ux_designer | `ux` |

**Step 3: Atualizar `github_permissions` — remover `gh issue create/close/edit`**

Para todos os agentes executores, localizar:
```
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow`
```
Substituir por:
```markdown
- **Operações permitidas:** `gh pr`, `gh label`, `gh workflow`, `gh run view` (somente `--repo "$TASK_GITHUB_REPO"`)
- **Proibido:** `gh issue create`, `gh issue edit`, `gh issue close` — usar control panel API
- **Repo ativo:** usar `$TASK_GITHUB_REPO` (campo `github_repo` da task) em vez de `$ACTIVE_GITHUB_REPOSITORY`
```

**Step 4: Atualizar AGENTS.md de cada executor**

Nos `constraints` / "NÃO faz", adicionar:
```yaml
  - "NÃO usar gh issue create/edit/close — gerenciar tasks pelo control panel API"
  - "SEMPRE ler github_repo da task para definir o repo ativo da sessão"
```

Nos `rules` de polling, substituir referência a GitHub issues pelo panel:
```yaml
  - id: panel_queue_polling
    description: "Polling de tasks do control panel com label <label>"
    when: ["intent == 'poll_panel_queue'"]
    actions:
      - "consultar panel: GET $PANEL_API_URL/tasks?status=inbox&label=<label>&page_size=20"
      - "se não houver task elegível: encerrar ciclo e manter standby"
      - "ao pegar task: PATCH status=in_progress imediatamente"
      - "usar task.github_repo como repo ativo para todos os comandos gh/git"
```

**Step 5: Commit por agente (ou todos juntos)**

```bash
git add k8s/base/openclaw-config/dev_backend/ \
        k8s/base/openclaw-config/dev_frontend/ \
        k8s/base/openclaw-config/dev_mobile/ \
        k8s/base/openclaw-config/qa_engineer/ \
        k8s/base/openclaw-config/devops_sre/ \
        k8s/base/openclaw-config/dba_data_engineer/ \
        k8s/base/openclaw-config/security_engineer/ \
        k8s/base/openclaw-config/ux_designer/
git commit -m "feat(agents): replace gh issue polling with control panel API for all executor agents"
```

---

## Task 13: Kubernetes — Secret `panel-agent-credentials` + patch nos pods

**Files:**
- Create: `k8s/base/panel-agent-credentials-secret.yaml`
- Modify: `k8s/base/openclaw-pod.yaml`
- Modify: `k8s/base/kustomization.yaml`

**Step 1: Criar o Secret**

```yaml
# k8s/base/panel-agent-credentials-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: panel-agent-credentials
  namespace: default
type: Opaque
stringData:
  PANEL_API_URL: "http://clawdevs-panel-backend:8000/api"
  PANEL_TOKEN: "PLACEHOLDER_REPLACE_WITH_REAL_TOKEN"
```

> **Nota:** O valor de `PANEL_TOKEN` deve ser substituído pelo token real gerado via
> `POST /auth/agent-token` após o deploy do backend. Use `kubectl create secret` ou
> `make secrets-apply` para substituir sem committar o token.

**Step 2: Abrir `k8s/base/openclaw-pod.yaml`**

Localizar o bloco `env:` do container principal do pod OpenClaw (onde estão as variáveis `GH_TOKEN`, `GITHUB_ORG`, etc.).

Adicionar as duas variáveis após as existentes:
```yaml
            - name: PANEL_API_URL
              valueFrom:
                secretKeyRef:
                  name: panel-agent-credentials
                  key: PANEL_API_URL
            - name: PANEL_TOKEN
              valueFrom:
                secretKeyRef:
                  name: panel-agent-credentials
                  key: PANEL_TOKEN
```

**Step 3: Registrar o novo Secret no kustomization**

Abrir `k8s/base/kustomization.yaml`. Na lista de `resources:`, adicionar:
```yaml
- panel-agent-credentials-secret.yaml
```

**Step 4: Commit**

```bash
git add k8s/base/panel-agent-credentials-secret.yaml \
        k8s/base/openclaw-pod.yaml \
        k8s/base/kustomization.yaml
git commit -m "feat(k8s): add panel-agent-credentials secret and env vars to openclaw pod"
```

---

## Task 14: Deploy e validação end-to-end

**Step 1: Aplicar migration no banco**

```bash
# dentro do pod do backend ou via kubectl exec
kubectl exec -it <panel-backend-pod> -- alembic upgrade head
```
Esperado: migration `0004` aplicada sem erro.

**Step 2: Gerar token de agente**

```bash
# Login para obter token admin
TOKEN=$(curl -s -X POST http://127.0.0.1:50160/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<senha>"}' | jq -r '.access_token')

# Gerar token de agente (30 dias)
AGENT_TOKEN=$(curl -s -X POST http://127.0.0.1:50160/api/auth/agent-token \
  -H "Authorization: Bearer $TOKEN" | jq -r '.access_token')

echo "AGENT_TOKEN=$AGENT_TOKEN"
```

**Step 3: Aplicar o token real no Secret K8s**

```bash
kubectl create secret generic panel-agent-credentials \
  --from-literal=PANEL_API_URL="http://clawdevs-panel-backend:8000/api" \
  --from-literal=PANEL_TOKEN="$AGENT_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -
```

**Step 4: Reiniciar pod OpenClaw para carregar novas env vars**

```bash
kubectl rollout restart deployment/openclaw  # ou o nome correto do deployment
```

**Step 5: Testar criação de repositório via UI**

1. Abrir http://127.0.0.1:50160/settings
2. Clicar "Add Repository"
3. Preencher: Nome = "Test Repo", org/repo = "test-org/test-repo", branch = "main"
4. Clicar Salvar
5. Verificar que repo aparece na lista

**Step 6: Testar criação de task com label e repo via UI**

1. Abrir http://127.0.0.1:50160/tasks
2. Clicar "+ Create Task"
3. Preencher: Título = "Test Task", Label = "back_end", Repositório = "test-org/test-repo"
4. Clicar Create
5. Verificar que card aparece no Inbox com pill `back_end` e repo abaixo do título

**Step 7: Testar poll via API (simular agente)**

```bash
curl -s -H "Authorization: Bearer $AGENT_TOKEN" \
  "http://127.0.0.1:50160/api/tasks?status=inbox&label=back_end" | jq '.items[].title'
```
Esperado: `"Test Task"` listada.

**Step 8: Testar atualização de status via API (simular agente marcando in_progress)**

```bash
TASK_ID=$(curl -s -H "Authorization: Bearer $AGENT_TOKEN" \
  "http://127.0.0.1:50160/api/tasks?status=inbox&label=back_end" | jq -r '.items[0].id')

curl -s -X PATCH \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}' \
  "http://127.0.0.1:50160/api/tasks/$TASK_ID" | jq '.status'
```
Esperado: `"in_progress"`.

**Step 9: Verificar que task saiu do Inbox no board**

Recarregar http://127.0.0.1:50160/tasks e confirmar que a task está na coluna "In Progress".

**Step 10: Commit final se houver ajustes**

```bash
git add -A
git commit -m "fix(deploy): post-deploy adjustments after validation"
```

---

## Checklist Final

- [ ] Migration `0004` aplicada (`repositories` table + `tasks.label` column)
- [ ] `GET /repositories` retorna lista
- [ ] `POST /repositories` cria repo, 409 em duplicata
- [ ] `PATCH /tasks` aceita `label` e `github_repo`
- [ ] `GET /tasks?label=back_end` filtra corretamente
- [ ] `POST /auth/agent-token` retorna JWT com 30 dias
- [ ] Create Task dialog mostra dropdowns de label e repo
- [ ] Task card mostra label pill colorida e github_repo
- [ ] Lista de tasks mostra coluna Label (sem coluna Issue)
- [ ] Settings mostra seção Repositories com CRUD
- [ ] TOOLS.md do Arquiteto sem `gh issue create`
- [ ] TOOLS.md dos 8 agentes executores usando panel API para poll
- [ ] K8s Secret `panel-agent-credentials` criado com token real
- [ ] Pod OpenClaw reiniciado com `PANEL_API_URL` e `PANEL_TOKEN` injetados
- [ ] Agente consegue listar tasks via `curl $PANEL_API_URL/tasks?label=back_end`
- [ ] Agente consegue atualizar status via `PATCH /tasks/{id}`
