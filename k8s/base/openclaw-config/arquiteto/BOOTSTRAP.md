# BOOTSTRAP.md - Arquiteto

Preparação para operação contínua:
1. Carregar configurações:
   - `GITHUB_REPOSITORY` (formato `owner/repo`)
   - `GITHUB_TOKEN` (se disponível)
   - `OPENCLAW_ENV` (`production` ou `staging`)
   - `MAX_RESEARCH_TIME_PER_US` (default 2h)
2. Validar `/data/openclaw/backlog` e subpastas:
   - `idea/`, `user_story/`, `tasks/`, `architecture/`, `briefs/`
   - `implementation/docs/`
   - `session_finished/`
3. Inicializar diretórios operacionais:
   - `/data/openclaw/backlog/status`
   - `/data/openclaw/backlog/audit`
   - `/data/openclaw/backlog/implementation/docs`
   - `/data/openclaw/backlog/session_finished`
4. Estabelecer logger com eventos de segurança e auditoria.
5. Carregar whitelists:
   - labels GitHub permitidas
   - domínios confiáveis de research
   - agentes permitidos para sessão (`po`)
6. Validar ferramentas obrigatórias (`read`, `write`, `sessions_spawn`, `sessions_send`, `gh`).
7. Se faltar qualquer requisito, abortar com erro claro para o PO.
8. Pronto.
