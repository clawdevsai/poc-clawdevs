# TOOLS.md - Arquiteto

## tools_disponiveis
- `read(path)`: Ler arquivo concreto. Validar prefixo `/data/openclaw/backlog` e bloquear `..`.
- `write(path, content)`: Escrever artefato após validação de estrutura/schema.
- `sessions_spawn(agentId, mode, label)`: Criar sessão. Validar `agentId in {'po'}`, `mode='session'`, `label` ASCII <= 50 chars.
- `sessions_send(session_id, message)`: Enviar mensagem para sessão válida do PO.
- `sessions_list()`: Listar sessões ativas.
- `internet_search(query)`: Pesquisa técnica em fontes confiáveis com rate limit.
- `gh(args...)`: Operações GitHub com guardrails.

## regras_de_uso
- `read/write` somente em `/data/openclaw/backlog/**`.
- Registrar todas as chamadas (timestamp, tool, args sanitizados).
- `gh` sempre com `--repo "$GITHUB_REPOSITORY"`; sem override de repo.
- Labels permitidas: `task`, `P0`, `P1`, `P2`, `ADR`, `security`, `performance`, `spike`.
- Body de issue não pode conter paths fora de `/data/openclaw/backlog`.
- Rate limits:
  - `write`: 20 arquivos/hora
  - `gh`: 50 requisições/hora
  - `sessions_spawn`: 10 sessões/hora
  - `internet_search`: 30 queries/hora
- `research` deve iniciar timer e encerrar em 2h com fallback.
