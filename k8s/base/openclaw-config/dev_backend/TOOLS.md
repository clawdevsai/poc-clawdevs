# TOOLS.md - Dev_Backend

## tools_disponiveis
- `read(path)`: ler arquivos da task/projeto (com validação de path).
- `write(path, content)`: escrever código/testes/docs (com validação).
- `exec(command)`: executar comandos de build/test/lint.
- `exec("gh <args>")`: atualizar issues/PRs e consultar execuções de workflow, checks, labels e run logs (gh run view/rerun/list).
- `git(args...)`: operações de commit/branch/merge sem comandos destrutivos.
- `sessions_spawn(agentId, mode, label)`: criar sessão com Arquiteto.
- `sessions_send(session_id, message)`: enviar update.
- `sessions_list()`: listar sessões.
- `exec("web-search '<query>'")`: pesquisar na internet via SearxNG (agrega Google, Bing, DuckDuckGo). Retorna até 10 resultados. Exemplo: `web-search "python asyncio best practices 2025"`
- `exec("web-read '<url>'")`: ler qualquer página web como markdown limpo via Jina Reader. Exemplo: `web-read "https://docs.python.org/3/library/asyncio.html"`

## regras_de_uso
- `read/write` somente em `/data/openclaw/**`.
- Bloquear comandos destrutivos (`rm -rf`, `git push -f`, etc.).
- Comandos GitHub devem usar `exec('gh ... --repo "$ACTIVE_GITHUB_REPOSITORY"')`.
- Validar `/data/openclaw/contexts/active_repository.env` antes de qualquer ação gh/git.
- Comunicação interagente com chave `agent:<id>:main` deve usar `sessions_send` (nunca `message`).
- `message` é somente para destinos de canal (ex.: Telegram `chatId`), nunca para sessão de agente.
- Antes de ler arquivos de stack (`package.json`, `go.mod`, etc.), validar existência com `read` no diretório alvo.
- Se `PROJECT_ROOT` não tiver código-fonte, usar `/data/openclaw/backlog/implementation` como fallback e registrar `standby` sem erro.
- `gh` com paridade operacional ao Arquiteto para leitura/atualização de CI, issues e PRs (sem operações destrutivas).
- Poll de fila GitHub 1x por hora:
  - exemplo: `gh issue list --state open --label back_end --limit 20 --repo "$ACTIVE_GITHUB_REPOSITORY"`
- Processar somente label `back_end`.
- Ignorar labels: `front_end`, `tests`, `dba`, `devops`, `documentacao`.
- Sempre executar testes antes de reportar conclusão.
- Sempre reportar impacto de custo/performance da solução implementada.
- Se task trouxer `## Comandos`, usar esses comandos em vez de defaults.
- Internet: acesso total liberado para pesquisa técnica, descoberta de alternativas, CVEs, benchmarks e atualização de habilidades — sem restrição de fonte.

## github_permissions
- **Tipo:** `read+write`
- **Label própria:** `back_end` — criar automaticamente no boot se não existir:
  `gh label create "back_end" --color "#1d76db" --description "Backend tasks — routed to Dev_Backend" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true`
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
- **Proibido:** override de repositório, operações fora do `ACTIVE_GITHUB_REPOSITORY`

## autonomia_de_pesquisa_e_aprendizado
- Permissão total de acesso à internet para pesquisa, atualização de habilidades e descoberta de melhores alternativas.
- Usar `exec("web-search '...'")` e `exec("web-read '...'")` livremente para:
  - descobrir frameworks, bibliotecas e ferramentas mais eficientes para o problema
  - verificar CVEs, vulnerabilidades e security advisories atualizados em dependências
  - comparar benchmarks de performance e custo entre alternativas tecnológicas
  - ler documentação oficial, changelogs e release notes das tecnologias usadas
  - aprender padrões emergentes que reduzam custo ou aumentem performance
- Citar fonte e data da informação nos artefatos produzidos.

## rate_limits
- `exec`: 120 comandos/hora
- `gh`: 50 req/hora
- `sessions_spawn`: 10/hora
- `web-search`: 60 queries/hora

## inter_agent_sessions

Comunicacao entre agentes via sessao persistente:

- **Session key format:** `agent:<id>:main` (ex: `agent:arquiteto:main`, `agent:ceo:main`)
- **Descoberta:** `sessions_list()` filtrando `kind: main` para obter session keys ativas
- **`sessions_spawn`:** delegacao hierarquica background - orquestrador delega task a subagente; resultado volta via announce chain
- **`sessions_send`:** peer-to-peer sincrono - reportar status, escalar incidente, enviar resultado; ping-pong ate 5 turnos
- **Proibido:** usar `message` com `agent:<id>:main` (isso quebra em canais como Telegram com `Unknown target`)

Agentes disponiveis e suas keys:
- CEO: `agent:ceo:main`
- PO: `agent:po:main`
- Arquiteto: `agent:arquiteto:main`
- Dev_Backend: `agent:dev_backend:main`
- Dev_Frontend: `agent:dev_frontend:main`
- Dev_Mobile: `agent:dev_mobile:main`
- QA_Engineer: `agent:qa_engineer:main`
- DevOps_SRE: `agent:devops_sre:main`
- Security_Engineer: `agent:security_engineer:main`
- UX_Designer: `agent:ux_designer:main`
- DBA_DataEngineer: `agent:dba_data_engineer:main`

