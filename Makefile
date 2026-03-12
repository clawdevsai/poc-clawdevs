PYTHON ?= python
MINIKUBE ?= minikube
KUBECTL ?= kubectl
DOCKER ?= docker
IMAGE ?= clawdevs-ai:latest
DIRECTOR_IMAGE ?= director-console:latest
DIRECTOR_CONSOLE_DIR ?= director-console
NAMESPACE ?= clawdevs-ai
OLLAMA_MODEL ?= qwen3-next:80b-cloud
OLLAMA_POD_SELECTOR ?= app=ollama
OLLAMA_AUTO_PULL ?= 1
OLLAMA_MODELS ?= rnj-1:8b-cloud,devstral-small-2:24b-cloud,nemotron-3-nano:30b-cloud,gpt-oss:120b-cloud,qwen3-coder-next:cloud,qwen3-coder:480b-cloud,devstral-2:123b-cloud,ministral-3:14b-cloud,qwen3-next:80b-cloud,qwen3.5:397b-cloud
OPENCLAW_GATEWAY_IMAGE ?= clawdevs-ai:latest
TELEGRAM_BOT_TOKEN ?=
TELEGRAM_CHAT_ID ?=
GPU_WAIT_TIMEOUT ?= 120
MINIKUBE_WAIT ?= all
MINIKUBE_WAIT_TIMEOUT ?= 10m
MINIKUBE_GPU_REQUEST ?= all

.PHONY: help test clean check-runtime-stack preflight gpu-host-check gpu-cdi-check gpu-cdi-help minikube-start minikube-start-host gpu-wait gpu-assert gpu-debug image-build deploy deploy-host up up-gpu up-force up-cdi up-host-ollama down down-host restart status logs gpu-smoke ollama-pull ollama-pull-all ollama-signin telegram-enable telegram-disable telegram-logs env-sync gh-check gh-token-sync gh-auth-check cluster-reset cluster-reset-hard console

help:
	@echo "make test      - executa a suite"
	@echo "make check-runtime-stack - valida OpenClaw + Ollama"
	@echo "make preflight - valida ferramentas instaladas"
	@echo "make up        - sobe stack (modo host-ollama, sem exigir GPU no node)"
	@echo "make up-gpu    - sobe stack completa no Minikube com GPU (modo all)"
	@echo "make up-force  - recria profile GPU (modo all) e sobe stack completa"
	@echo "make up-cdi    - fallback usando --gpus nvidia.com (CDI)"
	@echo "make up-host-ollama - sobe stack no cluster e usa Ollama no host"
	@echo "make restart   - reinicia todos os deployments"
	@echo "make console   - abre o diretor-console bloqueando a porta 3000 local para acesso"
	@echo "make down      - remove stack do Minikube"
	@echo "make down-host - remove stack host-ollama do Minikube"
	@echo "make cluster-reset - recria profile minikube do zero"
	@echo "make cluster-reset-hard - purge total de profiles minikube + recriacao GPU"
	@echo "make status    - status dos pods no Minikube"
	@echo "make logs      - logs dos deployments principais"
	@echo "make telegram-enable TELEGRAM_BOT_TOKEN=<token> TELEGRAM_CHAT_ID=<chat_id>"
	@echo "make telegram-disable - desabilita bridge Telegram"
	@echo "make telegram-logs - logs da bridge Telegram"
	@echo "make gpu-host-check - valida GPU no Docker host (nvidia-smi)"
	@echo "make gpu-cdi-check - valida suporte CDI no Docker host"
	@echo "make gpu-cdi-help - abre checklist de setup CDI"
	@echo "make gpu-assert - falha cedo se GPU nao estiver exposta no node"
	@echo "make gpu-debug - diagnostico rapido de GPU no cluster"
	@echo "make gpu-smoke - valida GPU no cluster (nvidia-smi)"
	@echo "make ollama-pull OLLAMA_MODEL=<modelo> - baixa modelo no pod Ollama"
	@echo "make ollama-pull-all - baixa automaticamente a lista OLLAMA_MODELS no pod Ollama"
	@echo "OLLAMA_MODELS=<m1,m2,...> pode sobrescrever a lista padrao de modelos"
	@echo "make ollama-signin - gera URL de login para Ollama Cloud (necessario p/ modelos cloud)"
	@echo "make gh-check - valida gh CLI em gateway e todos os agentes"
	@echo "make env-sync - sincroniza .env -> configmap (nao sensivel) + secret (sensivel)"
	@echo "make gh-token-sync - alias para make env-sync"
	@echo "make gh-auth-check - valida autenticacao do gh CLI em todos os deployments"
	@echo "OPENCLAW_GATEWAY_IMAGE=<img> pode sobrescrever imagem do gateway"
	@echo "DIRECTOR_IMAGE=<img> pode sobrescrever imagem do director-console"
	@echo "make clean     - remove caches Python"

test:
	@$(PYTHON) -m pytest -q

check-runtime-stack:
	@$(PYTHON) -m app.runtime.check_stack

preflight:
	@where $(MINIKUBE)
	@where $(KUBECTL)
	@where $(DOCKER)
	@$(MINIKUBE) version
	@$(KUBECTL) version --client
	@$(DOCKER) --version
	@powershell -NoProfile -Command "docker info > $$null 2>&1; if ($$LASTEXITCODE -ne 0) { Write-Host 'ERRO: Docker daemon indisponivel. Inicie o Docker Desktop e tente novamente.'; exit 1 } else { Write-Host 'docker daemon: ok' }"
	@echo "preflight ok: binarios encontrados"

gpu-host-check:
	@$(DOCKER) run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi

gpu-cdi-check:
	@$(DOCKER) run --rm --device nvidia.com/gpu=all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi
	@where nvidia-ctk || echo "nvidia-ctk nao encontrado no host"

gpu-cdi-help:
	@type docs\21-gpu-cdi-windows.md

minikube-start:
	@$(MINIKUBE) start --driver=docker --container-runtime=docker --gpus $(MINIKUBE_GPU_REQUEST) --wait=$(MINIKUBE_WAIT) --wait-timeout=$(MINIKUBE_WAIT_TIMEOUT)
	@$(MINIKUBE) update-context
	@$(MINIKUBE) status
	@$(KUBECTL) wait --for=condition=Ready node/minikube --timeout=240s
	@$(MINIKUBE) addons enable storage-provisioner || $(MINIKUBE) addons enable storage-provisioner
	@$(MINIKUBE) addons enable default-storageclass || $(MINIKUBE) addons enable default-storageclass
	@$(MINIKUBE) addons enable nvidia-device-plugin
	@$(MAKE) gpu-wait

minikube-start-host:
	@$(MINIKUBE) start --driver=docker --container-runtime=docker --wait=$(MINIKUBE_WAIT) --wait-timeout=$(MINIKUBE_WAIT_TIMEOUT)
	@$(MINIKUBE) update-context
	@$(MINIKUBE) status
	@$(KUBECTL) wait --for=condition=Ready node/minikube --timeout=240s
	@$(MINIKUBE) addons enable storage-provisioner || $(MINIKUBE) addons enable storage-provisioner
	@$(MINIKUBE) addons enable default-storageclass || $(MINIKUBE) addons enable default-storageclass

gpu-wait:
	@echo "Aguardando nvidia-device-plugin ficar Ready..."
	@powershell -NoProfile -Command "$$timeout = $(GPU_WAIT_TIMEOUT); $$elapsed = 0; while ($$elapsed -lt $$timeout) { try { $$phase = & $(KUBECTL) -n kube-system get pods -l name=nvidia-device-plugin-ds -o jsonpath='{.items[0].status.phase}' 2>$$null; if ($$phase -eq 'Running') { break } } catch {} ; Start-Sleep -Seconds 5; $$elapsed += 5; Write-Host ('  aguardando plugin... ' + $$elapsed + 's/' + $$timeout + 's') }; if ($$elapsed -ge $$timeout) { Write-Host 'ERRO: timeout aguardando nvidia-device-plugin pod.'; exit 1 }; Write-Host 'nvidia-device-plugin Running. Aguardando GPU ser registrada no node...'; while ($$elapsed -lt $$timeout) { $$gpu = & $(KUBECTL) get nodes -o jsonpath='{.items[0].status.allocatable.nvidia\.com/gpu}' 2>$$null; if (-not [string]::IsNullOrWhiteSpace($$gpu) -and $$gpu -ne '<none>' -and $$gpu -ne '0') { Write-Host ('GPU registrada no node: ' + $$gpu); exit 0 }; Start-Sleep -Seconds 5; $$elapsed += 5; Write-Host ('  aguardando GPU no node... ' + $$elapsed + 's/' + $$timeout + 's') }; Write-Host 'ERRO: timeout aguardando GPU ser registrada no node.'; exit 1"

gpu-assert:
	@powershell -NoProfile -Command "$$gpu = & $(KUBECTL) get nodes -o jsonpath='{.items[0].status.allocatable.nvidia\.com/gpu}'; if ([string]::IsNullOrWhiteSpace($$gpu) -or $$gpu -eq '<none>' -or $$gpu -eq '0') { Write-Host 'ERRO: GPU nao exposta no node minikube (nvidia.com/gpu).'; Write-Host 'Rode: make gpu-debug'; exit 1 } else { Write-Host ('GPU detectada no node: ' + $$gpu) }"

gpu-debug:
	@$(KUBECTL) get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu
	@$(KUBECTL) -n kube-system get ds nvidia-device-plugin-daemonset
	@$(KUBECTL) -n kube-system get pods -l name=nvidia-device-plugin-ds
	@$(KUBECTL) -n kube-system logs daemonset/nvidia-device-plugin-daemonset --tail=120
	@$(KUBECTL) describe node minikube

image-build:
	@$(MINIKUBE) image build -t $(IMAGE) .
	@$(MINIKUBE) image build -t $(DIRECTOR_IMAGE) $(DIRECTOR_CONSOLE_DIR)

deploy:
	@$(KUBECTL) apply -f k8s/stack.yaml
	@$(KUBECTL) set image deployment/director-console director-console=$(DIRECTOR_IMAGE) -n $(NAMESPACE)
	@$(MAKE) env-sync
	@powershell -NoProfile -Command "if ('$(OLLAMA_AUTO_PULL)' -eq '1') { & $(MAKE) ollama-pull-all } else { Write-Host 'OLLAMA_AUTO_PULL=0, pulando bootstrap de modelos' }"
	@$(KUBECTL) get pods -n $(NAMESPACE)

deploy-host:
	@$(KUBECTL) delete deploy/ollama svc/ollama -n $(NAMESPACE) --ignore-not-found=true
	@$(KUBECTL) apply -f k8s/stack-host-ollama.yaml
	@$(KUBECTL) set image deployment/director-console director-console=$(DIRECTOR_IMAGE) -n $(NAMESPACE)
	@$(MAKE) env-sync
	@powershell -NoProfile -Command "if ('$(OLLAMA_AUTO_PULL)' -eq '1') { & $(MAKE) ollama-pull-all } else { Write-Host 'OLLAMA_AUTO_PULL=0, pulando bootstrap de modelos' }"
	@$(KUBECTL) set image deployment/openclaw-gateway gateway=$(OPENCLAW_GATEWAY_IMAGE) -n $(NAMESPACE)
	@$(KUBECTL) rollout restart deployment/po-worker -n $(NAMESPACE)
	@$(KUBECTL) get pods -n $(NAMESPACE)

up: preflight gpu-host-check minikube-start-host image-build deploy-host status console

up-gpu: preflight gpu-host-check minikube-start gpu-assert image-build deploy status console

up-force: preflight gpu-host-check cluster-reset image-build deploy status console

up-cdi:
	@$(MAKE) MINIKUBE_GPU_REQUEST=nvidia.com up-force

up-host-ollama: preflight gpu-host-check minikube-start-host image-build deploy-host status console

down:
	@$(KUBECTL) delete -f k8s/stack.yaml --ignore-not-found=true

down-host:
	@$(KUBECTL) delete -f k8s/stack-host-ollama.yaml --ignore-not-found=true

cluster-reset:
	@$(MINIKUBE) delete -p minikube
	@$(MINIKUBE) start --driver=docker --container-runtime=docker --gpus $(MINIKUBE_GPU_REQUEST) --wait=$(MINIKUBE_WAIT) --wait-timeout=$(MINIKUBE_WAIT_TIMEOUT)
	@$(MINIKUBE) update-context
	@$(MINIKUBE) addons enable storage-provisioner
	@$(MINIKUBE) addons enable default-storageclass
	@$(MINIKUBE) addons enable nvidia-device-plugin
	@$(KUBECTL) wait --for=condition=Ready node/minikube --timeout=240s
	@$(MAKE) gpu-wait
	@$(MAKE) gpu-assert

cluster-reset-hard:
	@$(MINIKUBE) delete --all --purge
	@$(MINIKUBE) start --driver=docker --container-runtime=docker --gpus $(MINIKUBE_GPU_REQUEST) --wait=$(MINIKUBE_WAIT) --wait-timeout=$(MINIKUBE_WAIT_TIMEOUT)
	@$(MINIKUBE) update-context
	@$(MINIKUBE) addons enable storage-provisioner
	@$(MINIKUBE) addons enable default-storageclass
	@$(MINIKUBE) addons enable nvidia-device-plugin
	@$(KUBECTL) wait --for=condition=Ready node/minikube --timeout=240s
	@$(MAKE) gpu-wait
	@$(MAKE) gpu-assert

restart:
	@$(KUBECTL) rollout restart deployment -n $(NAMESPACE)
	@$(KUBECTL) get pods -n $(NAMESPACE)

status:
	@$(KUBECTL) get pods -n $(NAMESPACE)
	@$(KUBECTL) get svc -n $(NAMESPACE)
	@$(KUBECTL) get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu

console:
	@echo ">>> Abrindo Director Console na porta :3000 no background..."
	@powershell -NoProfile -Command "Start-Process -WindowStyle Hidden $(KUBECTL) -ArgumentList 'port-forward','svc/director-console','3000:3000','-n','$(NAMESPACE)'"

logs:
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/orchestration --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/po-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/architect-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/developer-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/qa-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/dba-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/cybersec-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/architect-review-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/devops-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/telegram-director --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/openclaw-gateway --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/ollama --tail=100

gpu-smoke:
	@$(KUBECTL) run gpu-smoke --rm -it --restart=Never --image=nvidia/cuda:12.3.2-base-ubuntu22.04 --limits=nvidia.com/gpu=1 -n $(NAMESPACE) -- nvidia-smi

ollama-pull:
	@$(KUBECTL) get pods -n $(NAMESPACE) -l $(OLLAMA_POD_SELECTOR)
	@$(KUBECTL) exec -n $(NAMESPACE) deployment/ollama -- ollama pull $(OLLAMA_MODEL)

ollama-pull-all:
	@powershell -NoProfile -Command "$$models = @(); foreach ($$item in '$(OLLAMA_MODELS)'.Split(',')) { $$m = $$item.Trim(); if (-not [string]::IsNullOrWhiteSpace($$m)) { $$models += $$m } }; if (-not $$models -or $$models.Count -eq 0) { Write-Host 'ERRO: OLLAMA_MODELS vazio.'; exit 1 }; & $(KUBECTL) -n $(NAMESPACE) rollout status deployment/ollama --timeout=300s; if ($$LASTEXITCODE -ne 0) { exit $$LASTEXITCODE }; foreach ($$m in $$models) { Write-Host ('[ollama] pulling ' + $$m); & $(KUBECTL) -n $(NAMESPACE) exec deployment/ollama -- ollama pull $$m; if ($$LASTEXITCODE -ne 0) { Write-Host ('ERRO no pull: ' + $$m); exit $$LASTEXITCODE } }; Write-Host '[ollama] modelos instalados:'; & $(KUBECTL) -n $(NAMESPACE) exec deployment/ollama -- ollama list"

ollama-signin:
	@$(KUBECTL) -n $(NAMESPACE) exec -it deployment/ollama -- ollama signin

telegram-enable:
	@powershell -NoProfile -Command "if ([string]::IsNullOrWhiteSpace('$(TELEGRAM_BOT_TOKEN)')) { Write-Host 'ERRO: informe TELEGRAM_BOT_TOKEN'; exit 1 }"
	@$(KUBECTL) set env deployment/telegram-director -n $(NAMESPACE) TELEGRAM_BOT_TOKEN="$(TELEGRAM_BOT_TOKEN)" TELEGRAM_CHAT_ID="$(TELEGRAM_CHAT_ID)"
	@$(KUBECTL) rollout restart deployment/telegram-director -n $(NAMESPACE)
	@$(KUBECTL) rollout status deployment/telegram-director -n $(NAMESPACE) --timeout=180s

telegram-disable:
	@$(KUBECTL) set env deployment/telegram-director -n $(NAMESPACE) TELEGRAM_BOT_TOKEN="" TELEGRAM_CHAT_ID=""
	@$(KUBECTL) rollout restart deployment/telegram-director -n $(NAMESPACE)
	@$(KUBECTL) rollout status deployment/telegram-director -n $(NAMESPACE) --timeout=180s

telegram-logs:
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/telegram-director --tail=200 -f

gh-check:
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/openclaw-gateway -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/orchestration -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/po-worker -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/architect-worker -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/developer-worker -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/qa-worker -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/dba-worker -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/cybersec-worker -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/architect-review-worker -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/devops-worker -- gh --version
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/telegram-director -- gh --version

env-sync:
	@powershell -NoProfile -Command "$$envPath='.env'; if (-not (Test-Path $$envPath)) { Write-Host 'ERRO: arquivo .env nao encontrado.'; exit 1 }; $$all=Get-Content $$envPath; $$secretPatterns='^(GITHUB_TOKEN|TELEGRAM_BOT_TOKEN|OPENCLAW_GATEWAY_TOKEN|REDIS_PASSWORD|OLLAMA_API_KEY)='; $$secret=$$all | Where-Object { $$_ -match $$secretPatterns }; $$config=$$all | Where-Object { $$_ -notmatch $$secretPatterns }; Set-Content -Path '.env.configmap.tmp' -Value $$config -Encoding Ascii; Set-Content -Path '.env.secret.tmp' -Value $$secret -Encoding Ascii"
	@$(KUBECTL) -n $(NAMESPACE) create configmap clawdevs-config --from-env-file=.env.configmap.tmp --dry-run=client -o yaml | $(KUBECTL) apply -f -
	@$(KUBECTL) -n $(NAMESPACE) create secret generic clawdevs-secrets --from-env-file=.env.secret.tmp --dry-run=client -o yaml | $(KUBECTL) apply -f -
	@powershell -NoProfile -Command "Remove-Item '.env.configmap.tmp','.env.secret.tmp' -Force -ErrorAction SilentlyContinue"
	@$(KUBECTL) -n $(NAMESPACE) rollout restart deployment
	@$(KUBECTL) -n $(NAMESPACE) get pods

gh-token-sync: env-sync

gh-auth-check:
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/openclaw-gateway -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/orchestration -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/po-worker -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/architect-worker -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/developer-worker -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/qa-worker -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/dba-worker -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/cybersec-worker -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/architect-review-worker -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/devops-worker -- sh -lc "gh api user --jq .login"
	@$(KUBECTL) -n $(NAMESPACE) exec deployment/telegram-director -- sh -lc "gh api user --jq .login"

clean:
	@cmd /c "for /d /r %d in (__pycache__) do @if exist \"%d\" rd /s /q \"%d\"" || true
	@cmd /c "if exist .pytest_cache rd /s /q .pytest_cache" || true
