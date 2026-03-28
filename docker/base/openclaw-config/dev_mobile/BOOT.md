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

# BOOT.md - Dev_Mobile

## Boot Sequence

1. Load `IDENTITY.md`.
2. Load `AGENTS.md`.
3. Read `README.md` the repository to understand the application, stack and target platforms.
4. Load `SOUL.md`.
5. Load `INPUT_SCHEMA.json`.
6. Read `/data/openclaw/memory/shared/SHARED_MEMORY.md` — apply global team standards as base context.
7. Read `/data/openclaw/memory/dev_mobile/MEMORY.md` — retrieve your own relevant mobile learning.
8. Validate `/data/openclaw/` and implementation workspace.
9. Detect mobile framework by task's `technology_stack` or by files (`app.json`, `expo.json`, `pubspec.yaml`).
10. Identify target platform: iOS, Android or both.
11. Load standard commands per framework (Expo/EAS or Flutter).
12. Validate tools in PATH: `node`, `npm`, `npx`, `expo`, `eas-cli` (or `flutter`, `dart`).
13. Check tools: `read`, `write`, `exec`, `git`, `sessions_send`.
14. Check presence of UX artifacts in `/data/openclaw/backlog/ux/` for screen-scoped tasks.
15. When completing the session: register up to 3 learnings in `/data/openclaw/memory/dev_mobile/MEMORY.md`.
16. Ready to receive task from the Architect.

##healthcheck
- `/data/openclaw/` accessible? ✅
- INPUT_SCHEMA.json loaded? ✅
- Mobile framework detected? ✅
- Target platform identified? ✅
- SHARED_MEMORY.md and MEMORY.md (dev_mobile) read? ✅
- `ACTIVE_GIT_REPOSITORY` defined? ✅