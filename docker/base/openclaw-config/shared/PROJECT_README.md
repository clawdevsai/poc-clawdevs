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

# PROJECT README

Mirror of the repository README for agent boot context.

## Project

`clawdevs-ai` and the ClawDevs AI platform repository to upload local Docker Compose with Docker on Docker Desktop, expose real GPU and run the `ollama` + `openclaw` stack.

## Spec flow

Before implementing a change, the recommended flow is:

0. `CONSTITUTION` with principles and guardrails
1. `BRIEF` with context and executive objective
2. `SPEC` with observable behavior, contracts and acceptance criteria
3. `CLARIFY` when there is ambiguity
4. `PLAN` technical and architecture
5. `TASK` techniques and issues
6. `FEATURE` and `USER STORY` when it makes sense for the product flow
7. implementation and validation

## Templates and artifacts

- `docker/base/openclaw-config/shared/BRIEF_TEMPLATE.md`
- `docker/base/openclaw-config/shared/CLARIFY_TEMPLATE.md`
- `docker/base/openclaw-config/shared/PLAN_TEMPLATE.md`
- `docker/base/openclaw-config/shared/TASK_TEMPLATE.md`
- `docker/base/openclaw-config/shared/VALIDATE_TEMPLATE.md`
- `docker/base/openclaw-config/shared/SDD_OPERATIONAL_PROMPTS.md`
- `docker/base/openclaw-config/shared/SPEC_TEMPLATE.md`
- `docker/base/openclaw-config/shared/CONSTITUTION.md`
- `docker/base/openclaw-config/shared/SDD_CHECKLIST.md`
- `docker/base/openclaw-config/shared/SDD_FULL_CYCLE_EXAMPLE.md`
- `docker/base/openclaw-config/shared/SPECKIT_ADAPTATION.md`
- `docker/base/openclaw-config/shared/initiatives/internal-sdd-operationalization/`
- `/data/openclaw/backlog/specs/`
- `/data/openclaw/backlog/briefs/`
- `/data/openclaw/backlog/user_story/`
- `/data/openclaw/backlog/tasks/`

## Main rules

- SPEC is the source of truth for intended behavior.
- The same contract applies to the internal platform and to delivered projects.
- When there is ambiguity, use `clarify` before `plan` and `tasks`.
- Use `SDD_CHECKLIST.md` as a standby gate.
- Use `SDD_OPERATIONAL_PROMPTS.md` to start conversations and executions with agents.
- Use `SDD_FULL_CYCLE_EXAMPLE.md` as a reference template.

## Vibe Coding

ClawDevs AI must operate in short, demonstrable cycles:

1. define a visible result
2. write the minimum spec
3. deliver a functional vertical slice
4. validate with demo
5. harden with tests, logs and observability

## Requirements

- Windows 11
- Docker Desktop with GPU support
- NVIDIA driver updated
- `docker`, `docker-compose` and `make` in PATH
- Docker Desktop running, with GPU exposed to containers

## Main commands

```bash
make preflight
make manifests-validate
make clawdevs-up
```

## GitHub

- The default organization for agents' GitHub shares comes from `GIT_ORG`.
- Optionally, `GIT_DEFAULT_REPOSITORY` defines the first active repository in bootstrap.
- The token comes from `GIT_TOKEN`.
- The active session repository is at `/data/openclaw/contexts/active_repository.env` (`ACTIVE_GIT_REPOSITORY`).
- For `gh` commands outside of local checkout, use `--repo "$ACTIVE_GIT_REPOSITORY"` (or `"$GIT_REPOSITORY"` for compatibility).

## container Structure

```text
container/
  .env
  .env.example
  kustomization.yaml
  base/
    kustomization.yaml
    openclaw-container.yaml
    ollama-container.yaml
    ollama-pvc.yaml
    networkpolicy-allow-egress.yaml
    openclaw-config/
      ceo/
      po/
      arquiteto/
      dev_backend/
  overlays/
    gpu/
      kustomization.yaml
      ollama-gpu-patch.yaml
      nvidia-device-plugin.yaml
      nvidia-runtimeclass.yaml
```

The default deploy command continues to be:

```bash
docker-compose apply -k container
```