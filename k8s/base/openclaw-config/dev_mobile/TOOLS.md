# TOOLS.md - Dev_Mobile

## tools_disponíveis
- `read(path)`: ler arquivos da task/projeto e artefatos UX.
- `write(path, content)`: escrever screens/componentes/testes/docs.
- `exec(command)`: executar build/test/lint mobile.
- `gh(args...)`: atualizar issues/PRs e consultar workflows.
- `git(args...)`: commit/branch/merge sem comandos destrutivos.
- `sessions_spawn(agentId, mode, label)`: criar sessão com Arquiteto ou QA_Engineer.
- `sessions_send(session_id, message)`: enviar update ou delegar ao QA_Engineer.
- `sessions_list()`: listar sessões ativas.
- `browser`: referência de implementação ou documentação de plataforma.
- `internet_search(query)`: boas práticas mobile, performance, segurança.

## regras_de_uso
- `read/write` somente em `/data/openclaw/**`.
- Bloquear comandos destrutivos (`rm -rf`, `git push -f`, etc.).
- `gh` sempre com `--repo "$ACTIVE_GITHUB_REPOSITORY"`.
- Validar `active_repository.env` antes de qualquer ação gh/git.
- Poll de fila GitHub 1x por hora (offset :30):
  - `gh issue list --state open --label mobile --limit 20 --repo "$ACTIVE_GITHUB_REPOSITORY"`
- Processar somente label `mobile`.
- `sessions_spawn` permitido para: `arquiteto`, `qa_engineer`.

## github_permissions
- **Tipo:** `read+write`
- **Label própria:** `mobile` — criar automaticamente no boot se não existir:
  `gh label create "mobile" --color "#e4e669" --description "Mobile tasks — routed to Dev_Mobile" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true`
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
- **Proibido:** override de repositório, operações fora do `ACTIVE_GITHUB_REPOSITORY`

## comandos_adicionais_mobile
- `expo`: `npx expo start`, `npx expo lint`, `eas build`, `eas submit`
- `flutter`: `flutter test`, `flutter build apk`, `flutter build ios`
- `detox`: `npx detox test` (e2e React Native)
- `maestro`: `maestro test` (e2e cross-platform)

## autonomia_de_pesquisa_e_aprendizado
- Permissão total de acesso à internet para pesquisa, atualização de habilidades e descoberta de melhores alternativas mobile.
- Usar `browser` e `internet_search` livremente para:
  - descobrir SDKs, bibliotecas e ferramentas de build mais eficientes para o problema
  - verificar CVEs e vulnerabilidades em dependências nativas e JS mobile
  - comparar benchmarks de startup time, bundle size e performance entre alternativas
  - ler documentação oficial de iOS, Android, Expo, Flutter e React Native
  - aprender padrões emergentes de performance mobile e app store compliance
- Citar fonte e data da informação nos artefatos produzidos.

## rate_limits
- `exec`: 120 comandos/hora
- `gh`: 50 req/hora
- `sessions_spawn`: 10/hora
- `internet_search`: 60 queries/hora
