# PROJECT README

Mirror of the repository README for agent boot context.

## Projeto

`clawdevs-ai` e o repositorio da plataforma ClawDevs AI para subir Kubernetes local com Minikube no Docker Desktop, expor GPU real e rodar o stack `ollama` + `openclaw`.

## Fluxo de spec

Antes de implementar uma mudanca, o fluxo recomendado e:

0. `CONSTITUTION` com principios e guardrails
1. `BRIEF` com contexto e objetivo executivo
2. `SPEC` com comportamento observavel, contratos e criterios de aceite
3. `CLARIFY` quando houver ambiguidade
4. `PLAN` tecnico e arquitetura
5. `TASK` tecnica e issues
6. `FEATURE` e `USER STORY` quando fizer sentido para o fluxo de produto
7. implementacao e validacao

## Templates e artefatos

- `k8s/base/openclaw-config/shared/BRIEF_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/CLARIFY_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/PLAN_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/TASK_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/VALIDATE_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/SDD_OPERATIONAL_PROMPTS.md`
- `k8s/base/openclaw-config/shared/SPEC_TEMPLATE.md`
- `k8s/base/openclaw-config/shared/CONSTITUTION.md`
- `k8s/base/openclaw-config/shared/SDD_CHECKLIST.md`
- `k8s/base/openclaw-config/shared/SDD_FULL_CYCLE_EXAMPLE.md`
- `k8s/base/openclaw-config/shared/SPECKIT_ADAPTATION.md`
- `k8s/base/openclaw-config/shared/initiatives/internal-sdd-operationalization/`
- `/data/openclaw/backlog/specs/`
- `/data/openclaw/backlog/briefs/`
- `/data/openclaw/backlog/user_story/`
- `/data/openclaw/backlog/tasks/`

## Regras principais

- A SPEC e a fonte de verdade do comportamento pretendido.
- O mesmo contrato vale para a plataforma interna e para projetos entregues.
- Quando houver ambiguidade, use `clarify` antes de `plan` e `tasks`.
- Use o `SDD_CHECKLIST.md` como gate de prontidao.
- Use `SDD_OPERATIONAL_PROMPTS.md` para iniciar conversas e execucoes com os agentes.
- Use `SDD_FULL_CYCLE_EXAMPLE.md` como molde de referencia.

## Vibe Coding

ClawDevs AI deve operar em ciclos curtos e demonstraveis:

1. definir um resultado visivel
2. escrever a spec minima
3. entregar um slice vertical funcional
4. validar com demo
5. endurecer com testes, logs e observabilidade

## Requisitos

- Windows 11
- Docker Desktop com suporte a GPU
- Driver NVIDIA atualizado
- `minikube`, `kubectl` e `make` no PATH
- Docker Desktop rodando, com GPU exposta aos containers

## Comandos principais

```bash
make preflight
make manifests-validate
make clawdevs-up
```

## GitHub

- A organização padrão para ações GitHub dos agentes vem de `GITHUB_ORG`.
- Opcionalmente, `GITHUB_DEFAULT_REPOSITORY` define o primeiro repositorio ativo no bootstrap.
- O token vem de `GITHUB_TOKEN`.
- O repositorio ativo da sessao fica em `/data/openclaw/contexts/active_repository.env` (`ACTIVE_GITHUB_REPOSITORY`).
- Para comandos `gh` fora de checkout local, usar `--repo "$ACTIVE_GITHUB_REPOSITORY"` (ou `"$GITHUB_REPOSITORY"` para compatibilidade).

## Estrutura K8s

```text
k8s/
  .env
  .env.example
  kustomization.yaml
  base/
    kustomization.yaml
    openclaw-pod.yaml
    ollama-pod.yaml
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

O comando padrao de deploy continua sendo:

```bash
kubectl apply -k k8s
```
