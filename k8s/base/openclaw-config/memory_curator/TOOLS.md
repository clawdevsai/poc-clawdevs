# TOOLS.md - Memory_Curator

## tools_disponíveis
- `read(path)`: Ler MEMORY.md de agentes e SHARED_MEMORY.md. Validar que path começa com `/data/openclaw/memory/` e não contém `..`.
- `write(path, content)`: Escrever em MEMORY.md de agentes (mover padrões para Archived) e em SHARED_MEMORY.md (adicionar padrões globais). Validar schema antes de persistir.
- `exec("tail -n 100 /data/openclaw/backlog/status/memory-curator.log")`: Consultar log do ciclo anterior.

## regras_de_uso
- `read` e `write` somente em `/data/openclaw/memory/**`.
- Nunca deletar linhas de MEMORY.md — apenas mover entre seções (`Active Patterns` → `Archived`).
- Nunca escrever em workspace de agente fora de `/data/openclaw/memory/`.
- Nunca gravar em `/data/openclaw/backlog/` exceto no arquivo de log: `/data/openclaw/backlog/status/memory-curator.log`.
- Nunca interagir com GitHub API (`gh`, `git`, etc.).
- Operação idempotente: rodar duas vezes deve produzir o mesmo resultado que rodar uma vez.

## paths_autorizados
- Leitura de agentes: `/data/openclaw/memory/<id>/MEMORY.md`
  - IDs permitidos: `ceo`, `po`, `arquiteto`, `dev_backend`, `dev_frontend`, `dev_mobile`, `qa_engineer`, `security_engineer`, `devops_sre`, `ux_designer`, `dba_data_engineer`, `memory_curator`
- Escrita shared: `/data/openclaw/memory/shared/SHARED_MEMORY.md`
- Log: `/data/openclaw/backlog/status/memory-curator.log`

## proibições
- Sem `sessions_spawn`, `sessions_send` ou `sessions_list` — não se comunica com outros agentes
- Sem `exec("gh ...")` ou qualquer operação GitHub
- Sem escrita fora de `/data/openclaw/memory/`
