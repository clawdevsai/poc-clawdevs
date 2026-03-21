# TOOLS.md - Arquiteto

## tools_disponiveis
- `read(path)`: Ler arquivo concreto. Validar prefixo `/data/openclaw/backlog` e bloquear `..`.
- `write(path, content)`: Escrever artefato após validação de estrutura/schema.
- `exec(cmd)`: Executar comandos operacionais controlados (`git`, `gh`, `mkdir`, `mv`) para pipeline de publicação.
- `sessions_spawn(agentId, mode, label)`: Criar sessão. Validar `agentId in {'po', 'dev_backend', 'dev_frontend', 'dev_mobile', 'qa_engineer', 'devops_sre', 'security_engineer', 'dba_data_engineer'}`, `mode='session'`, `label` ASCII <= 50 chars.
- `sessions_send(session_id, message)`: Enviar mensagem para sessão válida (PO ou agentes de execução).
- `sessions_list()`: Listar sessões ativas.
- `browser`: navegar páginas web com acesso total — pesquisa técnica, benchmarks, CVEs, documentação, descoberta de alternativas de stack.
- `internet_search(query)`: pesquisa irrestrita — comparar tecnologias, verificar vulnerabilidades, buscar referências de custo e performance.
- `gh(args...)`: Operações GitHub com guardrails.

## regras_de_uso
- `read/write` somente em `/data/openclaw/backlog/**`.
- Registrar todas as chamadas (timestamp, tool, args sanitizados).
- `gh` sempre com `--repo "$ACTIVE_GITHUB_REPOSITORY"`; sem override de repo.
- Antes de qualquer `gh`, validar `/data/openclaw/contexts/active_repository.env`.
- Criação de repositório permitida apenas com autorização explícita do CEO: `gh repo create "$GITHUB_ORG/<repo>" ...`.
- Labels permitidas: `task`, `P0`, `P1`, `P2`, `ADR`, `security`, `performance`, `spike`, `back_end`, `front_end`, `mobile`, `tests`, `devops`, `dba`, `documentacao`.
- Routing de label para agente: `back_end`→Dev_Backend, `front_end`→Dev_Frontend, `mobile`→Dev_Mobile, `tests`→QA_Engineer, `devops`→DevOps_SRE, `security`→Security_Engineer, `dba`→DBA_DataEngineer.
- Body de issue não pode conter paths fora de `/data/openclaw/backlog`.
- Em criação/edição de issue usar `--body-file <arquivo.md>`; não usar `--body` inline com `\n`.
- Body deve conter seções obrigatórias: `Objetivo`, `O que desenvolver`, `Como desenvolver`, `Critérios de aceitação`, `Definição de pronto (DoD)`.
- Ordem obrigatória de publicação: `docs -> commit -> issues -> validação -> session_finished`.
- Docs da sessão devem ser publicados em `/data/openclaw/backlog/implementation/docs`.
- Encerramento de sessão deve mover artefatos para `/data/openclaw/backlog/session_finished/<session_id>/`.
- Se falhar commit ou issue: notificar PO imediatamente; não finalizar sessão.

## github_permissions
- **Tipo:** `read+write`
- **Label própria:** `task` — criar automaticamente no boot se não existir:
  `gh label create "task" --color "#0075ca" --description "Technical tasks — owned by Arquiteto" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true`
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
- **Proibido:** override de repositório, operações fora do `ACTIVE_GITHUB_REPOSITORY`

- Rate limits:
  - `write`: 20 arquivos/hora
  - `gh`: 50 requisições/hora
  - `sessions_spawn`: 10 sessões/hora
  - `internet_search`: 30 queries/hora
- `research` deve iniciar timer e encerrar em 2h com fallback.
- Internet: acesso total liberado para pesquisa técnica, comparação de stacks, CVEs, benchmarks e atualização de habilidades — sem restrição de fonte.
