# ClawDevs AI Control Panel — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Construir um painel de controle web completo embedded no cluster Kubernetes do ClawDevs AI, cobrindo observabilidade, gestão de agentes, aprovações, tarefas, SDD workflow, memória e status do cluster.

**Architecture:** FastAPI (Python 3.12) + Next.js 16.2 (React 19) separados, comunicando via REST + WebSockets. PostgreSQL 18 para persistência, Redis 8 para pub/sub realtime. Backend monta o PVC do OpenClaw como read-only para sync de memória e artefatos SDD. Auth JWT local sem dependência externa.

**Tech Stack:** FastAPI 0.135.1, SQLModel 0.0.37, Alembic 1.18.4, uv 0.10.12, Next.js 16.2.0, React 19.2.4, Tailwind CSS 4.2.2, shadcn/ui 4.1.0, TanStack Query 5.94.5, Orval 8.5.3, Recharts 3.8.0, PostgreSQL 18-alpine, Redis 8-alpine.

**Design Doc:** `docs/plans/2026-03-22-control-panel-design.md`

---

## Phase 1: Infraestrutura Kubernetes

### Task 1: K8s Manifests — PostgreSQL + Redis

**Files:**
- Create: `k8s/base/control-panel/kustomization.yaml`
- Create: `k8s/base/control-panel/postgres-statefulset.yaml`
- Create: `k8s/base/control-panel/redis-deployment.yaml`
- Create: `k8s/base/control-panel/services.yaml`
- Modify: `k8s/base/kustomization.yaml` (adicionar control-panel)
- Modify: `k8s/.env.example` (adicionar vars do painel)

**Step 1: Criar diretório**
```bash
mkdir -p k8s/base/control-panel
```

**Step 2: Criar `k8s/base/control-panel/kustomization.yaml`**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - postgres-statefulset.yaml
  - redis-deployment.yaml
  - backend-deployment.yaml
  - frontend-deployment.yaml
  - worker-deployment.yaml
  - services.yaml
  - serviceaccount.yaml
  - clusterrole.yaml
  - clusterrolebinding.yaml
```

**Step 3: Criar `k8s/base/control-panel/postgres-statefulset.yaml`**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: clawdevs-panel-db
  labels:
    app: clawdevs-panel-db
spec:
  serviceName: clawdevs-panel-db
  replicas: 1
  selector:
    matchLabels:
      app: clawdevs-panel-db
  template:
    metadata:
      labels:
        app: clawdevs-panel-db
    spec:
      containers:
        - name: postgres
          image: postgres:18-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: clawdevs_panel
            - name: POSTGRES_USER
              value: panel
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: clawdevs-panel-auth
                  key: PANEL_DB_PASSWORD
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              cpu: 500m
              memory: 1Gi
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "panel", "-d", "clawdevs_panel"]
            initialDelaySeconds: 5
            periodSeconds: 5
          volumeMounts:
            - name: panel-db-data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: panel-db-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

**Step 4: Criar `k8s/base/control-panel/redis-deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clawdevs-panel-redis
  labels:
    app: clawdevs-panel-redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: clawdevs-panel-redis
  template:
    metadata:
      labels:
        app: clawdevs-panel-redis
    spec:
      containers:
        - name: redis
          image: redis:8-alpine
          ports:
            - containerPort: 6379
          command: ["redis-server", "--requirepass", "$(REDIS_PASSWORD)"]
          env:
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: clawdevs-panel-auth
                  key: PANEL_REDIS_PASSWORD
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
          readinessProbe:
            exec:
              command: ["redis-cli", "ping"]
            initialDelaySeconds: 3
            periodSeconds: 5
```

**Step 5: Adicionar vars ao `.env.example`**
```bash
# --- Control Panel ---
PANEL_SECRET_KEY=change-me-very-long-random-string
PANEL_ADMIN_USERNAME=admin
PANEL_ADMIN_PASSWORD=change-me
PANEL_DB_PASSWORD=change-me-db
PANEL_REDIS_PASSWORD=change-me-redis
```

**Step 6: Adicionar control-panel ao `k8s/base/kustomization.yaml`**
Adicionar `- control-panel/` na seção `resources:`.

**Step 7: Commit**
```bash
git add k8s/base/control-panel/ k8s/base/kustomization.yaml k8s/.env.example
git commit -m "feat(k8s): add control-panel postgres and redis manifests"
```

---

### Task 2: K8s RBAC + ServiceAccount

**Files:**
- Create: `k8s/base/control-panel/serviceaccount.yaml`
- Create: `k8s/base/control-panel/clusterrole.yaml`
- Create: `k8s/base/control-panel/clusterrolebinding.yaml`

**Step 1: Criar `serviceaccount.yaml`**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: clawdevs-panel
  namespace: default
```

**Step 2: Criar `clusterrole.yaml`**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: clawdevs-panel-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "events", "persistentvolumeclaims", "services", "nodes"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "statefulsets", "replicasets"]
    verbs: ["get", "list", "watch"]
```

**Step 3: Criar `clusterrolebinding.yaml`**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: clawdevs-panel-reader-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: clawdevs-panel-reader
subjects:
  - kind: ServiceAccount
    name: clawdevs-panel
    namespace: default
```

**Step 4: Commit**
```bash
git add k8s/base/control-panel/serviceaccount.yaml k8s/base/control-panel/clusterrole.yaml k8s/base/control-panel/clusterrolebinding.yaml
git commit -m "feat(k8s): add RBAC serviceaccount for panel in-cluster K8s API access"
```

---

## Phase 2: Backend Scaffold

### Task 3: Backend — Estrutura e Dependências

**Files:**
- Create: `control-panel/backend/pyproject.toml`
- Create: `control-panel/backend/Dockerfile`
- Create: `control-panel/backend/alembic.ini`
- Create: `control-panel/backend/app/__init__.py`
- Create: `control-panel/backend/app/main.py`
- Create: `control-panel/backend/app/core/__init__.py`
- Create: `control-panel/backend/app/core/config.py`

**Step 1: Criar `control-panel/backend/pyproject.toml`**
```toml
[project]
name = "clawdevs-panel-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.135.1",
    "uvicorn[standard]==0.34.0",
    "sqlmodel==0.0.37",
    "alembic==1.18.4",
    "asyncpg==0.30.0",
    "psycopg[binary]==3.2.4",
    "redis[hiredis]==5.3.0",
    "python-jose[cryptography]==3.5.0",
    "passlib[bcrypt]==1.7.4",
    "httpx==0.28.1",
    "kubernetes==32.0.1",
    "watchdog==6.0.0",
    "fastapi-pagination==0.12.36",
    "sse-starlette==2.3.0",
    "rq==2.6.0",
    "python-multipart==0.0.20",
    "pydantic-settings==2.8.2",
]

[project.optional-dependencies]
dev = [
    "pytest==8.4.0",
    "pytest-asyncio==0.25.3",
    "httpx==0.28.1",
    "pytest-cov==6.1.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 2: Criar `control-panel/backend/Dockerfile`**
```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.10.12 /uv /usr/local/bin/uv

WORKDIR /app

# Install deps
COPY pyproject.toml .
RUN uv pip install --system --no-cache -e .

# Copy source
COPY . .

# Non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 3: Criar `control-panel/backend/app/core/config.py`**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://panel:password@clawdevs-panel-db:5432/clawdevs_panel"

    # Redis
    redis_url: str = "redis://:password@clawdevs-panel-redis:6379/0"

    # Auth
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Admin bootstrap
    admin_username: str = "admin"
    admin_password: str = "change-me"

    # OpenClaw gateway
    openclaw_gateway_url: str = "http://openclaw:18789"
    openclaw_gateway_token: str = ""

    # GitHub
    github_token: str = ""
    github_org: str = ""
    github_default_repository: str = ""

    # OpenClaw data path (PVC mounted read-only)
    openclaw_data_path: str = "/data/openclaw"

    # Kubernetes
    k8s_namespace: str = "default"

    class Config:
        env_file = ".env"
        env_prefix = "PANEL_"
        # Allow OPENCLAW_ and GITHUB_ prefixes too
        extra = "allow"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Step 4: Criar `control-panel/backend/app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="ClawDevs Panel API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://clawdevs-panel-frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)


@app.get("/healthz")
async def health():
    return {"status": "ok"}


# Routers são registrados nas tasks seguintes
```

**Step 5: Testar que a app sobe**
```bash
cd control-panel/backend
uv pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
# Esperado: "Application startup complete" em http://localhost:8000/healthz → {"status":"ok"}
```

**Step 6: Commit**
```bash
git add control-panel/backend/
git commit -m "feat(backend): scaffold FastAPI app with config and health endpoint"
```

---

### Task 4: Backend — Database + Modelos + Migrations

**Files:**
- Create: `control-panel/backend/app/core/database.py`
- Create: `control-panel/backend/app/models/__init__.py`
- Create: `control-panel/backend/app/models/user.py`
- Create: `control-panel/backend/app/models/agent.py`
- Create: `control-panel/backend/app/models/session.py`
- Create: `control-panel/backend/app/models/approval.py`
- Create: `control-panel/backend/app/models/task.py`
- Create: `control-panel/backend/app/models/sdd_artifact.py`
- Create: `control-panel/backend/app/models/memory_entry.py`
- Create: `control-panel/backend/app/models/cron_execution.py`
- Create: `control-panel/backend/app/models/activity_event.py`
- Create: `control-panel/backend/app/models/metric.py`
- Create: `control-panel/backend/alembic.ini`
- Create: `control-panel/backend/migrations/env.py`

**Step 1: Criar `app/core/database.py`**
```python
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False, future=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Step 2: Criar `app/models/agent.py`**
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Agent(SQLModel, table=True):
    __tablename__ = "agents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    slug: str = Field(unique=True, index=True)  # ceo, po, arquiteto, ...
    display_name: str
    role: str
    avatar_url: Optional[str] = None
    status: str = Field(default="unknown")  # active|inactive|error|unknown
    current_model: Optional[str] = None
    openclaw_session_id: Optional[str] = None
    last_heartbeat_at: Optional[datetime] = None
    cron_expression: Optional[str] = None
    cron_last_run_at: Optional[datetime] = None
    cron_next_run_at: Optional[datetime] = None
    cron_status: str = Field(default="idle")  # idle|running|error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Step 3: Criar `app/models/user.py`**
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="viewer")  # admin|viewer
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Step 4: Criar `app/models/approval.py`**
```python
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class Approval(SQLModel, table=True):
    __tablename__ = "approvals"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id")
    openclaw_approval_id: Optional[str] = Field(default=None, index=True)
    action_type: str
    payload: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    confidence: Optional[float] = None
    rubric_scores: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    status: str = Field(default="pending")  # pending|approved|rejected
    decided_by_id: Optional[UUID] = Field(default=None, foreign_key="users.id")
    justification: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Step 5: Criar demais modelos** (session, task, sdd_artifact, memory_entry, cron_execution, activity_event, metric) seguindo o mesmo padrão SQLModel. Ver design doc para campos completos.

**Step 6: Criar `app/models/__init__.py`** importando todos os modelos para garantir registro no metadata:
```python
from .user import User
from .agent import Agent
from .session import Session
from .approval import Approval
from .task import Task
from .sdd_artifact import SddArtifact
from .memory_entry import MemoryEntry
from .cron_execution import CronExecution
from .activity_event import ActivityEvent
from .metric import Metric

__all__ = [
    "User", "Agent", "Session", "Approval", "Task",
    "SddArtifact", "MemoryEntry", "CronExecution",
    "ActivityEvent", "Metric",
]
```

**Step 7: Inicializar Alembic**
```bash
cd control-panel/backend
alembic init migrations
# Editar migrations/env.py para usar async engine e importar os models
```

**Step 8: Gerar e rodar primeira migration**
```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
# Esperado: todas as tabelas criadas no PostgreSQL
```

**Step 9: Escrever teste dos modelos**
```bash
mkdir -p tests
```
```python
# tests/test_models.py
import pytest
from sqlmodel import select
from app.models import Agent


@pytest.mark.asyncio
async def test_agent_model(db_session):
    agent = Agent(slug="ceo", display_name="Victor", role="CEO")
    db_session.add(agent)
    await db_session.commit()
    result = await db_session.exec(select(Agent).where(Agent.slug == "ceo"))
    found = result.first()
    assert found.display_name == "Victor"
```

**Step 10: Rodar testes**
```bash
pytest tests/test_models.py -v
# Esperado: PASS
```

**Step 11: Commit**
```bash
git add control-panel/backend/app/models/ control-panel/backend/migrations/ control-panel/backend/alembic.ini tests/
git commit -m "feat(backend): add SQLModel models and Alembic migrations for all entities"
```

---

### Task 5: Backend — Auth (JWT Local)

**Files:**
- Create: `control-panel/backend/app/core/auth.py`
- Create: `control-panel/backend/app/api/auth.py`
- Create: `control-panel/backend/app/api/deps.py`
- Create: `control-panel/backend/tests/test_auth.py`

**Step 1: Escrever teste falhando**
```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post("/auth/login", json={
        "username": "admin",
        "password": "test-password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    response = await client.post("/auth/login", json={
        "username": "admin",
        "password": "wrong"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token(client, auth_token):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
```

**Step 2: Rodar — verificar FAIL**
```bash
pytest tests/test_auth.py -v
# Esperado: FAIL — módulo não existe
```

**Step 3: Criar `app/core/auth.py`**
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
```

**Step 4: Criar `app/api/auth.py`** com endpoints `/auth/login` e `/auth/me`.

**Step 5: Criar `app/api/deps.py`** com `get_current_user` dependency.

**Step 6: Registrar router no `main.py`**
```python
from app.api import auth as auth_router
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
```

**Step 7: Rodar testes — verificar PASS**
```bash
pytest tests/test_auth.py -v
# Esperado: 4 PASS
```

**Step 8: Commit**
```bash
git add control-panel/backend/app/core/auth.py control-panel/backend/app/api/auth.py control-panel/backend/app/api/deps.py tests/test_auth.py
git commit -m "feat(backend): add JWT local auth with login and /me endpoints"
```

---

### Task 6: Backend — Agents API

**Files:**
- Create: `control-panel/backend/app/api/agents.py`
- Create: `control-panel/backend/app/services/agent_sync.py`
- Create: `control-panel/backend/tests/test_agents.py`

**O que faz:** Lê as configs dos agentes de `/data/openclaw/agents/*/IDENTITY.md` e `openclaw.json`, sincroniza com DB. Expõe endpoints CRUD + status.

**Step 1: Escrever teste falhando**
```python
# tests/test_agents.py
@pytest.mark.asyncio
async def test_list_agents(client, auth_headers):
    response = await client.get("/agents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_agent_by_slug(client, auth_headers, seeded_agent):
    response = await client.get(f"/agents/ceo", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["slug"] == "ceo"
    assert response.json()["display_name"] == "Victor"
```

**Step 2: Rodar — verificar FAIL**

**Step 3: Criar `app/services/agent_sync.py`**
```python
import re
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()

AGENT_SLUGS = [
    "ceo", "po", "arquiteto", "dev_backend", "dev_frontend",
    "dev_mobile", "qa_engineer", "devops_sre", "security_engineer",
    "ux_designer", "dba_data_engineer", "memory_curator"
]

CRON_MAP = {
    # extraído do openclaw-pod.yaml env vars
    "dev_backend": "0 * * * *",
    "dev_frontend": "0 * * * *",
    "dev_mobile": "0 * * * *",
    "qa_engineer": "0 */6 * * *",
    "devops_sre": "0 */6 * * *",
    "security_engineer": "0 */6 * * *",
    "ux_designer": "0 */6 * * *",
    "dba_data_engineer": "0 */6 * * *",
    "memory_curator": "0 2 * * *",
}


def parse_identity(slug: str) -> dict:
    base = Path(settings.openclaw_data_path) / "agents" / slug
    identity_file = base / "IDENTITY.md"
    if not identity_file.exists():
        return {"display_name": slug, "role": slug}
    content = identity_file.read_text()
    name_match = re.search(r"Nome[:\s]+(.+)", content)
    role_match = re.search(r"Papel[:\s]+(.+)", content)
    return {
        "display_name": name_match.group(1).strip() if name_match else slug,
        "role": role_match.group(1).strip() if role_match else slug,
    }


async def sync_agents(session):
    from app.models import Agent
    from sqlmodel import select
    for slug in AGENT_SLUGS:
        result = await session.exec(select(Agent).where(Agent.slug == slug))
        agent = result.first()
        identity = parse_identity(slug)
        if not agent:
            agent = Agent(
                slug=slug,
                display_name=identity["display_name"],
                role=identity["role"],
                avatar_url=f"/static/avatars/{slug}.png",
                cron_expression=CRON_MAP.get(slug),
            )
            session.add(agent)
        else:
            agent.display_name = identity["display_name"]
        await session.commit()
```

**Step 4: Criar `app/api/agents.py`** com routers:
- `GET /agents` — lista paginada
- `GET /agents/{slug}` — detalhe
- `POST /agents/{slug}/restart` — restart session (chama openclaw gateway)
- `POST /agents/{slug}/cron/trigger` — força execução do cron

**Step 5: Registrar router no `main.py`**

**Step 6: Chamar `sync_agents` no startup do app**
```python
@app.on_event("startup")
async def on_startup():
    async with AsyncSessionLocal() as session:
        await sync_agents(session)
```

**Step 7: Rodar testes — verificar PASS**
```bash
pytest tests/test_agents.py -v
```

**Step 8: Commit**
```bash
git commit -m "feat(backend): add agents API with file-based sync from openclaw config"
```

---

### Task 7: Backend — Approvals API

**Files:**
- Create: `control-panel/backend/app/api/approvals.py`
- Create: `control-panel/backend/app/services/openclaw_client.py`
- Create: `control-panel/backend/tests/test_approvals.py`

**Step 1: Criar `app/services/openclaw_client.py`**
```python
import httpx
from app.core.config import get_settings

settings = get_settings()

class OpenClawClient:
    def __init__(self):
        self.base_url = settings.openclaw_gateway_url
        self.headers = {"Authorization": f"Bearer {settings.openclaw_gateway_token}"}

    async def get_approvals(self, status: str = "pending") -> list:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/v1/approvals",
                headers=self.headers,
                params={"status": status},
                timeout=10.0,
            )
            r.raise_for_status()
            return r.json().get("items", [])

    async def decide_approval(self, approval_id: str, decision: str, justification: str = "") -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/v1/approvals/{approval_id}/decide",
                headers=self.headers,
                json={"decision": decision, "justification": justification},
                timeout=10.0,
            )
            r.raise_for_status()
            return r.json()

    async def get_sessions(self) -> list:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/v1/sessions",
                headers=self.headers,
                timeout=10.0,
            )
            r.raise_for_status()
            return r.json().get("items", [])

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{self.base_url}/healthz", timeout=5.0)
                return r.status_code == 200
        except Exception:
            return False

openclaw = OpenClawClient()
```

**Step 2: Escrever teste falhando**
```python
# tests/test_approvals.py
@pytest.mark.asyncio
async def test_list_approvals(client, auth_headers, seeded_approval):
    response = await client.get("/approvals", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

@pytest.mark.asyncio
async def test_decide_approval(client, auth_headers, seeded_approval):
    approval_id = seeded_approval["id"]
    response = await client.post(
        f"/approvals/{approval_id}/decide",
        headers=auth_headers,
        json={"decision": "approved", "justification": "Looks good"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
```

**Step 3: Rodar — verificar FAIL**

**Step 4: Criar `app/api/approvals.py`** com:
- `GET /approvals` — lista paginada (filtro por status)
- `GET /approvals/{id}` — detalhe
- `POST /approvals/{id}/decide` — aprovar/rejeitar (persiste + chama gateway)
- `GET /approvals/stats` — contagem por status

**Step 5: Rodar testes — verificar PASS**

**Step 6: Commit**
```bash
git commit -m "feat(backend): add approvals API with openclaw gateway integration"
```

---

### Task 8: Backend — Sessions, Tasks, SDD, Memory APIs

**Files:**
- Create: `control-panel/backend/app/api/sessions.py`
- Create: `control-panel/backend/app/api/tasks.py`
- Create: `control-panel/backend/app/api/sdd.py`
- Create: `control-panel/backend/app/api/memory.py`
- Create: `control-panel/backend/app/services/github_client.py`
- Create: `control-panel/backend/app/services/memory_sync.py`

**Sessions API:**
- `GET /sessions` — lista paginada (proxy ao gateway + cache Redis)
- `GET /sessions/{id}` — detalhe completo (proxy)
- `GET /sessions/{id}/stream` — SSE streaming de mensagens

**Tasks API (GitHub sync):**
- `GET /tasks` — lista com filtros (status, agent, label)
- `POST /tasks` — criar task (cria GitHub Issue + persiste local)
- `PATCH /tasks/{id}` — atualizar status
- `POST /tasks/sync` — trigger sync manual com GitHub

**`app/services/github_client.py`:**
```python
import httpx
from app.core.config import get_settings

settings = get_settings()

class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
        }

    async def list_issues(self, repo: str, state: str = "open") -> list:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.BASE}/repos/{settings.github_org}/{repo}/issues",
                headers=self.headers,
                params={"state": state, "per_page": 100},
                timeout=15.0,
            )
            r.raise_for_status()
            return r.json()
```

**SDD API:**
- `GET /sdd` — lista artefatos com filtro por tipo e status
- `POST /sdd` — criar novo artefato (BRIEF inicia o fluxo)
- `GET /sdd/{id}` — artefato completo
- `PATCH /sdd/{id}` — atualizar conteúdo/status

**Memory API:**
- `GET /memory` — lista entradas paginadas com filtro por agente e tipo
- `GET /memory/agents/{slug}` — memória do agente específico
- `POST /memory/{id}/promote` — promover candidato para global

**`app/services/memory_sync.py`** — usa `watchdog` para watch de `/data/openclaw/memory/` e sincroniza mudanças no DB.

**Step: Commit**
```bash
git commit -m "feat(backend): add sessions, tasks, SDD, and memory APIs"
```

---

### Task 9: Backend — Crons + Cluster + Metrics + WebSocket Hub

**Files:**
- Create: `control-panel/backend/app/api/crons.py`
- Create: `control-panel/backend/app/api/cluster.py`
- Create: `control-panel/backend/app/api/metrics.py`
- Create: `control-panel/backend/app/api/ws.py`
- Create: `control-panel/backend/app/services/k8s_client.py`
- Create: `control-panel/backend/app/services/cron_monitor.py`

**`app/services/k8s_client.py`:**
```python
from kubernetes import client, config as k8s_config
from app.core.config import get_settings

settings = get_settings()


def get_k8s_clients():
    try:
        k8s_config.load_incluster_config()
    except Exception:
        k8s_config.load_kube_config()
    return client.CoreV1Api(), client.AppsV1Api()


async def list_pods(namespace: str = "default") -> list:
    core, _ = get_k8s_clients()
    pods = core.list_namespaced_pod(namespace=namespace)
    return [
        {
            "name": p.metadata.name,
            "status": p.status.phase,
            "restarts": sum(
                c.restart_count for c in (p.status.container_statuses or [])
            ),
            "ready": all(c.ready for c in (p.status.container_statuses or [])),
            "age": p.metadata.creation_timestamp.isoformat(),
        }
        for p in pods.items
    ]
```

**Crons API:**
- `GET /crons` — lista todos os crons com status
- `GET /crons/{slug}/executions` — histórico de execuções do agente
- `POST /crons/{slug}/trigger` — dispara cron manualmente

**Cluster API:**
- `GET /cluster/pods` — lista pods do namespace
- `GET /cluster/events` — eventos K8s recentes
- `GET /cluster/pvcs` — uso de PVCs
- `WebSocket /cluster/logs/{pod}` — streaming de logs do pod

**WebSocket Hub (`app/api/ws.py`):**
```python
from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()

class WSHub:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, channel: str, ws: WebSocket):
        await ws.accept()
        self.connections.setdefault(channel, []).append(ws)

    async def disconnect(self, channel: str, ws: WebSocket):
        self.connections.get(channel, []).remove(ws)

    async def broadcast(self, channel: str, data: dict):
        dead = []
        for ws in self.connections.get(channel, []):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.connections.get(channel, []).remove(ws)

    async def listen_redis(self):
        """Subscreve Redis e distribui para WebSocket clients."""
        r = redis.from_url(settings.redis_url)
        pubsub = r.pubsub()
        await pubsub.subscribe("approvals", "agents", "cluster", "dashboard")
        async for message in pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"].decode()
                data = json.loads(message["data"])
                await self.broadcast(channel, data)

hub = WSHub()
```

**Metrics API:**
- `GET /metrics/overview` — métricas 24h (tokens, tasks, aprovações)
- `GET /metrics/agents/{slug}` — métricas por agente

**Step: Commit**
```bash
git commit -m "feat(backend): add crons, cluster, metrics APIs and WebSocket hub"
```

---

### Task 10: K8s Manifests — Backend + Frontend + Worker

**Files:**
- Create: `k8s/base/control-panel/backend-deployment.yaml`
- Create: `k8s/base/control-panel/frontend-deployment.yaml`
- Create: `k8s/base/control-panel/worker-deployment.yaml`
- Create: `k8s/base/control-panel/services.yaml`
- Create: `k8s/base/control-panel/configmap.yaml`
- Modify: `k8s/kustomization.yaml` (adicionar secretGenerator para panel)

**`backend-deployment.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clawdevs-panel-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: clawdevs-panel-backend
  template:
    metadata:
      labels:
        app: clawdevs-panel-backend
    spec:
      serviceAccountName: clawdevs-panel
      containers:
        - name: backend
          image: clawdevs-panel-backend:latest
          imagePullPolicy: Never  # minikube local image
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: clawdevs-panel-auth
            - secretRef:
                name: openclaw-auth  # reutiliza token OpenClaw existente
          env:
            - name: PANEL_DATABASE_URL
              value: postgresql+asyncpg://panel:$(PANEL_DB_PASSWORD)@clawdevs-panel-db:5432/clawdevs_panel
            - name: PANEL_REDIS_URL
              value: redis://:$(PANEL_REDIS_PASSWORD)@clawdevs-panel-redis:6379/0
            - name: PANEL_OPENCLAW_GATEWAY_URL
              value: http://clawdevs-ai:18789
          volumeMounts:
            - name: openclaw-data
              mountPath: /data/openclaw
              readOnly: true
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              cpu: 500m
              memory: 1Gi
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
      volumes:
        - name: openclaw-data
          persistentVolumeClaim:
            claimName: openclaw-data  # PVC existente do StatefulSet
            readOnly: true
```

**`services.yaml`:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: clawdevs-panel-frontend
spec:
  type: NodePort
  selector:
    app: clawdevs-panel-frontend
  ports:
    - port: 3000
      targetPort: 3000
      nodePort: 31880
---
apiVersion: v1
kind: Service
metadata:
  name: clawdevs-panel-backend
spec:
  type: NodePort
  selector:
    app: clawdevs-panel-backend
  ports:
    - port: 8000
      targetPort: 8000
      nodePort: 31881
---
apiVersion: v1
kind: Service
metadata:
  name: clawdevs-panel-db
spec:
  type: ClusterIP
  selector:
    app: clawdevs-panel-db
  ports:
    - port: 5432
      targetPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: clawdevs-panel-redis
spec:
  type: ClusterIP
  selector:
    app: clawdevs-panel-redis
  ports:
    - port: 6379
      targetPort: 6379
```

**Adicionar ao `k8s/kustomization.yaml`:**
```yaml
secretGenerator:
  - name: clawdevs-panel-auth
    envs:
      - .env
```

**Step: Commit**
```bash
git commit -m "feat(k8s): add backend, frontend, worker deployments and services for control panel"
```

---

## Phase 3: Frontend

### Task 11: Frontend Scaffold — Next.js 16 + Tailwind v4 + shadcn/ui

**Files:**
- Create: `control-panel/frontend/package.json`
- Create: `control-panel/frontend/next.config.ts`
- Create: `control-panel/frontend/tailwind.config.ts`
- Create: `control-panel/frontend/src/app/layout.tsx`
- Create: `control-panel/frontend/src/app/globals.css`
- Create: `control-panel/frontend/Dockerfile`

**Step 1: Inicializar projeto**
```bash
cd control-panel/frontend
npx create-next-app@16.2.0 . --typescript --tailwind --app --no-src-dir
# Depois mover para src/
```

**Step 2: Instalar dependências**
```bash
npm install \
  @tanstack/react-query@5.94.5 \
  @tanstack/react-table@8.21.3 \
  recharts@3.8.0 \
  next-themes \
  lucide-react \
  clsx \
  tailwind-merge \
  orval@8.5.3

# shadcn/ui
npx shadcn@4.1.0 init
npx shadcn@4.1.0 add button badge card dialog dropdown-menu input label select separator sheet sidebar skeleton table tabs textarea tooltip
```

**Step 3: Configurar tema ClawDevs em `src/app/globals.css`**
```css
@import "tailwindcss";

:root {
  --background: 0 0% 3%;
  --foreground: 0 0% 98%;
  --accent: 153 100% 50%;          /* #00FF9C verde neon */
  --accent-foreground: 0 0% 3%;
  --card: 0 0% 6%;
  --card-foreground: 0 0% 90%;
  --border: 0 0% 14%;
  --input: 0 0% 10%;
  --ring: 153 100% 50%;
  --radius: 0.5rem;
  --font-sans: "Geist", sans-serif;
  --font-mono: "Geist Mono", monospace;
}
```

**Step 4: Criar `src/app/layout.tsx`** com providers (QueryClient, ThemeProvider, sidebar layout).

**Step 5: Criar Dockerfile frontend**
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
USER appuser
EXPOSE 3000
CMD ["node", "server.js"]
```

**Step 6: Commit**
```bash
git commit -m "feat(frontend): scaffold Next.js 16 with Tailwind v4, shadcn/ui, ClawDevs dark theme"
```

---

### Task 12: Frontend — Orval Setup + API Client

**Files:**
- Create: `control-panel/frontend/orval.config.ts`
- Create: `control-panel/frontend/src/lib/api/.gitkeep`
- Create: `control-panel/frontend/src/lib/query-client.ts`
- Create: `control-panel/frontend/src/lib/ws.ts`

**Step 1: Criar `orval.config.ts`**
```typescript
import { defineConfig } from "orval";

export default defineConfig({
  panel: {
    input: {
      target: "http://localhost:8000/openapi.json",
    },
    output: {
      mode: "tags-split",
      target: "src/lib/api",
      schemas: "src/lib/api/models",
      client: "react-query",
      override: {
        mutator: {
          path: "src/lib/axios-instance.ts",
          name: "customInstance",
        },
      },
    },
  },
});
```

**Step 2: Criar `src/lib/axios-instance.ts`** com interceptors para JWT:
```typescript
import Axios, { AxiosRequestConfig } from "axios";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const customInstance = async <T>(config: AxiosRequestConfig): Promise<T> => {
  const token = typeof window !== "undefined"
    ? localStorage.getItem("panel_token")
    : null;

  const response = await Axios({
    ...config,
    baseURL: BACKEND_URL,
    headers: {
      ...config.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return response.data;
};
```

**Step 3: Criar `src/lib/ws.ts`** — WebSocket client com reconnect:
```typescript
type WSChannel = "approvals" | "agents" | "cluster" | "dashboard";

class WSManager {
  private sockets: Map<string, WebSocket> = new Map();
  private listeners: Map<string, Set<(data: unknown) => void>> = new Map();

  connect(channel: WSChannel, baseUrl: string) {
    const url = `${baseUrl.replace("http", "ws")}/ws/${channel}`;
    const ws = new WebSocket(url);
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      this.listeners.get(channel)?.forEach((fn) => fn(data));
    };
    ws.onclose = () => {
      // exponential backoff reconnect
      setTimeout(() => this.connect(channel, baseUrl), 3000);
    };
    this.sockets.set(channel, ws);
  }

  subscribe(channel: WSChannel, fn: (data: unknown) => void) {
    if (!this.listeners.has(channel)) this.listeners.set(channel, new Set());
    this.listeners.get(channel)!.add(fn);
    return () => this.listeners.get(channel)?.delete(fn);
  }
}

export const wsManager = new WSManager();
```

**Step 4: Gerar API client**
```bash
cd control-panel/frontend
# Backend deve estar rodando em localhost:8000
npm run orval
# Esperado: src/lib/api/* gerado com hooks React Query tipados
```

**Step 5: Commit**
```bash
git commit -m "feat(frontend): add Orval API codegen config and WebSocket client"
```

---

### Task 13: Frontend — Layout Principal (Sidebar + Header)

**Files:**
- Create: `control-panel/frontend/src/components/layout/sidebar.tsx`
- Create: `control-panel/frontend/src/components/layout/header.tsx`
- Create: `control-panel/frontend/src/components/layout/app-layout.tsx`

**Sidebar items:**
```typescript
const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/agents", label: "Agentes", icon: Bot },
  { href: "/sessions", label: "Sessões", icon: MessageSquare },
  { href: "/approvals", label: "Aprovações", icon: ShieldCheck, badge: "approvals" },
  { href: "/tasks", label: "Tarefas", icon: CheckSquare },
  { href: "/sdd", label: "SDD", icon: FileText },
  { href: "/memory", label: "Memória", icon: Brain },
  { href: "/crons", label: "Crons", icon: Clock },
  { href: "/cluster", label: "Cluster", icon: Server },
  { href: "/settings", label: "Settings", icon: Settings },
];
```

**Sidebar** com logo ClawDevs, navegação colapsável, avatar do usuário no rodapé.
**Header** com breadcrumb dinâmico e badge de aprovações pendentes (conectado via WebSocket).

**Step: Commit**
```bash
git commit -m "feat(frontend): add sidebar navigation and app layout with ClawDevs branding"
```

---

### Task 14: Frontend — Dashboard Page

**Files:**
- Create: `control-panel/frontend/src/app/page.tsx`
- Create: `control-panel/frontend/src/components/dashboard/stats-cards.tsx`
- Create: `control-panel/frontend/src/components/dashboard/agents-grid.tsx`
- Create: `control-panel/frontend/src/components/dashboard/activity-feed.tsx`
- Create: `control-panel/frontend/src/components/dashboard/usage-chart.tsx`

**Componentes:**
- `StatsCards` — 4 cards: Agentes Ativos, Aprovações Pendentes, Tasks Abertas, Tokens 24h
- `AgentsGrid` — grid 4×3 com avatar PNG, nome, status badge (verde/vermelho/cinza), último heartbeat
- `UsageChart` — Recharts LineChart de tokens por agente nas últimas 24h
- `ActivityFeed` — lista de activity_events mais recentes

**Realtime:** WebSocket `dashboard` channel atualiza stats e status dos agentes sem reload.

**Step: Commit**
```bash
git commit -m "feat(frontend): add dashboard with real-time stats, agents grid and activity feed"
```

---

### Task 15: Frontend — Agents Pages

**Files:**
- Create: `control-panel/frontend/src/app/agents/page.tsx`
- Create: `control-panel/frontend/src/app/agents/[slug]/page.tsx`
- Create: `control-panel/frontend/src/components/agents/agent-card.tsx`
- Create: `control-panel/frontend/src/components/agents/agent-profile.tsx`

**Lista:** TanStack Table com avatar, nome, role, status badge, heartbeat, modelo atual, próximo cron. Filtros por status e role.

**Perfil:** Tabs — Visão Geral / Memória / Sessões / Aprovações / Métricas.
- Tab Geral: identidade renderizada em Markdown, ferramentas disponíveis, ações (restart, trigger cron).
- Gráfico de uso semanal (Recharts BarChart).

**Step: Commit**
```bash
git commit -m "feat(frontend): add agents list and profile pages with full detail tabs"
```

---

### Task 16: Frontend — Approvals Page

**Files:**
- Create: `control-panel/frontend/src/app/approvals/page.tsx`
- Create: `control-panel/frontend/src/components/approvals/approval-card.tsx`
- Create: `control-panel/frontend/src/components/approvals/decision-dialog.tsx`

**Kanban** com três colunas: Pendente / Aprovado / Rejeitado.
**ApprovalCard** mostra: agente + avatar, tipo de ação, payload em JSON colapsável, confidence score como barra de progresso, rubric scores como badges coloridos, timestamp.
**DecisionDialog** modal com textarea para justificativa + botões Aprovar/Rejeitar.
**Toast** de confirmação após decisão. Badge no nav atualiza via WebSocket.

**Step: Commit**
```bash
git commit -m "feat(frontend): add approvals Kanban with real-time updates and decision modal"
```

---

### Task 17: Frontend — Sessions, Tasks, SDD Pages

**Sessions (`/sessions`, `/sessions/[id]`):**
- Tabela paginada com TanStack Table. Colunas: agente, canal, peer, mensagens, tokens, duração, status.
- Detalhe: thread de mensagens renderizado em Markdown, timeline de tool calls, link para SDD artifact.

**Tasks (`/tasks`):**
- Board view (Kanban: inbox→in_progress→review→done) e List view toggle.
- Criar task abre modal com campo título, descrição, agente assignee — sincroniza com GitHub Issues.
- Badge de prioridade (alta/média/baixa) com cores.

**SDD (`/sdd`, `/sdd/[id]`):**
- Stepper visual: BRIEF → SPEC → CLARIFY → PLAN → TASK → VALIDATE com status por etapa.
- Artefato renderizado em Markdown com editor inline para BRIEF.
- GitHub Issue linkado com link externo.

**Step: Commit**
```bash
git commit -m "feat(frontend): add sessions, tasks and SDD workflow pages"
```

---

### Task 18: Frontend — Memory, Crons, Cluster, Settings Pages

**Memory (`/memory`):**
- Sidebar com lista de agentes. Main area com três tabs: Ativa / Candidatas / Global.
- Cada entrada mostra: tipo badge, conteúdo truncado (expand), tags, data. Busca fulltext.
- Botão "Promover" em candidatas.

**Crons (`/crons`):**
- Grid de cards por agente. Cada card: avatar + nome, próxima execução com countdown timer, status badge, sparkline das últimas 10 execuções (verde=ok, vermelho=error), botão "Disparar Agora".
- Expandir card mostra log tail da última execução.

**Cluster (`/cluster`):**
- Tabela de pods: nome, status badge, restarts, ready, idade. Clique expande logs ao vivo (WebSocket streaming).
- Seção de eventos K8s recentes (últimos 20).
- Cards de PVCs com uso.

**Settings (`/settings`):**
- Formulário para troca de senha.
- Status de conexão com gateway OpenClaw (badge verde/vermelho).
- Lista de modelos Ollama disponíveis.
- Toggle de features (GitHub sync, etc.).

**Step: Commit**
```bash
git commit -m "feat(frontend): add memory, crons, cluster and settings pages"
```

---

## Phase 4: Integration + Polish

### Task 19: Makefile — Novos Targets

**Files:**
- Modify: `Makefile`

**Step 1: Adicionar targets no final do Makefile**
```makefile
# ─────────────────────────────────────────────
# Control Panel
# ─────────────────────────────────────────────

panel-build: ## Build images do control panel no minikube
	eval $$(minikube docker-env) && \
	docker build -t clawdevs-panel-backend:latest control-panel/backend/ && \
	docker build -t clawdevs-panel-frontend:latest control-panel/frontend/

panel-apply: ## Deploy control panel no cluster
	kubectl apply -k k8s/base/control-panel/

panel-status: ## Status dos pods do control panel
	kubectl get pods -l app.kubernetes.io/part-of=clawdevs-panel

panel-logs-backend: ## Logs do backend
	kubectl logs -l app=clawdevs-panel-backend -f

panel-logs-frontend: ## Logs do frontend
	kubectl logs -l app=clawdevs-panel-frontend -f

panel-db-migrate: ## Rodar migrações Alembic
	kubectl exec -it $$(kubectl get pod -l app=clawdevs-panel-backend -o jsonpath='{.items[0].metadata.name}') \
	-- alembic upgrade head

panel-restart: ## Restart dos pods do painel
	kubectl rollout restart deployment/clawdevs-panel-backend
	kubectl rollout restart deployment/clawdevs-panel-frontend

panel-destroy: ## Remove todos os recursos do control panel
	kubectl delete -k k8s/base/control-panel/ || true

panel-url: ## Exibe URL de acesso ao painel
	@echo "Frontend: http://$$(minikube ip):31880"
	@echo "Backend:  http://$$(minikube ip):31881"
	@echo "API Docs: http://$$(minikube ip):31881/docs"
```

**Step 2: Commit**
```bash
git commit -m "feat(makefile): add control panel build, deploy, logs and migrate targets"
```

---

### Task 20: Deploy End-to-End — Validação

**Step 1: Build local images no minikube**
```bash
make panel-build
# Esperado: imagens clawdevs-panel-backend:latest e frontend:latest no docker do minikube
```

**Step 2: Aplicar todos os manifests**
```bash
make panel-apply
# Esperado: pods iniciando no kubectl get pods
```

**Step 3: Aguardar pods ficarem Ready**
```bash
kubectl wait --for=condition=ready pod -l app=clawdevs-panel-backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=clawdevs-panel-db --timeout=120s
# Esperado: pod/... condition met
```

**Step 4: Rodar migrations**
```bash
make panel-db-migrate
# Esperado: "Running upgrade -> xxxxxx, initial schema"
```

**Step 5: Verificar health**
```bash
curl http://$(minikube ip):31881/healthz
# Esperado: {"status":"ok"}
```

**Step 6: Acessar painel**
```bash
make panel-url
# Abrir no browser: http://$(minikube ip):31880
# Esperado: tela de login ClawDevs Control Panel
```

**Step 7: Login e smoke test**
- Login com `PANEL_ADMIN_USERNAME` e `PANEL_ADMIN_PASSWORD` do `.env`
- Verificar: Dashboard carrega com grid de agentes
- Verificar: /approvals carrega sem erro
- Verificar: /cluster lista os pods (openclaw, ollama, searxng + panel)
- Verificar: /memory mostra arquivos do PVC

**Step 8: Commit final**
```bash
git add .
git commit -m "feat: complete ClawDevs AI Control Panel — full-stack K8s embedded dashboard"
```

---

## Checklist de Qualidade

- [ ] Todos os endpoints protegidos por JWT (exceto `/healthz` e `/auth/login`)
- [ ] Todos os modelos SQLModel têm indexes nos campos mais consultados
- [ ] CORS configurado corretamente para o NodePort do frontend
- [ ] PVC do OpenClaw montado como `readOnly: true` no backend
- [ ] ServiceAccount tem apenas permissões de leitura no K8s
- [ ] Variáveis sensíveis nunca hardcoded — sempre via Secret K8s
- [ ] Dockerfile com usuário não-root
- [ ] WebSocket reconnect automático no frontend
- [ ] Loading states em todas as páginas (Suspense + skeleton)
- [ ] Error boundaries nas páginas críticas
- [ ] Responsive: sidebar colapsa em telas < 1024px

---

## Execução

**Plano salvo em:** `docs/plans/2026-03-22-control-panel-plan.md`

**Duas opções de execução:**

**1. Subagent-Driven (esta sessão)** — despacho de subagente por task, revisão entre tasks, iteração rápida.

**2. Parallel Session (sessão separada)** — abrir nova sessão no worktree com `executing-plans`, execução em batch com checkpoints.

**Qual prefere?**
