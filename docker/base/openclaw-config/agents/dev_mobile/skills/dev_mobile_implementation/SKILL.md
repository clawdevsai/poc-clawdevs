<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

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

## Multi-Agent Label Routing

| Label | Responsible agent |
|-------|-------------------|
| `mobile` | Dev_Mobile (this agent) |
| `front_end` | Dev_Frontend |
| `back_end` | Dev_Backend |
| `tests` | QA_Engineer |
| `devops` | DevOps_SRE |