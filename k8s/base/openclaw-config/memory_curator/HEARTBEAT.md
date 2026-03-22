# HEARTBEAT.md - Memory_Curator

Diariamente às 2h (cron: `0 2 * * *`, TZ: America/Sao_Paulo):

1. **Inicializar** — Definir `MEMORY_BASE=/data/openclaw/memory`; verificar que o diretório existe
2. **Coletar padrões** — Para cada agente em `ceo po arquiteto dev_backend dev_frontend dev_mobile qa_engineer security_engineer devops_sre ux_designer dba_data_engineer`:
   - Ler `${MEMORY_BASE}/<id>/MEMORY.md`
   - Extrair todas as linhas de `## Active Patterns` (linhas iniciadas com `- [PATTERN]`)
   - Armazenar lista de padrões com origem (agent_id)
3. **Identificar padrões cruzados** — Agrupar padrões semanticamente similares entre agentes:
   - Usar LLM para comparar descrições e identificar equivalências
   - Padrões com 3+ origens distintas → candidatos à promoção
4. **Promover para SHARED_MEMORY.md** — Para cada padrão candidato:
   - Verificar se já existe em `${MEMORY_BASE}/shared/SHARED_MEMORY.md`
   - Se não existe: adicionar `- [GLOBAL] <descrição consolidada> | Promovido: <data> | Origem: <agentes>`
   - Se já existe: atualizar campo `Origem` com novos agentes se necessário
5. **Arquivar nos agentes de origem** — Para cada padrão promovido:
   - Em cada MEMORY.md de agente de origem: mover linha de `## Active Patterns` → `## Archived`
   - Adicionar sufixo `| Arquivado: <data> | Motivo: Promovido para SHARED_MEMORY`
6. **Gerar relatório** — Escrever em `/data/openclaw/backlog/status/memory-curator.log`:
   - Timestamp do ciclo
   - Agentes processados (N)
   - Padrões coletados (total)
   - Padrões promovidos no ciclo (N novos)
   - Padrões arquivados nos agentes (N)
   - Erros encontrados (0 esperado)
