PROFILE ?= clawdevs-ai
KUBE_CONTEXT ?= clawdevs-ai
CPUS ?= 4
MEMORY ?= 8192
K8S_VERSION ?= v1.34.1
PF_SERVICE ?= service/openclaw
PF_PORTS ?= 18789:18789


.PHONY: help minikube-up minikube-down minikube-status minikube-logs minikube-delete minikube-addons dashboard dashboard-url openclaw-apply openclaw-restart openclaw-logs ollama-apply ollama-volume-apply ollama-logs stack-apply stack-status port-forward-start port-forward-stop port-forward-status net-allow-egress net-test-openclaw reset-all

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
	@echo "  make openclaw-apply - aplica k8s sem apagar deployment/sessoes"
	@echo "  make openclaw-restart - reinicia o deployment openclaw preservando PVC e sessoes"
	@echo "  make openclaw-kustomization - aplica k8s via kustomize"
	@echo "  make openclaw-logs  - mostra logs do deployment openclaw"
	@echo "  make port-forward-start PF_SERVICE=service/openclaw PF_PORTS=18789:18789 PF_PID=.openclaw-forward.pid"
	@echo "  make port-forward-stop  PF_PID=.openclaw-forward.pid"
	@echo "  make port-forward-status PF_PORTS=18789:18789 PF_PID=.openclaw-forward.pid"
	@echo "  make net-allow-egress        - aplica policy liberando egress"
	@echo "  make net-test-openclaw       - testa internet no pod openclaw"
	@echo "  make reset-all    - reaplica openclaw e limpa sessoes/backlog para teste do zero"
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

ollama-list:
	kubectl --context=$(KUBE_CONTEXT) exec -it pod/ollama -- ollama list

net-allow-egress:
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/networkpolicy-allow-egress.yaml

net-test-openclaw:
	kubectl --context=$(KUBE_CONTEXT) exec deployment/openclaw -- bash -lc "apt-get update >/dev/null 2>&1 || true; apt-get install -y --no-install-recommends curl ca-certificates dnsutils >/dev/null 2>&1 || true; echo 'DNS:'; nslookup google.com | head -n 5; echo 'HTTPS:'; curl -I -m 10 https://google.com | head -n 1"

openclaw-apply: net-allow-egress
	kubectl --context=$(KUBE_CONTEXT) apply -k k8s

openclaw-restart:
	kubectl --context=$(KUBE_CONTEXT) rollout restart deployment/openclaw
	kubectl --context=$(KUBE_CONTEXT) rollout status deployment/openclaw --timeout=240s

openclaw-logs:
	kubectl --context=$(KUBE_CONTEXT) logs -f deployment/openclaw

openclaw-dashboard:
	kubectl --context=$(KUBE_CONTEXT) exec deployment/openclaw -- openclaw dashboard --no-open

reset-all: openclaw-apply
	kubectl --context=$(KUBE_CONTEXT) rollout status deployment/openclaw --timeout=240s
	kubectl --context=$(KUBE_CONTEXT) exec deployment/openclaw -- bash -lc "set -euo pipefail; \
		mkdir -p /data/openclaw/agents/ceo/sessions /data/openclaw/agents/po/sessions /data/openclaw/agents/architecture/sessions; \
		rm -f /data/openclaw/agents/ceo/sessions/*.jsonl /data/openclaw/agents/ceo/sessions/*.lock || true; \
		rm -f /data/openclaw/agents/po/sessions/*.jsonl /data/openclaw/agents/po/sessions/*.lock || true; \
		rm -f /data/openclaw/agents/architecture/sessions/*.jsonl /data/openclaw/agents/architecture/sessions/*.lock || true; \
		printf '{}' > /data/openclaw/agents/ceo/sessions/sessions.json; \
		printf '{}' > /data/openclaw/agents/po/sessions/sessions.json; \
		printf '{}' > /data/openclaw/agents/architecture/sessions/sessions.json; \
		rm -f /data/openclaw/backlog/*.md || true; \
		rm -f /data/openclaw/backlog/idea/* || true; \
		rm -f /data/openclaw/backlog/user_story/* || true; \
		rm -f /data/openclaw/backlog/tasks/* || true; \
		echo 'reset-all concluido'; \
		echo 'sessions:'; \
		cat /data/openclaw/agents/ceo/sessions/sessions.json; echo; \
		cat /data/openclaw/agents/po/sessions/sessions.json; echo; \
		cat /data/openclaw/agents/architecture/sessions/sessions.json; echo; \
		echo 'backlog:'; \
		ls -la /data/openclaw/backlog/idea; \
		ls -la /data/openclaw/backlog/user_story; \
		ls -la /data/openclaw/backlog/tasks"

stack-apply: ollama-apply openclaw-apply

stack-status:
	kubectl --context=$(KUBE_CONTEXT) get pods -l app=ollama
	kubectl --context=$(KUBE_CONTEXT) get pods -l app=openclaw
	kubectl --context=$(KUBE_CONTEXT) get svc ollama openclaw

port-forward-start:
	kubectl --context=$(KUBE_CONTEXT) port-forward $(PF_SERVICE) $(PF_PORTS)

port-forward-stop:
	@echo "Sem PID/daemon. Use Ctrl+C na sessao onde o port-forward esta rodando."

port-forward-status:
	@echo "Sem PID/daemon. Rode o port-forward na sessao atual para acompanhar o status."
