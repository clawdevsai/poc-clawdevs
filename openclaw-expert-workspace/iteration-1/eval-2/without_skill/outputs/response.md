# Como Construir um Plugin OpenClaw do Zero

## 1. Introdução

Um **plugin OpenClaw** é uma extensão modular que adiciona funcionalidades aos agentes da plataforma OpenClaw. Neste guia, você aprenderá como criar um plugin que integra com uma API externa do zero.

---

## 2. Estrutura de Pastas

A estrutura padrão de um plugin OpenClaw segue este layout:

```
seu-plugin/
├── SKILL.md                              # Metadados e documentação do plugin
├── README.md                             # (Opcional) Documentação completa
├── src/
│   ├── __init__.py                       # Inicializador do módulo
│   ├── main.py                           # Lógica principal do plugin
│   ├── api_client.py                     # Cliente da API externa
│   ├── models.py                         # Schemas e modelos de dados
│   └── utils.py                          # Funções auxiliares
├── tests/
│   ├── __init__.py
│   ├── test_main.py                      # Testes da lógica principal
│   └── test_api_client.py                # Testes do cliente API
├── config/
│   └── config.yaml                       # Configuração do plugin
└── requirements.txt                      # Dependências Python
```

---

## 3. Arquivo Principal: SKILL.md

O arquivo `SKILL.md` é obrigatório. Ele define metadados e documentação do plugin:

```markdown
---
name: meu_plugin_api
description: Plugin para integrar com API externa XYZ. Use para autenticar, buscar dados, processar informações.
dependencies:
  - requests>=2.28.0
  - pydantic>=1.10.0
keywords:
  - api
  - integração
  - dados
---

# Meu Plugin API

## Objetivo
Integrar com uma API externa para realizar operações como autenticação, busca e processamento de dados.

## Funcionalidades Principais

### 1. Autenticação
- Autentica com a API usando tokens ou credenciais
- Mantém sessões ativas

### 2. Busca de Dados
- Realiza requisições GET para buscar informações
- Trata erros e retentativas

### 3. Processamento de Dados
- Valida dados recebidos
- Transforma respostas em formatos utilizáveis

## Como Usar

```python
from src.main import APIIntegration

# Inicializar plugin
api = APIIntegration(api_key="sua_chave")

# Buscar dados
result = api.fetch_data(endpoint="/users", params={"id": 123})

# Processar
processed = api.process(result)
print(processed)
```

## Configuração

Defina variáveis de ambiente:
```bash
export API_KEY="sua_chave_api"
export API_BASE_URL="https://api.exemplo.com"
export API_TIMEOUT=30
```

## Security Guardrails

- Nunca exponha chaves API em logs ou stdout
- Valide todas as respostas da API antes de processar
- Implemente rate limiting para proteger a API
- Use HTTPS apenas
- Sanitize entrada de usuários antes de enviar à API

## Exemplos

### Exemplo 1: Buscar usuários
```python
api = APIIntegration(api_key="token")
users = api.fetch_data("/users")
for user in users:
    print(f"User: {user['name']}")
```

### Exemplo 2: Criar recurso
```python
payload = {"name": "João", "email": "joao@exemplo.com"}
response = api.post("/users", data=payload)
```

---
```

---

## 4. Estrutura de Código - Pseudocódigo

### 4.1 Cliente da API (`src/api_client.py`)

```python
"""
Cliente para integração com API externa.
Responsabilidades:
  - Autenticação
  - Requisições HTTP
  - Tratamento de erros
  - Retentativas e timeouts
"""

import requests
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class APIClient:
    """Cliente base para API externa"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        # Inicializa cliente
        # Valida parametros
        # Configura session HTTP com headers padrão
        pass

    def authenticate(self) -> bool:
        """
        Autentica com a API

        Pseudocódigo:
        1. Prepare credenciais
        2. Faça POST /auth ou similiar
        3. Armazene token em header Authorization
        4. Valide sucesso
        5. Retorne True/False
        """
        pass

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Executa requisição HTTP com retentativas

        Pseudocódigo:
        1. Build URL completa
        2. Merge headers (auth + custom)
        3. Loop com retentativas:
           a. Tente fazer requisição
           b. Se sucesso (2xx): parse JSON e retorne
           c. Se erro 4xx: lance exception com mensagem
           d. Se erro 5xx ou timeout: aguarde e retente
        4. Se todas retentativas falharem: lance exception
        5. Log de sucesso/erro
        """
        pass

    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Atalho para GET"""
        pass

    def post(
        self,
        endpoint: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atalho para POST"""
        pass

    def put(
        self,
        endpoint: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Atalho para PUT"""
        pass

    def delete(
        self,
        endpoint: str
    ) -> Dict[str, Any]:
        """Atalho para DELETE"""
        pass

    def handle_rate_limit(self, retry_after: int):
        """
        Trata rate limiting

        Pseudocódigo:
        1. Log warning
        2. Aguarde retry_after segundos
        3. Retorne para retry automático
        """
        pass
```

### 4.2 Modelos de Dados (`src/models.py`)

```python
"""
Schemas e validação de dados.
Responsabilidades:
  - Validar estrutura de dados
  - Type hints
  - Transformação de dados
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class AuthResponse(BaseModel):
    """Resposta de autenticação"""
    token: str
    expires_in: int
    token_type: str = "Bearer"

    class Config:
        extra = "forbid"  # Rejeita campos desconhecidos

class UserData(BaseModel):
    """Dados de usuário da API"""
    id: str
    name: str
    email: str
    status: str
    created_at: str

    @validator("email")
    def validate_email(cls, v):
        # Valide formato de email
        pass

    class Config:
        extra = "allow"  # Permite campos extras

class ListResponse(BaseModel):
    """Resposta com lista de items"""
    items: List[UserData]
    total: int
    page: int
    page_size: int

class APIError(Exception):
    """Exception customizada para erros de API"""

    def __init__(self, status_code: int, message: str, details: Dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"API Error {status_code}: {message}")
```

### 4.3 Lógica Principal (`src/main.py`)

```python
"""
Interface principal do plugin.
Responsabilidades:
  - Orquestração de operações
  - Abstração de complexidade do cliente
  - Logging e observabilidade
"""

from src.api_client import APIClient
from src.models import UserData, ListResponse, APIError
from typing import List, Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class APIIntegration:
    """Interface principal do plugin"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa integração com API

        Pseudocódigo:
        1. Leia API_KEY de parâmetro ou env
        2. Leia BASE_URL de env
        3. Crie instância de APIClient
        4. Autentique
        5. Defina estado como pronto
        """
        pass

    def fetch_users(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict] = None
    ) -> ListResponse:
        """
        Busca lista de usuários

        Pseudocódigo:
        1. Valide parametros
        2. Build query params com page, page_size, filters
        3. Chame client.get("/users", params=params)
        4. Parse resposta com ListResponse
        5. Log sucesso
        6. Retorne resultado
        7. Em caso de erro: log e re-raise APIError
        """
        pass

    def get_user(self, user_id: str) -> UserData:
        """
        Busca usuário por ID

        Pseudocódigo:
        1. Valide user_id não vazio
        2. Chame client.get(f"/users/{user_id}")
        3. Parse com UserData
        4. Log acesso
        5. Retorne resultado
        """
        pass

    def create_user(
        self,
        name: str,
        email: str
    ) -> UserData:
        """
        Cria novo usuário

        Pseudocódigo:
        1. Valide name e email
        2. Build payload
        3. Chame client.post("/users", data=payload)
        4. Parse com UserData
        5. Log criação
        6. Retorne resultado
        """
        pass

    def process_batch(
        self,
        user_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Processa múltiplos usuários em paralelo

        Pseudocódigo:
        1. Valide lista não vazia
        2. Para cada ID (com thread pool):
           a. Chame get_user(id)
           b. Processe dados
           c. Armazene resultado
        3. Agregue resultados
        4. Retorne resumo com sucessos/falhas
        """
        pass

    def sync_data(self) -> Dict[str, int]:
        """
        Sincroniza todos os dados

        Pseudocódigo:
        1. Log "Iniciando sincronização"
        2. Para cada página de usuários:
           a. Busque página
           b. Validhe cada item
           c. Armazene/atualize localmente
           d. Log progresso
        3. Log "Sincronização completa"
        4. Retorne estatísticas (total, novos, atualizados)
        """
        pass
```

### 4.4 Funções Auxiliares (`src/utils.py`)

```python
"""
Utilidades e helpers do plugin.
"""

import logging
from typing import Any, Dict
from functools import wraps
import time

logger = logging.getLogger(__name__)

def setup_logging(name: str, level: str = "INFO"):
    """Configura logging do plugin"""
    # Setup handler
    # Set formatter
    pass

def retry_on_exception(
    max_attempts: int = 3,
    delay: int = 1,
    backoff: float = 2.0
):
    """
    Decorator para retentativas automáticas

    Pseudocódigo:
    - Wrapa função
    - Em exceção: aguarde delay, multiplique por backoff
    - Retente até max_attempts
    """
    pass

def validate_response(response: Dict[str, Any]) -> bool:
    """
    Valida estrutura de resposta da API

    Pseudocódigo:
    - Verifique campos obrigatórios
    - Valide tipos
    - Retorne True/False
    """
    pass

def sanitize_log(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove dados sensíveis antes de logar

    Pseudocódigo:
    - Identifique campos sensíveis (token, password, key)
    - Substitua por [REDACTED]
    - Retorne cópia segura
    """
    pass
```

### 4.5 Testes (`tests/test_main.py`)

```python
"""
Testes unitários do plugin.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.main import APIIntegration
from src.models import UserData, APIError

class TestAPIIntegration:

    @pytest.fixture
    def api_client(self):
        """Fixture para cliente API mockado"""
        # Retorne mock de APIClient
        pass

    def test_initialization(self):
        """Testa inicialização do plugin"""
        # Arrange: prepare variáveis
        # Act: crie instância
        # Assert: valide estado
        pass

    def test_fetch_users_success(self, api_client):
        """Testa busca de usuários bem-sucedida"""
        # Arrange: mock da resposta
        # Act: chame fetch_users
        # Assert: valide resultado
        pass

    def test_fetch_users_with_filters(self):
        """Testa busca com filtros"""
        # Arrange
        # Act
        # Assert
        pass

    def test_fetch_users_api_error(self):
        """Testa tratamento de erro de API"""
        # Arrange: mock erro 500
        # Act
        # Assert: valide exception e logging
        pass

    def test_create_user(self):
        """Testa criação de usuário"""
        # Arrange
        # Act
        # Assert
        pass

    def test_invalid_email(self):
        """Testa validação de email"""
        # Arrange: email inválido
        # Act
        # Assert: valide validation error
        pass
```

---

## 5. Arquivo de Configuração (`config/config.yaml`)

```yaml
# Configuração do plugin
plugin:
  name: meu_plugin_api
  version: "1.0.0"
  description: "Integração com API externa XYZ"

# Configuração da API
api:
  base_url: "${API_BASE_URL:https://api.exemplo.com}"
  timeout: "${API_TIMEOUT:30}"
  max_retries: "${API_RETRIES:3}"
  verify_ssl: "${API_VERIFY_SSL:true}"

# Logging
logging:
  level: "${LOG_LEVEL:INFO}"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Rate limiting
rate_limit:
  enabled: true
  requests_per_minute: 60
  burst_size: 10

# Cache
cache:
  enabled: true
  ttl_seconds: 300
  max_size_mb: 100
```

---

## 6. Dependências (`requirements.txt`)

```
requests>=2.28.0
pydantic>=1.10.0
python-dotenv>=0.20.0
pytest>=7.0.0
pytest-asyncio>=0.20.0
pytest-mock>=3.10.0
```

---

## 7. Integração com OpenClaw

### 7.1 Estrutura Esperada no Workspace

```
/data/openclaw/workspace-<agente>/skills/seu_plugin_api/
├── SKILL.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api_client.py
│   └── models.py
├── tests/
└── requirements.txt
```

### 7.2 Carregamento do Plugin

O OpenClaw carrega automaticamente plugins do workspace se:
1. Estão em `skills/<nome_plugin>/`
2. Possuem `SKILL.md` com frontmatter
3. Estão acessíveis via Python (instalado ou PYTHONPATH)

### 7.3 Uso dentro de Skills

```python
# Em outro SKILL.md, você pode usar seu plugin:
from src.main import APIIntegration

api = APIIntegration(api_key=os.getenv("API_KEY"))
users = api.fetch_users()

# Processe dados e retorne resultado
```

---

## 8. Checklist de Implementação

- [ ] Criar estrutura de pastas
- [ ] Escrever `SKILL.md` com metadados
- [ ] Implementar `APIClient` com autenticação
- [ ] Definir modelos Pydantic em `models.py`
- [ ] Criar interface `APIIntegration` em `main.py`
- [ ] Implementar utilidades em `utils.py`
- [ ] Escrever testes em `tests/`
- [ ] Adicionar `requirements.txt`
- [ ] Testar localmente com `pytest`
- [ ] Integrar ao workspace OpenClaw
- [ ] Validar carregamento no container

---

## 9. Exemplo Completo Mínimo

Para começar rápido, use este template mínimo:

```
minimal_plugin/
├── SKILL.md
└── src/
    ├── __init__.py
    └── main.py
```

**SKILL.md:**
```markdown
---
name: minimal_plugin
description: Plugin mínimo de exemplo
---
# Minimal Plugin
```

**src/main.py:**
```python
import requests

class MinimalIntegration:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def fetch(self):
        response = requests.get(self.api_url)
        return response.json()
```

---

## 10. Próximos Passos

1. **Clonar template**: Use a estrutura acima como base
2. **Adaptar para sua API**: Ajuste endpoints, headers, autenticação
3. **Escrever testes**: Garanta cobertura mínima de 80%
4. **Documentar**: Atualize SKILL.md com exemplos específicos
5. **Integrar**: Coloque no workspace OpenClaw
6. **Monitorar**: Adicione logging e observabilidade
7. **Iterar**: Melhore baseado em feedback

---

## Referências

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [AgentSkills Format](https://agentskills.io)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [Python Requests Library](https://requests.readthedocs.io)
