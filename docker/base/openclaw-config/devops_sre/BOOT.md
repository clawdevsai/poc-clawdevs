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

# BOOT.md - DevOps_SRE

## Boot Sequence

1. Load `IDENTITY.md`.
2. Load `AGENTS.md`.
3. Read `README.md` the repository to understand the application, stack and infrastructure.
4. Load `SOUL.md`.
5. Load `INPUT_SCHEMA.json`.
6. Read `/data/openclaw/memory/shared/SHARED_MEMORY.md` — apply global team standards as base context.
7. Read `/data/openclaw/memory/devops_sre/MEMORY.md` — retrieve your own relevant infrastructure learnings.
8. Validate `/data/openclaw/` and infrastructure workspace.
9. Detect infrastructure stack: Docker Compose, Terraform, Helm, GitHub Actions workflows.
10. Check tools in PATH: `docker-compose`, `docker`, `terraform`, `helm`, `gh`, `git`.
11. Check available cloud CLI: `aws`, `gcloud`, `az`.
12. Validate variables via `/data/openclaw/contexts/active_repository.env`: `ACTIVE_GIT_REPOSITORY`.
13. Check active SLOs and alerts at `/data/openclaw/backlog/status/`.
14. When completing the session: register up to 3 learnings in `/data/openclaw/memory/devops_sre/MEMORY.md`.
15. Ready to receive tasks from the Architect or production incidents.

##healthcheck
- `/data/openclaw/` accessible? ✅
- INPUT_SCHEMA.json loaded? ✅
- Infra stack detected? ✅
- Are `docker-compose`, `gh`, `terraform` tools available? ✅ (warn if missing, don't crash)
- SHARED_MEMORY.md and MEMORY.md (devops_sre) read? ✅
- `ACTIVE_GIT_REPOSITORY` set? ✅