# Validação do Bug dos Agents Vazios

## Problema
O endpoint `/agents` retorna uma lista vazia mesmo com os pods rodando no Kubernetes.

## Mudanças Realizadas

### 1. Logging Detalhado em `sync_agents()`
**Arquivo:** `control-panel/backend/app/services/agent_sync.py`
- Adicionado logging para rastrear cada agent criado/atualizado
- Adicionado logging final com contagem total de agents no DB
- Tratamento explícito de erros com stack trace
- Logging em `parse_identity()` para debug de leitura de configurações

### 2. Tratamento de Erro em Bootstrap
**Arquivo:** `control-panel/backend/app/main.py`
- Adicionado try-except em `bootstrap_agents()` com logging detalhado
- Agora erros durante a sincronização inicial são capturados e logados

### 3. Logging no Endpoint
**Arquivo:** `control-panel/backend/app/api/agents.py`
- Adicionado logging em `list_agents()` mostrando quantos agents estão no DB
- Novo endpoint `/agents/admin/sync` (POST) para sincronizar manualmente

## Como Validar

### Opção 1: Verificar Logs da Aplicação
```bash
# Dentro do cluster Kubernetes
kubectl logs deployment/clawdevs-panel-backend -f

# Procure por linhas como:
# - "Starting sync_agents for 12 agents"
# - "✓ Created agent: ceo (Leonardo)"
# - "✓ Agent sync completed: 12 created, 0 updated"
# - "Total agents in database: 12"
```

### Opção 2: Testar Endpoint de Sincronização Manual
```bash
# Trigger sync manualmente (requer autenticação de admin)
curl -X POST http://127.0.0.1:50968/agents/admin/sync \
  -H "Authorization: Bearer <token-do-admin>"

# Esperado:
# {
#   "message": "Synchronized 12 new agents",
#   "created": 12,
#   "updated": 0,
#   "total": 12
# }
```

### Opção 3: Script de Debug
```bash
# Na raiz do projeto
python debug_agents.py

# Este script:
# - Conecta ao banco de dados
# - Chama sync_agents() manualmente
# - Verifica se agents foram criados
# - Mostra log detalhado do processo
```

### Opção 4: Verificar Endpoint GET
```bash
curl http://127.0.0.1:50968/agents

# Esperado: lista com 12 agents
# {
#   "items": [
#     {
#       "slug": "arquiteto",
#       "display_name": "Henrique",
#       "role": "Architect",
#       ...
#     },
#     ...
#   ],
#   "total": 12
# }
```

## Diagnóstico Esperado

Após as mudanças, você deve ver nos logs:

1. **Se os agents foram criados com sucesso:**
   ```
   Starting sync_agents for 12 agents
   ✓ Created agent: ceo (Leonardo)
   ✓ Created agent: po (Camila)
   ...
   ✓ Agent sync completed: 12 created, 0 updated
   ✓ Total agents in database: 12
   ```

2. **Se houver erro na sincronização:**
   ```
   Error syncing agent dev_backend: [erro específico]
   ✗ Failed to sync agents: [detalhes do erro]
   ```

3. **Se o banco de dados não estiver acessível:**
   ```
   Agent bootstrap failed: [erro de conexão]
   ```

## Possíveis Causas Identificadas

1. **Migrações não rodaram:** Verifique se `PANEL_RUN_DB_MIGRATIONS_ON_STARTUP=true`
2. **Conexão com banco falhou:** Verifique `PANEL_DATABASE_URL`
3. **OpenClaw data path incorreto:** Verifique `PANEL_OPENCLAW_DATA_PATH` (default: `/data/openclaw`)
4. **Permissões de arquivo:** O deployment tenta ajustar permissões em `/data/openclaw`

## Próximos Passos

1. **Verificar logs** da aplicação rodando
2. **Testar endpoint de sync** manual se os logs revelarem erro
3. **Confirmar** que o GET `/agents` retorna 12 agents
4. Se tudo funcionar → **Fazer commit** das mudanças

## Revert (Se Necessário)
```bash
git reset --hard HEAD~1
```
(Volta para commit anterior se precisar descartar as mudanças)
