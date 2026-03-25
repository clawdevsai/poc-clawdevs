# clawdevs-ai (Windows only)

Fluxo para subir Kubernetes local com Minikube no Docker Desktop (Windows), expor GPU real e rodar o stack (`ollama` + `openclaw` + `control-panel`).

## Novidades (2026-03-24)

- **Makefile reorganizado** em 3 seções: Preparação de Ambiente, Deploy e Operação, Logs e Monitoramento
- **Control Panel integrado** ao fluxo principal (`make clawdevs-up` agora inclui o painel)
- **Comandos consolidados**: removidos comandos duplicados e ambíguos
- **Formatação compacta**: arquivo 43% menor e mais legível
- **Help melhorado**: `make help` agora mostra interface visual organizada
- **Suporte a build local e remoto**: configure via `PUSH_IMAGE` em `k8s/.env`

## Fluxo de spec

Antes de implementar uma mudanca, o fluxo recomendado neste repositorio e:

0. `CONSTITUTION` com principios e guardrails
1. `BRIEF` com contexto e objetivo executivo
2. `SPEC` com comportamento observavel, contratos e criterios de aceite
3. `CLARIFY` quando houver ambiguidade
4. `PLAN` tecnico e arquitetura
5. `TASK` tecnica e issues
6. `FEATURE` e `USER STORY` quando fizer sentido para o fluxo de produto
7. implementacao e validacao

Templates e artefatos:

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

O mesmo contrato vale para:
- a plataforma interna da ClawDevs AI
- os projetos e entregas feitos por ela

Em ambos os casos, a SPEC é a fonte de verdade do comportamento pretendido.
Quando houver ambiguidade, o passo correto é `clarify` antes de `plan` e `tasks`.
Use o `SDD_CHECKLIST.md` como gate de prontidao antes de mover uma entrega para a proxima etapa.
Use os templates para manter o fluxo repetivel entre plataforma interna e projetos.
Use `SDD_OPERATIONAL_PROMPTS.md` para iniciar conversas e execucoes com os agentes.
Use `SDD_FULL_CYCLE_EXAMPLE.md` como molde de referencia para novas iniciativas.
Use `shared/initiatives/internal-sdd-operationalization/` como iniciativa real pronta para execucao.

## Modo Vibe Coding

ClawDevs AI deve operar em ciclos curtos e demonstraveis:

1. definir um resultado visivel
2. escrever a spec minima
3. entregar um slice vertical funcional
4. validar com demo
5. endurecer com testes, logs e observabilidade

Regra pratica:
- se a mudanca nao cabe em uma demo curta, ela esta grande demais
- se o fluxo ficar invisivel por muito tempo, ele precisa ser fatiado
- se a solução nao for reversivel, ela precisa de mais cuidado antes de subir

## Requisitos

- Windows 11
- Docker Desktop com suporte a GPU
- Driver NVIDIA atualizado
- `minikube`, `kubectl` e `make` no PATH
- Docker Desktop rodando, com GPU exposta aos containers do driver Docker

## Makefile - Comandos Disponíveis

O Makefile está organizado em **3 seções principais**. Para ver todos os comandos:

```bash
make help
```

### SEÇÃO 1: PREPARAÇÃO DE AMBIENTE

Comandos para setup inicial e configuração do cluster:

```bash
make clawdevs-up              # Setup completo (não destrutivo)
make minikube-up              # Inicia Minikube com GPU
make minikube-context         # Configura contexto k8s
make minikube-addons          # Habilita addons necessários
make storage-enable-expansion # Habilita expansão de volumes
make preflight                # Valida k8s/.env
make manifests-validate       # Valida manifests kustomize
```

**GPU (Docker Desktop Kubernetes):**
```bash
make gpu-doctor               # Diagnóstico completo GPU
make docker-k8s-check         # Valida contexto docker-desktop
make docker-k8s-context       # Muda para contexto docker-desktop
make gpu-plugin-apply         # Aplica NVIDIA device plugin
make gpu-node-check           # Verifica GPU no node
make gpu-migrate-apply        # Aplica stack com GPU
```

### SEÇÃO 2: DEPLOY E OPERAÇÃO

**Deploy Completo:**
```bash
make stack-apply              # Deploy completo (ollama+openclaw+panel)
make stack-status             # Status de todos os pods
```

**Ollama:**
```bash
make ollama-volume-apply      # Cria PVC ollama-data
make ollama-apply             # Deploy Ollama pod
make ollama-sign              # Login no Ollama
make ollama-list              # Lista modelos Ollama
```

**OpenClaw:**
```bash
make openclaw-apply           # Deploy OpenClaw
make openclaw-apply-gpu       # Deploy OpenClaw com GPU
make openclaw-restart         # Restart preservando PVC
make openclaw-dashboard       # Abre dashboard OpenClaw
```

**Control Panel:**
```bash
make panel-apply              # Deploy control panel
make panel-url                # Mostra URLs de acesso
make panel-forward            # Port-forward para localhost:3000
make panel-status             # Status dos pods
make panel-db-migrate         # Executa migrations Alembic
make panel-restart            # Restart panel pods
```

**Build de Imagens:**
```bash
make images-build             # Build todas as imagens
make images-push              # Push todas as imagens
make images-release           # Build + Push todas
make openclaw-image-release   # Build + Push OpenClaw
```

**Reset/Destrutivo:**
```bash
make reset-all                # Recria stack do zero
make destroy-all              # Limpeza completa
make clawdevs-down            # Para e remove tudo
make minikube-down            # Para Minikube
make panel-destroy            # Remove control panel
```

### SEÇÃO 3: LOGS E MONITORAMENTO

```bash
make minikube-status          # Status do Minikube
make minikube-logs            # Logs do Minikube
make ollama-logs              # Logs do Ollama
make openclaw-logs            # Logs do OpenClaw
make panel-logs-backend       # Logs do backend
make panel-logs-frontend      # Logs do frontend
```

**Templates SDD:**
```bash
make spec-template            # Template SPEC
make vibe-playbook            # Playbook vibe coding
make sdd-contract             # Contrato SDD
make constitution-template    # Constitution
make sdd-checklist            # Checklist SDD
make brief-template           # Template BRIEF
make clarify-template         # Template CLARIFY
make plan-template            # Template PLAN
make task-template            # Template TASK
make validate-template        # Template VALIDATE
```

## Ordem de execução — subindo toda a aplicação

### 1. Pré-requisitos

Copie e preencha o arquivo de segredos antes de qualquer coisa:

```bash
cp k8s/.env.example k8s/.env
# edite k8s/.env com os valores reais
```

### 2. Validar segredos e manifests

```bash
make preflight           # valida que os segredos obrigatórios estão em k8s/.env
make manifests-validate  # valida renderização do kustomize (dry-run)
```

### 3. Subir o cluster e o stack principal (OpenClaw + Ollama + Control Panel)

```bash
make clawdevs-up
```

Esse único target executa, em sequência:

| Passo | Target interno | O que faz |
|-------|---------------|-----------|
| 1 | `preflight` | Valida segredos obrigatórios em k8s/.env |
| 2 | `minikube-up` | Sobe o cluster Minikube no Docker com GPU |
| 3 | `minikube-context` | Ajusta kubeconfig e seta o contexto `clawdevs-ai` |
| 4 | `minikube-addons` | Habilita dashboard, metrics-server, storage e nvidia-device-plugin |
| 5 | `storage-enable-expansion` | Habilita expansão de volumes no storageclass |
| 6 | `ollama-volume-apply` | Cria PVC ollama-data |
| 7 | `stack-apply` | Aplica ollama + openclaw + control-panel |

### 3.1 Startup rápido (imagem pré-configurada + sem pull automático)

O `openclaw` agora usa a imagem `clawdevsai/openclaw-runtime:latest`, com `gh` e `openclaw` já instalados.
Isso remove o `apt-get`/`install.sh` do boot e reduz o tempo de subida do pod.

No `ollama`, o pull automático de modelos está desativado por padrão para evitar boot demorado.
Se quiser fazer warm-up no startup, ative no manifest:

```yaml
OLLAMA_AUTO_PULL_MODELS=true
OLLAMA_BOOT_MODELS="nemotron-3-super:cloud qwen3-next:80b-cloud"
```

### 3.2 Modo de Build de Imagens (Local vs Remote)

O projeto suporta dois modos de build de imagens, configurado via `PUSH_IMAGE` em `k8s/.env`:

**Modo Remote (padrão):**
```bash
# Em k8s/.env
PUSH_IMAGE=remote
```
- Faz pull das imagens do Docker Hub (`clawdevsai/*`)
- Mais rápido para desenvolvimento
- Requer imagens publicadas no Docker Hub

**Modo Local:**
```bash
# Em k8s/.env
PUSH_IMAGE=local
```
- Faz build das imagens localmente no contexto do Minikube
- Útil para desenvolvimento e testes
- Não requer acesso ao Docker Hub

Para publicar imagens no Docker Hub (`clawdevsAI`):

```bash
docker login -u clawdevsAI

# Publicar apenas OpenClaw
make openclaw-image-release OPENCLAW_IMAGE_TAG=latest OPENCLAW_VERSION=2026.3.22

# Publicar todas as imagens do projeto
make images-release STACK_IMAGE_TAG=latest
```

### 4. Acessar o Control Panel

O Control Panel já foi deployado pelo `make clawdevs-up`. Para acessá-lo:

```bash
make panel-url          # exibe as URLs de acesso (frontend, backend, API docs)
make panel-forward      # port-forward para http://localhost:3000
```

Para executar migrations do banco de dados:

```bash
make panel-db-migrate   # executa as migrations Alembic no backend
```

### 5. Acessar o dashboard Minikube

```bash
make dashboard          # abre o dashboard Minikube no browser
make dashboard-url      # mostra apenas a URL
```

---

O arquivo `k8s/.env` deve conter apenas valores preenchidos localmente. Antes de aplicar o stack, rode `make preflight` para validar os segredos obrigatorios.
Para manter o pod estavel e ainda ter logs úteis, use `OPENCLAW_LOG_LEVEL=info` em `k8s/.env`. Deixe `DEBUG_LOG_ENABLED=true` apenas para rastrear o bootstrap e espelhar sessoes dos agentes no log principal, porque esse modo gera muito mais ruido e pode atrapalhar o fluxo normal.

O `make minikube-up` já sobe o profile com `--gpus=all`, então o node passa a anunciar `nvidia.com/gpu` sem passo manual extra.

O deploy padrao `kubectl apply -k k8s` usa so o `base` (CPU no manifest do `ollama`). Para GPU no Ollama, use o overlay `k8s/overlays/gpu` (por exemplo `make openclaw-apply-gpu` ou `make gpu-migrate-apply` no fluxo Docker Desktop).

## Fluxo Alternativo: Docker Desktop Kubernetes

Se você quiser usar o contexto `docker-desktop` em vez do Minikube, siga este caminho:

### 1. Diagnóstico e Validação

```bash
make gpu-doctor           # Valida NVIDIA host + Docker Desktop + contextos
make docker-k8s-check     # Valida acesso ao contexto docker-desktop
```

### 2. Aplicar NVIDIA Device Plugin

```bash
make gpu-plugin-apply     # Aplica RuntimeClass + NVIDIA device plugin
make gpu-node-check       # Verifica se nvidia.com/gpu está disponível
```

Quando o `gpu-node-check` mostrar `GPU_ALLOC` diferente de `<none>`, o cluster está pronto para usar GPU.

### 3. Deploy do Stack com GPU

```bash
make gpu-migrate-apply    # Aplica stack no contexto docker-desktop com GPU
```

Este comando aplica o overlay `k8s/overlays/gpu` que inclui:
- RuntimeClass NVIDIA
- NVIDIA device plugin
- Patch do Ollama para usar GPU

**Nota:** O fluxo validado e recomendado usa Minikube com `--gpus=all`. O caminho `docker-desktop` é uma alternativa para quem prefere usar o Kubernetes integrado do Docker Desktop.

## Logs e Monitoramento

Para acompanhar os logs dos componentes:

```bash
make minikube-logs        # Logs do Minikube
make ollama-logs          # Logs do Ollama
make openclaw-logs        # Logs do OpenClaw
make panel-logs-backend   # Logs do backend do Control Panel
make panel-logs-frontend  # Logs do frontend do Control Panel
```

Para verificar status:

```bash
make minikube-status      # Status do Minikube
make stack-status         # Status de todos os pods e services
make panel-status         # Status específico do Control Panel
```

## Reset e Limpeza

Para reiniciar ou limpar o ambiente:

```bash
make reset-all            # Recria stack do zero (mantém Minikube)
make destroy-all          # Limpeza completa (remove tudo)
make clawdevs-down        # Para e remove tudo (alias para destroy-all)
make minikube-down        # Para apenas o Minikube
make panel-destroy        # Remove apenas o Control Panel
```

## Conclusão para o desenvolvedor

Resumo do caminho **mínimo** para subir a stack completa e ter **acesso fora dos pods** (NodePort no node do cluster — o mesmo mecanismo que expõe o serviço para outra máquina na LAN que alcance o IP do node).

### Ordem dos comandos (básico)

1. Copiar e preencher segredos: `cp k8s/.env.example k8s/.env` e editar.
2. (Recomendado) Validar: `make preflight` e, se quiser, `make manifests-validate`.
3. Subir tudo de uma vez: `make clawdevs-up`  
   Isso já inclui Minikube, contexto `clawdevs-ai`, addons, expansão de volume, PVC do Ollama e `stack-apply` (**Ollama + OpenClaw + Control Panel**).
4. Na **primeira** subida com banco novo do painel: `make panel-db-migrate`.
5. Conferir saúde: `make stack-status` e `make panel-status`.

### Acesso externo ao Kubernetes (UI)

Os serviços expõem **NodePort** no manifest atual. A URL típica usa o IP do node Minikube (`minikube ip`) na mesma rede que a VM/host:

| O quê | Porta NodePort | URL (substitua `MINIKUBE_IP` por `minikube ip`) |
|--------|----------------|--------------------------------------------------|
| OpenClaw gateway / **control UI** (porta do serviço `clawdevs-ai`) | 31879 | `http://MINIKUBE_IP:31879` |
| **Control Panel** — frontend | 31880 | `http://MINIKUBE_IP:31880` |
| **Control Panel** — backend (API; `/docs` para OpenAPI) | 31881 | `http://MINIKUBE_IP:31881` e `http://MINIKUBE_IP:31881/docs` |

Para listar e confirmar portas no cluster:

```bash
kubectl --context=clawdevs-ai get svc clawdevs-ai clawdevs-panel-frontend clawdevs-panel-backend
```

**Minikube Dashboard** (Kubernetes: pods, deployments, eventos — não é a UI do OpenClaw):

```bash
make dashboard
# ou só a URL:
make dashboard-url
```

### Windows + driver `docker` do Minikube

Em muitos setups o `minikube ip` **não abre no navegador da máquina host**. Nesse caso o acesso “externo” ao processo na sua máquina é via **port-forward**:

- Painel na máquina local: `make panel-forward` → [http://localhost:3000](http://localhost:3000)
- OpenClaw (control UI) na máquina local:

```bash
kubectl --context=clawdevs-ai port-forward svc/clawdevs-ai 18789:18789
```

Depois abra [http://localhost:18789](http://localhost:18789) (deixe o terminal aberto).

### Ordem mental rápida

Segredos → `make clawdevs-up` → (primeira vez) `make panel-db-migrate` → validar com `make stack-status` / `make panel-status` → acessar **control UI** (NodePort 31879 ou port-forward 18789), **control panel** (31880/31881 ou `panel-forward`), e **dashboard** do cluster com `make dashboard`.

## GitHub (gh CLI)

- A organização padrão para ações GitHub dos agentes deve vir de `GITHUB_ORG` (definido em `k8s/.env` e injetado no pod).
- Opcionalmente, `GITHUB_DEFAULT_REPOSITORY` define o primeiro repositório ativo na inicialização.
- O token deve vir de `GITHUB_TOKEN` (também definido em `k8s/.env` e injetado no pod).
- O repositório ativo por sessão fica em `/data/openclaw/contexts/active_repository.env` (`ACTIVE_GITHUB_REPOSITORY`).
- Para comandos `gh` fora de um checkout local, usar `--repo "$ACTIVE_GITHUB_REPOSITORY"` (ou `"$GITHUB_REPOSITORY"` para compatibilidade).
- Utilitários de contexto multi-repo no pod:
  - `claw-repo-discover [filtro]` para descobrir repositórios da organização
  - `claw-repo-ensure <repo> [--create]` para validar existência e criar quando autorizado
  - `claw-repo-switch <repo> [branch]` para trocar contexto de todos os agentes/workspaces
- Documentação oficial: https://cli.github.com/manual/gh

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
    searxng-deployment.yaml
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

O comando padrão de deploy continua sendo:

```bash
kubectl apply -k k8s
```

O `base` concentra o stack comum e os agentes. O overlay `gpu` adiciona `RuntimeClass`, device plugin e o patch do `ollama` para GPU; nao entra no `kubectl apply -k k8s` ate voce aplicar explicitamente esse overlay ou os targets Make que o usam. Detalhes: `docs/README.md`.


https://clawhub.ai/pskoett/self-improving-agent
