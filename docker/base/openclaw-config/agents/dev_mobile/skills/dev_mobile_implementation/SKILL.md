---
name: dev_mobile_implementation
description: Mobile implementation skills for tasks, tests and status updates
---

# Dev_Mobile Skills

---

## Implement Task Mobile

Use when the scheduled 1h cycle encounters an issue with label `mobile` or when delegated by the Architect.

Workflow:
1. Read `TASK-XXX`, `US-XXX`, `UX-XXX` (if exists) and `ADR`.
2. Identify framework (`app.json` = Expo; `pubspec.yaml` = Flutter) and target platform.
3. Implement screens and mobile components within the scope of the task.
4. Run lint/test/build/e2e.
5. Update issue/PR with technical summary + performance metrics.
6. Report to Architect with evidence.

---

## Appointment of 1 hour (Required)

- Every 60 minutes (offset :15), query GitHub for issues with label `mobile`.
- Process only: `mobile`
- Ignore: `back_end`, `front_end`, `tests`, `dba`, `devops`, `documentacao`

---

## Routing for QA (Dev-QA Loop)

After implementation and opening of PR:
1. Delegate to QA_Engineer via `sessions_spawn` / `sessions_send`.
2. Wait for QA report.
3. PASS → close the cycle and report to the Architect.
4. FAIL → fix and re-delegate (retry, max 3x).
5. 3rd FAIL → escalate to Architect with history.

---

## Stack React Native + Expo (Default)

```bash
npm ci
npx expo lint
npx expo start --no-dev --minify   # smoke test
npx jest --coverage
npx detox test                     # e2e (quando configurado)
eas build --platform all --profile preview  # build pipeline
```

## Stack Flutter (Alternative)

```bash
flutter pub get
flutter analyze
flutter test --coverage
flutter build apk --release
flutter build ios --release        # requer macOS host
```

---

## Mobile Security Guardrails

- Never hardcode secrets: use `EAS Secrets`, `react-native-config`, or `flutter_dotenv`.
- Implement certificate pinning when SPEC requires it.
- Follow OWASP Mobile Top 10.
- Do not expose user data in production logs.

---

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (97-98% redução de tokens).

### Ferramentas Otimizadas

#### NPM/Expo (Node Package Manager)
```bash
# ❌ NÃO USE: npm list, npx expo list
# ✅ USE ESTE: npm list --depth=0

# Economia: 142KB → 3KB (97.9% ↓)
```

#### GIT (Version Control)
```bash
# ❌ NÃO USE: git log --all
# ✅ USE ESTE: git log -20 --oneline

# Economia: 315KB → 2KB (99.4% ↓)
```

#### Build Logs (Expo/Flutter)
```bash
# ❌ NÃO USE: Logs completos (200KB+)
# ✅ USE ESTE: Apenas warnings e errors
npx expo build:ios 2>&1 | grep -E "ERROR|WARNING" | tail -50

# Economia: 95%+ ↓
```

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```

---

## Multi-Agent Label Routing

| Label | Responsible agent |
|-------|-------------------|
| `mobile` | Dev_Mobile (this agent) |
| `front_end` | Dev_Frontend |
| `back_end` | Dev_Backend |
| `tests` | QA_Engineer |
| `devops` | DevOps_SRE |
