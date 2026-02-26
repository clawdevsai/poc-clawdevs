# [team-devs-ai] Minikube, Redis e Ollama com limite 65%

**Fase:** 0 — Fundação  
**Labels:** foundation, k8s, infra

## Descrição

Configurar o cluster Minikube (Pop!_OS) com Redis e Ollama, respeitando o limite de **65%** dos recursos da máquina de referência para manter o host estável. Arquitetura Hub & Spoke: um único pod de inferência (Ollama) acessado por todos os agentes locais.

## Critérios de aceite

- [ ] Minikube iniciado com `--driver=docker --addons=nvidia-device-plugin`, CPUs e memória equivalentes a ~65% (ex.: 10 CPUs, 20 GB RAM para máquina 16 threads / 31 GB).
- [ ] Redis implantado e acessível no cluster (Helm ou manifestos).
- [ ] Ollama implantado com acesso à GPU (`nvidia.com/gpu: 1`), volume persistente para modelos, variável `OLLAMA_KEEP_ALIVE` configurável.
- [ ] Tabela de limites documentada: CPU, RAM, VRAM e disco (cluster vs host).
- [ ] Modelos recomendados documentados (ex.: deepseek-coder:6.7b para Developer, llama3:8b para Architect/QA/CyberSec, phi3:mini para DevOps/UX).

## Referências

- [04-infraestrutura.md](../04-infraestrutura.md)
- [00-objetivo-e-maquina-referencia.md](../00-objetivo-e-maquina-referencia.md)
