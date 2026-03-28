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

# BOOTSTRAP.md - DevOps_SRE

1. Upload env:
   - `GIT_ORG`
   - `ACTIVE_GIT_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT` (default `/data/openclaw/backlog/implementation`)
2. Read `README.md` the repository to understand stack and infrastructure.
3. Validate base structure:
   - `${PROJECT_ROOT}`
   - if non-existent, use fallback `/data/openclaw/backlog/implementation` and mark context as `standby` (without throwing an error)
4. Detect infra stack by files:
   - `.github/workflows/` → GitHub Actions
   - `terraform/` or `infra/` → Terraform
   - `helm/` or `charts/` → Helm
   - `docker-compose.yml` → Docker Compose
   - `Dockerfile` → Docker image builds
   - before reading stack files, validate that the file/directory exists
   - if no stack file exists, do not fail; operate by `technology_stack` or wait for task
5. Detect cloud providers by environment variables or configuration files.
6. Check toolchain in PATH: `terraform`, `helm`, `docker`, `docker-compose`, `aws/gcloud/az`.
7. Configure logger with `task_id` and `infra_type`.
8. Enable technical research on the internet for good infrastructure and cloud practices.
9. Validate `gh` authentication and active repository permissions.
10. Set up scheduling:
   - fixed interval: 30 minutes
   - work source: issues GitHub label `devops` + production monitoring
11. Ready.