# BOOTSTRAP.md - PO

Preparação para operação contínua:
1. Carregar configurações do ambiente:
   - `DIRECTORS_NAME`
   - `GITHUB_ORG` (formato `owner`)
   - `ACTIVE_GITHUB_REPOSITORY` (formato `owner/repo`)
   - `OPENCLAW_ENV` (`production` ou `staging`)
2. Ler `README.md` do repositorio para entender o projeto e o fluxo antes de estruturar backlog.
3. Validar diretório base `/data/openclaw/backlog` e subpastas obrigatórias:
   - `idea/`, `user_story/`, `tasks/`, `planning/`, `briefs/`
4. Inicializar diretórios operacionais:
   - `/data/openclaw/backlog/status`
   - `/data/openclaw/backlog/audit`
5. Estabelecer logger:
   - audit trail em JSONL
   - nível mínimo INFO, eventos de segurança em WARN/ERROR
6. Carregar whitelists de segurança:
   - labels permitidas do GitHub
   - domínios permitidos para pesquisa
7. Verificar ferramentas obrigatórias (`read`, `write`, `sessions_spawn`, `sessions_send`, `gh`).
8. Se qualquer check falhar, abortar com erro claro ao CEO.
9. Pronto.

Notas operacionais:
- `gh` pode ser usado para consultar issues, PRs, labels e workflows.
- Criação de PRs e commits continua delegada ao Arquiteto.
