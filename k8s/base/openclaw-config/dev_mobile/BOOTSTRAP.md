# BOOTSTRAP.md - Dev_Mobile

1. Carregar env:
   - `GITHUB_ORG`
   - `ACTIVE_GITHUB_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT` (default `/data/openclaw/backlog/implementation`)
2. Ler `README.md` do repositório para entender app, stack e plataformas alvo.
3. Detectar framework por arquivos:
   - `app.json` / `expo.json` → React Native + Expo
   - `pubspec.yaml` → Flutter
   - `package.json` + `react-native` → React Native bare
4. Identificar plataforma: verificar `app.json.expo.platforms` ou ADR da task.
5. Definir comandos padrão por framework.
6. Verificar toolchain no PATH:
   - Expo: `node`, `npm`, `npx`, `expo`, `eas`
   - Flutter: `flutter`, `dart`
7. Configurar logger com `task_id`, `framework` e `platform`.
8. Verificar artefatos UX em `/data/openclaw/backlog/ux/`.
9. Habilitar pesquisa técnica na internet para boas práticas mobile.
10. Validar autenticação `gh` e permissões do repositório ativo.
11. Configurar agendamento:
    - intervalo fixo: 60 minutos (offset: :30 de cada hora)
    - origem de trabalho: issues GitHub label `mobile`
12. Pronto.
