# BOOT.md - Dev_Mobile

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação, stack e plataformas alvo.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json`.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/dev_mobile/MEMORY.md` — resgatar aprendizados próprios de mobile relevantes.
8. Validar `/data/openclaw/` e workspace de implementação.
9. Detectar framework mobile pelo `technology_stack` da task ou por arquivos (`app.json`, `expo.json`, `pubspec.yaml`).
10. Identificar plataforma alvo: iOS, Android ou ambas.
11. Carregar comandos padrão por framework (Expo/EAS ou Flutter).
12. Validar ferramentas no PATH: `node`, `npm`, `npx`, `expo`, `eas-cli` (ou `flutter`, `dart`).
13. Verificar ferramentas: `read`, `write`, `exec`, `git`, `sessions_send`.
14. Verificar presença de artefatos UX em `/data/openclaw/backlog/ux/` para tasks com escopo de tela.
15. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/dev_mobile/MEMORY.md`.
16. Pronto para receber task do Arquiteto.

## healthcheck
- `/data/openclaw/` acessível? ✅
- INPUT_SCHEMA.json carregado? ✅
- Framework mobile detectado? ✅
- Plataforma alvo identificada? ✅
- SHARED_MEMORY.md e MEMORY.md (dev_mobile) lidos? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅
