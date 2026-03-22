---
name: dev_mobile_implementation
description: Skill de implementação mobile para tasks, testes e atualização de status
---

# Skills do Dev_Mobile

---

## Implementar Task Mobile

Use quando o ciclo agendado de 1h encontrar issue com label `mobile` ou quando delegado pelo Arquiteto.

Workflow:
1. Ler `TASK-XXX`, `US-XXX`, `UX-XXX` (se existir) e `ADR`.
2. Identificar framework (`app.json` = Expo; `pubspec.yaml` = Flutter) e plataforma alvo.
3. Implementar screens e componentes mobile no escopo da task.
4. Executar lint/test/build/e2e.
5. Atualizar issue/PR com resumo técnico + métricas de performance.
6. Reportar ao Arquiteto com evidências.

---

## Agendamento de 1h (Obrigatório)

- A cada 60 minutos (offset :30), consultar GitHub por issues com label `mobile`.
- Processar apenas: `mobile`
- Ignorar: `back_end`, `front_end`, `tests`, `dba`, `devops`, `documentacao`

---

## Roteamento para QA (Dev-QA Loop)

Após implementação e abertura de PR:
1. Delegar ao QA_Engineer via `sessions_spawn` / `sessions_send`.
2. Aguardar relatório do QA.
3. PASS → fechar ciclo e reportar ao Arquiteto.
4. FAIL → corrigir e re-delegar (retry, max 3x).
5. 3º FAIL → escalar ao Arquiteto com histórico.

---

## Stack React Native + Expo (Padrão)

```bash
npm ci
npx expo lint
npx expo start --no-dev --minify   # smoke test
npx jest --coverage
npx detox test                     # e2e (quando configurado)
eas build --platform all --profile preview  # build pipeline
```

## Stack Flutter (Alternativa)

```bash
flutter pub get
flutter analyze
flutter test --coverage
flutter build apk --release
flutter build ios --release        # requer macOS host
```

---

## Guardrails de Segurança Mobile

- Nunca hardcodar secrets: usar `EAS Secrets`, `react-native-config`, ou `flutter_dotenv`.
- Implementar certificate pinning quando a SPEC exigir.
- Seguir OWASP Mobile Top 10.
- Não expor dados do usuário em logs de produção.

---

## Multi-Agent Routing de Labels

| Label | Agente responsável |
|-------|-------------------|
| `mobile` | Dev_Mobile (este agente) |
| `front_end` | Dev_Frontend |
| `back_end` | Dev_Backend |
| `tests` | QA_Engineer |
| `devops` | DevOps_SRE |
