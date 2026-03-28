# K8s → Docker Compose Refactoring Implementation Plan

> **Para Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans para executar este plano task-by-task.

**Objetivo:** Remover todas as referências a Kubernetes do codebase, renomeando para arquitetura Docker Compose.

**Arquitetura:** Migrando de abstração k8s (pods, namespaces, kubeconfig) para Docker Compose (containers, services, volumes). O código será refatorado de `k8s_client` → `container_client`, com suporte degradado para ambientes sem Kubernetes.

**Tech Stack:** Python FastAPI, Docker Compose, pytest

---

## Task 1: Renomear arquivo principal de client

**Arquivos:**
- Renomear: `control-panel/backend/app/services/k8s_client.py` → `control-panel/backend/app/services/container_client.py`
- Modificar: `control-panel/backend/app/api/cluster.py`

**Step 1: Ler o arquivo atual**

```bash
cat control-panel/backend/app/services/k8s_client.py
```

**Step 2: Criar novo arquivo com conteúdo refatorado**

Criar `control-panel/backend/app/services/container_client.py` com:
- Renomear função `get_k8s_clients()` → `get_container_clients()`
- Renomear função `list_pods()` → `list_containers()`
- Manter compatibilidade com código antigo via alias (deprecated)
- Atualizar mensagens de log para "container" em vez de "kubernetes"
- Remover importação da biblioteca kubernetes (mantém try/except)

Código base (adotar como template):

```python
# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
# [Manter licença original]

import logging

logger = logging.getLogger(__name__)

try:
    import kubernetes
except Exception:  # pragma: no cover
    kubernetes = None


def get_container_clients():
    """Get container management clients (deprecated k8s fallback)."""
    try:
        if kubernetes is None:
            logger.warning("Container management requires kubernetes package")
            return None, None
        client = kubernetes.client
        k8s_config = kubernetes.config
        try:
            k8s_config.load_incluster_config()
        except Exception:
            k8s_config.load_kube_config()
        return client.CoreV1Api(), client.AppsV1Api()
    except Exception as e:
        logger.warning(f"Container client not available: {e}")
        return None, None


def list_containers(namespace: str = "default") -> list:
    """List containers (k8s pods as fallback)."""
    core, _ = get_container_clients()
    if core is None:
        return []
    try:
        pods = core.list_namespaced_pod(namespace=namespace)
        return [
            {
                "name": p.metadata.name,
                "namespace": p.metadata.namespace,
                "status": p.status.phase or "Unknown",
                "restarts": sum(
                    c.restart_count for c in (p.status.container_statuses or [])
                ),
                "ready": (
                    all(c.ready for c in (p.status.container_statuses or []))
                    if p.status.container_statuses
                    else False
                ),
                "age": (
                    p.metadata.creation_timestamp.isoformat()
                    if p.metadata.creation_timestamp
                    else None
                ),
                "node": p.spec.node_name,
            }
            for p in pods.items
        ]
    except Exception as e:
        logger.error(f"Error listing containers: {e}")
        return []


def list_events(namespace: str = "default", limit: int = 50) -> list:
    """List container events."""
    core, _ = get_container_clients()
    if core is None:
        return []
    try:
        events = core.list_namespaced_event(
            namespace=namespace,
            limit=limit,
        )
        return [
            {
                "name": e.metadata.name,
                "type": e.type,
                "reason": e.reason,
                "message": e.message,
                "involved_object": e.involved_object.name,
                "count": e.count,
                "last_timestamp": (
                    e.last_timestamp.isoformat() if e.last_timestamp else None
                ),
            }
            for e in sorted(
                events.items,
                key=lambda x: x.last_timestamp or x.metadata.creation_timestamp,
                reverse=True,
            )
        ]
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return []


def list_pvcs(namespace: str = "default") -> list:
    """List persistent volume claims."""
    core, _ = get_container_clients()
    if core is None:
        return []
    try:
        pvcs = core.list_namespaced_persistent_volume_claim(namespace=namespace)
        return [
            {
                "name": p.metadata.name,
                "status": p.status.phase,
                "capacity": (
                    p.status.capacity.get("storage") if p.status.capacity else None
                ),
                "access_modes": p.spec.access_modes,
                "storage_class": p.spec.storage_class_name,
            }
            for p in pvcs.items
        ]
    except Exception as e:
        logger.error(f"Error listing PVCs: {e}")
        return []


def get_cluster_info(namespace: str = "default") -> dict:
    """Get container cluster information."""
    core, _ = get_container_clients()
    if core is None:
        return {"cluster_name": None, "namespace": namespace, "version": "unknown"}

    version = "unknown"
    cluster_name = None

    try:
        if kubernetes is not None:
            version_api = kubernetes.client.VersionApi()
            version_data = version_api.get_code()
            version = getattr(version_data, "git_version", None) or "unknown"
    except Exception as e:
        logger.warning(f"Error getting container version: {e}")

    try:
        nodes = core.list_node(limit=1)
        if nodes.items:
            cluster_name = nodes.items[0].metadata.cluster_name
    except Exception as e:
        logger.warning(f"Error getting cluster name: {e}")

    return {
        "cluster_name": cluster_name,
        "namespace": namespace,
        "version": version,
    }


# Deprecated: maintained for backwards compatibility
get_k8s_clients = get_container_clients
list_pods = list_containers
```

**Step 3: Atualizar import em `cluster.py`**

Mudar:
```python
from app.services import k8s_client
```

Para:
```python
from app.services import container_client
```

**Step 4: Atualizar todas as chamadas em `cluster.py`**

- `k8s_client.get_k8s_clients()` → `container_client.get_container_clients()`
- `k8s_client.list_pods()` → `container_client.list_containers()`
- `k8s_client.list_events()` → `container_client.list_events()`
- `k8s_client.list_pvcs()` → `container_client.list_pvcs()`
- `k8s_client.get_cluster_info()` → `container_client.get_cluster_info()`
- Renomear função `_ensure_k8s_available()` → `_ensure_container_client_available()`
- Renomear `settings.k8s_namespace` → `settings.container_namespace` (ver Task 3)

**Step 5: Commit**

```bash
git add control-panel/backend/app/services/container_client.py
git add control-panel/backend/app/api/cluster.py
git commit -m "refactor(backend): rename k8s_client to container_client for Docker Compose"
```

---

## Task 2: Renomear arquivo de testes

**Arquivos:**
- Renomear: `control-panel/backend/tests/test_services/test_k8s_client.py` → `test_container_client.py`
- Atualizar: imports e nomes de classe/função

**Step 1: Criar novo arquivo de testes**

Criar `control-panel/backend/tests/test_services/test_container_client.py`:
- Renomear `TestK8sClient` → `TestContainerClient`
- Renomear `TestListPods` → `TestListContainers`
- Renomear `test_get_k8s_clients_*` → `test_get_container_clients_*`
- Renomear `test_list_pods_*` → `test_list_containers_*`
- Atualizar paths: `app.services.k8s_client` → `app.services.container_client`
- Atualizar nomes de funções mockadas: `get_k8s_clients` → `get_container_clients`
- Atualizar docstrings: "Kubernetes" → "Container"

**Step 2: Commit**

```bash
git add control-panel/backend/tests/test_services/test_container_client.py
git commit -m "test: rename k8s_client tests to container_client tests"
```

---

## Task 3: Atualizar configurações (config.py)

**Arquivos:**
- Modificar: `control-panel/backend/app/core/config.py:56`

**Step 1: Refatorar variável de configuração**

Mudar:
```python
k8s_namespace: str = "default"
```

Para:
```python
container_namespace: str = "default"

# Deprecated: backwards compatibility
@property
def k8s_namespace(self) -> str:
    """Deprecated: use container_namespace instead."""
    return self.container_namespace
```

**Step 2: Atualizar uso em `cluster.py`**

- `settings.k8s_namespace` → `settings.container_namespace` em todas as 4 chamadas

**Step 3: Commit**

```bash
git add control-panel/backend/app/core/config.py
git commit -m "config: rename k8s_namespace to container_namespace"
```

---

## Task 4: Atualizar arquivo de testes de configuração

**Arquivos:**
- Modificar: `control-panel/backend/tests/test_core/test_config.py`

**Step 1: Procurar referências a k8s no test_config.py**

```bash
grep -n "k8s" control-panel/backend/tests/test_core/test_config.py
```

**Step 2: Atualizar testes**

- Renomear testes: `test_*_k8s_*` → `test_*_container_*` (se houver)
- Atualizar assertions para usar `container_namespace`
- Adicionar teste: verificar que `settings.k8s_namespace` ainda funciona (backwards compat)

**Step 3: Commit**

```bash
git add control-panel/backend/tests/test_core/test_config.py
git commit -m "test: update config tests for container_namespace"
```

---

## Task 5: Remover arquivo k8s_client.py antigo

**Arquivos:**
- Deletar: `control-panel/backend/app/services/k8s_client.py`
- Deletar: `control-panel/backend/tests/test_services/test_k8s_client.py`

**Step 1: Verificar que não há mais imports do arquivo antigo**

```bash
grep -r "from.*k8s_client import\|import.*k8s_client" control-panel/backend/ 2>/dev/null || echo "✓ No k8s_client imports found"
```

**Step 2: Deletar arquivos**

```bash
rm control-panel/backend/app/services/k8s_client.py
rm control-panel/backend/tests/test_services/test_k8s_client.py
```

**Step 3: Commit**

```bash
git add -A
git commit -m "refactor: remove deprecated k8s_client files"
```

---

## Task 6: Executar testes

**Arquivos:**
- Executar: `control-panel/backend/tests/`

**Step 1: Rodar testes de container_client**

```bash
cd control-panel/backend
python -m pytest tests/test_services/test_container_client.py -v
```

**Step 2: Rodar todos os testes**

```bash
python -m pytest tests/ -v --tb=short
```

**Step 3: Verificar cobertura**

```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

Expected: Todos os testes passam com cobertura similar à anterior.

**Step 4: Commit se passou**

```bash
git add -A
git commit -m "test: all tests passing after refactoring"
```

---

## Task 7: Atualizar documentação e comentários

**Arquivos:**
- Buscar e atualizar: `docs/` (README.md, arquitetura, etc)

**Step 1: Procurar todas as referências documentadas**

```bash
grep -r "kubernetes\|k8s_namespace\|k8s client" docs/ --include="*.md" 2>/dev/null | head -20
```

**Step 2: Atualizar arquivos de documentação**

Para cada arquivo encontrado:
- Substituir "Kubernetes" → "Docker Compose" (mantendo contexto histórico se relevante)
- Substituir "k8s" → "container" ou "docker" conforme contexto
- Atualizar exemplos de configuração

**Step 3: Commit**

```bash
git add docs/
git commit -m "docs: update references from k8s to Docker Compose"
```

---

## Task 8: Atualizar GitHub Workflows

**Arquivos:**
- Verificar: `.github/workflows/*.yml`

**Step 1: Procurar e atualizar**

```bash
grep -n "kubernetes\|k8s" .github/workflows/*.yml 2>/dev/null || echo "✓ No k8s refs found"
```

**Step 2: Se houver referências, atualizar cada workflow**

- Remover jobs/steps específicos de k8s se forem obsoletos
- Atualizar mensagens/nomes de referências

**Step 3: Commit**

```bash
git add .github/workflows/
git commit -m "ci: remove kubernetes references from workflows"
```

---

## Task 9: Verificação final e testes de integração

**Arquivos:**
- Validar: `docker-compose.yaml`
- Testar: Backend container inicia corretamente

**Step 1: Verificar que docker-compose.yaml está correto**

```bash
docker-compose config > /dev/null && echo "✓ Valid docker-compose.yaml"
```

**Step 2: Build da imagem de backend**

```bash
docker-compose build panel-backend
```

**Step 3: Iniciar apenas o backend para testes**

```bash
docker-compose up -d postgres redis panel-backend
sleep 10
curl http://localhost:8000/healthz || echo "⚠ Backend not ready yet"
```

**Step 4: Verificar logs do backend**

```bash
docker-compose logs panel-backend | tail -20
```

**Step 5: Parar containers**

```bash
docker-compose down
```

**Step 6: Commit final**

```bash
git add -A
git commit -m "ci: verify docker-compose backend deployment works"
```

---

## Checklist de Verificação

- [ ] Arquivo `k8s_client.py` renomeado para `container_client.py`
- [ ] Todos os imports atualizados
- [ ] Nomes de funções refatorados (`get_container_clients`, `list_containers`)
- [ ] Compatibilidade retroativa mantida via aliases
- [ ] Arquivo de testes renomeado e atualizado
- [ ] Configurações em `config.py` atualizadas
- [ ] Documentação atualizada
- [ ] Workflows do GitHub atualizados
- [ ] Testes passando (pytest)
- [ ] Docker-compose.yaml validado
- [ ] Backend inicia corretamente com Docker Compose
- [ ] Todos os commits consolidados no branch main
