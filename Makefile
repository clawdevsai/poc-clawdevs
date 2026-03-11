PYTHON ?= python
MINIKUBE ?= minikube
KUBECTL ?= kubectl
DOCKER ?= docker
IMAGE ?= clawdevs-ai:latest
NAMESPACE ?= clawdevs-ai
OLLAMA_MODEL ?= qwen3-next:80b-cloud
OLLAMA_POD_SELECTOR ?= app=ollama
OPENCLAW_GATEWAY_IMAGE ?= ghcr.io/openclaw/openclaw:latest
TELEGRAM_BOT_TOKEN ?=
TELEGRAM_CHAT_ID ?=
GPU_WAIT_TIMEOUT ?= 120
MINIKUBE_WAIT ?= all
MINIKUBE_WAIT_TIMEOUT ?= 10m
MINIKUBE_GPU_REQUEST ?= all

.PHONY: help test clean check-runtime-stack preflight gpu-host-check gpu-cdi-check gpu-cdi-help minikube-start minikube-start-host gpu-wait gpu-assert gpu-debug image-build deploy deploy-host up up-gpu up-force up-cdi up-host-ollama down down-host restart status logs gpu-smoke ollama-pull telegram-enable telegram-disable telegram-logs cluster-reset cluster-reset-hard

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
	@echo "OPENCLAW_GATEWAY_IMAGE=<img> pode sobrescrever imagem do gateway"
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

deploy:
	@$(KUBECTL) apply -f k8s/stack.yaml
	@$(KUBECTL) get pods -n $(NAMESPACE)

deploy-host:
	@$(KUBECTL) delete deploy/ollama svc/ollama -n $(NAMESPACE) --ignore-not-found=true
	@$(KUBECTL) apply -f k8s/stack-host-ollama.yaml
	@$(KUBECTL) set image deployment/openclaw-gateway gateway=$(OPENCLAW_GATEWAY_IMAGE) -n $(NAMESPACE)
	@$(KUBECTL) rollout restart deployment/po-worker -n $(NAMESPACE)
	@$(KUBECTL) get pods -n $(NAMESPACE)

up: preflight gpu-host-check minikube-start-host image-build deploy-host status

up-gpu: preflight gpu-host-check minikube-start gpu-assert image-build deploy status

up-force: preflight gpu-host-check cluster-reset image-build deploy status

up-cdi:
	@$(MAKE) MINIKUBE_GPU_REQUEST=nvidia.com up-force

up-host-ollama: preflight gpu-host-check minikube-start-host image-build deploy-host status

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

logs:
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/orchestration --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/po-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/architect-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/developer-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/devops-worker --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/telegram-director --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/openclaw-gateway --tail=100
	@$(KUBECTL) logs -n $(NAMESPACE) deployment/ollama --tail=100

gpu-smoke:
	@$(KUBECTL) run gpu-smoke --rm -it --restart=Never --image=nvidia/cuda:12.3.2-base-ubuntu22.04 --limits=nvidia.com/gpu=1 -n $(NAMESPACE) -- nvidia-smi

ollama-pull:
	@$(KUBECTL) get pods -n $(NAMESPACE) -l $(OLLAMA_POD_SELECTOR)
	@$(KUBECTL) exec -n $(NAMESPACE) deployment/ollama -- ollama pull $(OLLAMA_MODEL)

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

clean:
	@cmd /c "for /d /r %d in (__pycache__) do @if exist \"%d\" rd /s /q \"%d\"" || true
	@cmd /c "if exist .pytest_cache rd /s /q .pytest_cache" || true
