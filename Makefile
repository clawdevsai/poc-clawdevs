PROFILE ?= clawdevs-ai
KUBE_CONTEXT ?= clawdevs-ai
CPUS ?= 4
MEMORY ?= 8192
K8S_VERSION ?= v1.34.1


.PHONY: help minikube-up minikube-down minikube-status minikube-logs minikube-delete minikube-addons dashboard dashboard-url openclaw-apply openclaw-logs ollama-apply ollama-volume-apply ollama-logs stack-apply stack-status openclaw-forward-start openclaw-forward-stop openclaw-forward-status net-allow-egress net-test-openclaw

help:
	@echo "Targets disponiveis (sem GPU):"
	@echo "  make minikube-up    - sobe Minikube no Docker Desktop"
	@echo "  make minikube-down  - para Minikube"
	@echo "  make minikube-addons - habilita addons do Minikube"
	@echo "  make minikube-addons-gpu - habilita addons GPU (NVIDIA) no Minikube"
	@echo "  make minikube-context - ajusta kubeconfig e seta contexto clawdevs-ai"
	@echo "  make dashboard      - abre dashboard do Minikube"
	@echo "  make dashboard-url  - mostra URL do dashboard"
	@echo "  make ollama-apply   - aplica k8s/ollama-pod.yaml (Pod + Service)"
	@echo "  make ollama-volume-apply - cria PVC ollama-data"
	@echo "  make ollama-logs    - mostra logs do pod ollama"
	@echo "  make openclaw-apply - aplica k8s via kustomize"
	@echo "  make openclaw-kustomization - aplica k8s via kustomize"
	@echo "  make openclaw-logs  - mostra logs do deployment openclaw"
	@echo "  make openclaw-forward-start  - inicia port-forward em background"
	@echo "  make openclaw-forward-stop   - para port-forward em background"
	@echo "  make openclaw-forward-status - status do port-forward"
	@echo "  make net-allow-egress        - aplica policy liberando egress"
	@echo "  make net-test-openclaw       - testa internet no pod openclaw"
	@echo "  make stack-apply    - aplica ollama + openclaw"
	@echo "  make stack-status   - status de pods e service do stack"
	@echo "  make minikube-status|minikube-logs|minikube-delete"

minikube-up:
	minikube start \
		--profile=$(PROFILE) \
		--driver=docker \
		--container-runtime=docker \
		--kubernetes-version=$(K8S_VERSION) \
		--cpus=$(CPUS) \
		--memory=$(MEMORY)

minikube-down:
	minikube stop --profile=$(PROFILE)
	minikube delete --profile=$(PROFILE)

minikube-context:
	minikube profile $(PROFILE)
	minikube update-context -p $(PROFILE)
	kubectl config use-context $(PROFILE)

minikube-addons:
	minikube addons enable dashboard -p $(PROFILE) --force --refresh
	minikube addons enable metrics-server -p $(PROFILE) --force --refresh
	minikube addons enable default-storageclass -p $(PROFILE) --force --refresh
	minikube addons enable storage-provisioner -p $(PROFILE) --force --refresh
ifneq ($(GPU),0)
	minikube addons enable nvidia-device-plugin -p $(PROFILE) --force --refresh
endif

minikube-status:
	minikube status --profile=$(PROFILE)

minikube-logs:
	minikube logs --profile=$(PROFILE)

minikube-dashboard:
	minikube dashboard -p $(PROFILE) --url

ollama-apply: ollama-volume-apply
	kubectl --context=$(KUBE_CONTEXT) delete pod ollama --ignore-not-found
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/ollama-pod.yaml

ollama-volume-apply:
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/ollama-pvc.yaml

ollama-logs:
	kubectl --context=$(KUBE_CONTEXT) logs -f pod/ollama

ollama-sign:
	kubectl --context=$(KUBE_CONTEXT) exec -it pod/ollama -- ollama signin

openclaw-apply: net-allow-egress
	kubectl --context=$(KUBE_CONTEXT) delete pod openclaw --ignore-not-found
	kubectl --context=$(KUBE_CONTEXT) delete deployment openclaw --ignore-not-found
	kubectl --context=$(KUBE_CONTEXT) apply -k k8s

openclaw-forward-start:
	powershell -NoProfile -Command "$$pidPath='.openclaw-forward.pid'; if (Test-Path $$pidPath) { try { $$oldPid=Get-Content $$pidPath; if ($$oldPid -and (Get-Process -Id $$oldPid -ErrorAction SilentlyContinue)) { Write-Host 'Port-forward ja esta rodando. PID:' $$oldPid; exit 0 } } catch {} }; $$p=Start-Process -FilePath kubectl -ArgumentList '--context=$(KUBE_CONTEXT)','port-forward','service/openclaw','18789:18789' -PassThru -WindowStyle Hidden; Set-Content -Path $$pidPath -Value $$p.Id; Write-Host 'Port-forward iniciado. PID:' $$p.Id; Write-Host 'URL: http://127.0.0.1:18789'"

openclaw-forward-stop:
	powershell -NoProfile -Command "$$pidPath='.openclaw-forward.pid'; if (!(Test-Path $$pidPath)) { Write-Host 'Sem PID file (.openclaw-forward.pid).'; exit 0 }; $$pid=Get-Content $$pidPath; if ($$pid -and (Get-Process -Id $$pid -ErrorAction SilentlyContinue)) { Stop-Process -Id $$pid -Force; Write-Host 'Port-forward parado. PID:' $$pid } else { Write-Host 'Processo nao encontrado para PID:' $$pid }; Remove-Item $$pidPath -ErrorAction SilentlyContinue"

openclaw-forward-status:
	powershell -NoProfile -Command "$$pidPath='.openclaw-forward.pid'; if (!(Test-Path $$pidPath)) { Write-Host 'Port-forward: parado'; exit 0 }; $$pid=Get-Content $$pidPath; if ($$pid -and (Get-Process -Id $$pid -ErrorAction SilentlyContinue)) { Write-Host 'Port-forward: rodando (PID' $$pid ')'; Write-Host 'URL: http://127.0.0.1:18789' } else { Write-Host 'Port-forward: parado (PID stale:' $$pid ')'; exit 1 }"

openclaw-logs:
	kubectl --context=$(KUBE_CONTEXT) logs -f deployment/openclaw

openclaw-dashboard:
	kubectl --context=$(KUBE_CONTEXT) exec deployment/openclaw -- openclaw dashboard --no-open

stack-apply: ollama-apply openclaw-apply

stack-status:
	kubectl --context=$(KUBE_CONTEXT) get pods -l app=ollama
	kubectl --context=$(KUBE_CONTEXT) get pods -l app=openclaw
	kubectl --context=$(KUBE_CONTEXT) get svc ollama openclaw

net-allow-egress:
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/networkpolicy-allow-egress.yaml

net-test-openclaw:
	kubectl --context=$(KUBE_CONTEXT) exec deployment/openclaw -- bash -lc "apt-get update >/dev/null 2>&1 || true; apt-get install -y --no-install-recommends curl ca-certificates dnsutils >/dev/null 2>&1 || true; echo 'DNS:'; nslookup google.com | head -n 5; echo 'HTTPS:'; curl -I -m 10 https://google.com | head -n 1"
