PROFILE ?= clawdevs-ai
CPUS ?= 4
MEMORY ?= 8192
K8S_VERSION ?= v1.35.1

.PHONY: help minikube-up minikube-status minikube-logs minikube-delete dashboard dashboard-url openclaw-apply openclaw-logs ollama-apply ollama-logs stack-apply stack-status openclaw-forward-start openclaw-forward-stop openclaw-forward-status

help:
	@echo "Targets disponiveis (sem GPU):"
	@echo "  make minikube-up    - sobe Minikube no Docker Desktop"
	@echo "  make dashboard      - abre dashboard do Minikube"
	@echo "  make dashboard-url  - mostra URL do dashboard"
	@echo "  make ollama-apply   - aplica k8s/ollama-pod.yaml (Pod + Service)"
	@echo "  make ollama-logs    - mostra logs do pod ollama"
	@echo "  make openclaw-apply - aplica k8s/openclaw-pod.yaml"
	@echo "  make openclaw-logs  - mostra logs do pod openclaw"
	@echo "  make openclaw-forward-start  - inicia port-forward em background"
	@echo "  make openclaw-forward-stop   - para port-forward em background"
	@echo "  make openclaw-forward-status - status do port-forward"
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

minikube-status:
	minikube status --profile=$(PROFILE)

minikube-logs:
	minikube logs --profile=$(PROFILE)

minikube-delete:
	minikube delete --profile=$(PROFILE)

dashboard:
	minikube dashboard -p $(PROFILE)

dashboard-url:
	minikube dashboard -p $(PROFILE) --url

ollama-apply:
	kubectl --context=$(PROFILE) delete pod ollama --ignore-not-found
	kubectl --context=$(PROFILE) apply -f k8s/ollama-pod.yaml

ollama-logs:
	kubectl --context=$(PROFILE) logs -f pod/ollama

ollama-sign:
	kubectl exec -it pod/ollama -- ollama signin

openclaw-apply:
	kubectl --context=$(PROFILE) delete pod openclaw --ignore-not-found
	kubectl --context=$(PROFILE) apply -f k8s/openclaw-pod.yaml

openclaw-forward:
	kubectl port-forward pod/openclaw 18789:18789

openclaw-logs:
	kubectl --context=$(PROFILE) logs -f pod/openclaw

openclaw-dashboard:
	kubectl exec pod/openclaw -- openclaw dashboard --no-open

stack-apply: ollama-apply openclaw-apply

stack-status:
	kubectl --context=$(PROFILE) get pod ollama openclaw
	kubectl --context=$(PROFILE) get svc ollama

openclaw-forward-start:
	powershell -NoProfile -Command "$$pidPath='.openclaw-forward.pid'; if (Test-Path $$pidPath) { try { $$oldPid=Get-Content $$pidPath; if ($$oldPid -and (Get-Process -Id $$oldPid -ErrorAction SilentlyContinue)) { Write-Host 'Port-forward ja esta rodando. PID:' $$oldPid; exit 0 } } catch {} }; $$p=Start-Process -FilePath kubectl -ArgumentList 'port-forward','pod/openclaw','18789:18789' -PassThru -WindowStyle Hidden; Set-Content -Path $$pidPath -Value $$p.Id; Write-Host 'Port-forward iniciado. PID:' $$p.Id; Write-Host 'URL: http://127.0.0.1:18789'"

openclaw-forward-stop:
	powershell -NoProfile -Command "$$pidPath='.openclaw-forward.pid'; if (!(Test-Path $$pidPath)) { Write-Host 'Sem PID file (.openclaw-forward.pid).'; exit 0 }; $$pid=Get-Content $$pidPath; if ($$pid -and (Get-Process -Id $$pid -ErrorAction SilentlyContinue)) { Stop-Process -Id $$pid -Force; Write-Host 'Port-forward parado. PID:' $$pid } else { Write-Host 'Processo nao encontrado para PID:' $$pid }; Remove-Item $$pidPath -ErrorAction SilentlyContinue"

openclaw-forward-status:
	powershell -NoProfile -Command "$$pidPath='.openclaw-forward.pid'; if (!(Test-Path $$pidPath)) { Write-Host 'Port-forward: parado'; exit 0 }; $$pid=Get-Content $$pidPath; if ($$pid -and (Get-Process -Id $$pid -ErrorAction SilentlyContinue)) { Write-Host 'Port-forward: rodando (PID' $$pid ')'; Write-Host 'URL: http://127.0.0.1:18789' } else { Write-Host 'Port-forward: parado (PID stale:' $$pid ')'; exit 1 }"
