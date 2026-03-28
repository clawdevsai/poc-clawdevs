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

# BOOTSTRAP.md - Dev_Mobile

1. Upload env:
   - `GIT_ORG`
   - `ACTIVE_GIT_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT` (default `/data/openclaw/backlog/implementation`)
2. Read `README.md` the repository to understand the target app, stack and platforms.
3. Validate base structure:
   - `${PROJECT_ROOT}`
   - if non-existent, use fallback `/data/openclaw/backlog/implementation` and mark context as `standby` (without throwing an error)
4. Detect framework by files:
   - `app.json` / `expo.json` → React Native + Expo
   - `pubspec.yaml` → Flutter
   - `package.json` + `react-native` → React Native bare
   - before reading build files, validate that the file exists
   - if no build file exists, do not fail; operate by `technology_stack` or wait for task
5. Identify platform: check `app.json.expo.platforms` or ADR of the task.
6. Define default commands per framework.
7. Check toolchain in PATH:
   - Expo: `node`, `npm`, `npx`, `expo`, `eas`
   - Flutter: `flutter`, `dart`
8. Configure logger with `task_id`, `framework` and `platform`.
9. Check out UX artifacts at `/data/openclaw/backlog/ux/`.
10. Enable technical research on the internet for good mobile practices.
11. Validate `gh` authentication and active repository permissions.
12. Set up scheduling:
    - fixed interval: 60 minutes (offset: :30 of each hour)
    - work source: issues GitHub label `mobile`
13. Ready.