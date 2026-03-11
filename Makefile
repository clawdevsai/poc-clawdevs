PYTHON ?= python
MINIKUBE ?= minikube
KUBECTL ?= kubectl
IMAGE ?= clawdevs-ai:latest
NAMESPACE ?= clawdevs-ai

.PHONY: help test clean up down status check-runtime-stack gpu-smoke

help:
	@echo "make test      - executa a suite"
	@echo "make check-runtime-stack - valida OpenClaw + Ollama"
	@echo "make up        - sobe stack no Minikube com GPU"
	@echo "make down      - remove stack do Minikube"
	@echo "make status    - status dos pods no Minikube"
	@echo "make gpu-smoke - valida GPU no cluster (nvidia-smi)"
	@echo "make clean     - remove caches Python"

test:
	@$(PYTHON) -m pytest -q

check-runtime-stack:
	@$(PYTHON) -m app.runtime.check_stack

up:
	@$(MINIKUBE) start --driver=docker --gpus all
	@$(MINIKUBE) addons enable nvidia-device-plugin
	@$(MINIKUBE) image build -t $(IMAGE) .
	@$(KUBECTL) apply -f k8s/stack.yaml
	@$(KUBECTL) get pods -n $(NAMESPACE)

down:
	@$(KUBECTL) delete -f k8s/stack.yaml --ignore-not-found=true

status:
	@$(KUBECTL) get pods -n $(NAMESPACE)
	@$(KUBECTL) get svc -n $(NAMESPACE)
	@$(KUBECTL) get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu

gpu-smoke:
	@$(KUBECTL) run gpu-smoke --rm -it --restart=Never --image=nvidia/cuda:12.3.2-base-ubuntu22.04 --limits=nvidia.com/gpu=1 -n $(NAMESPACE) -- nvidia-smi

clean:
	@cmd /c "for /d /r %d in (__pycache__) do @if exist \"%d\" rd /s /q \"%d\"" || true
	@cmd /c "if exist .pytest_cache rd /s /q .pytest_cache" || true
