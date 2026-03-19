# TOOLS.md - Arquiteto

## tools_disponiveis
- `read(path)`: Ler arquivo concreto. Validar prefixo `/data/openclaw/backlog` e bloquear `..`.
- `write(path, content)`: Escrever artefato após validação de estrutura/schema.
- `exec(cmd)`: Executar comandos operacionais controlados (`git`, `gh`, `mkdir`, `mv`) para pipeline de publicação.
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
- Em criação/edição de issue usar `--body-file <arquivo.md>`; não usar `--body` inline com `\n`.
- Body deve conter seções obrigatórias: `Objetivo`, `O que desenvolver`, `Como desenvolver`, `Critérios de aceitação`, `Definição de pronto (DoD)`.
- Ordem obrigatória de publicação: `docs -> commit -> issues -> validação -> session_finished`.
- Docs da sessão devem ser publicados em `/data/openclaw/backlog/implementation/docs`.
- Encerramento de sessão deve mover artefatos para `/data/openclaw/backlog/session_finished/<session_id>/`.
- Se falhar commit ou issue: notificar PO imediatamente; não finalizar sessão.
- Rate limits:
  - `write`: 20 arquivos/hora
  - `gh`: 50 requisições/hora
  - `sessions_spawn`: 10 sessões/hora
  - `internet_search`: 30 queries/hora
- `research` deve iniciar timer e encerrar em 2h com fallback.
