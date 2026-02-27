# Validação Fase 0 — 001, 003, 008

Resumo da validação dos itens **001** (máquina de referência), **003** (Minikube/Redis/Ollama 65%) e **008** (Docker enxuto) antes de considerar a Fase 0 concluída.

## 001 — Máquina de referência e verificação

- **Script de verificação:** [docs/scripts/verify-machine.sh](../scripts/verify-machine.sh) e [docs/scripts/verify-machine.md](../scripts/verify-machine.md).
- **Uso:** A partir da raiz do repositório: `./docs/scripts/verify-machine.sh`. Exibe CPU, GPU, RAM e disco (somente leitura); valores 65% para Minikube estão em [verify-machine.md](../scripts/verify-machine.md) (seção "Quest 65%"). (Caminho do script: `docs/scripts/verify-machine.sh`.)
- **Referências:** [00-objetivo-e-maquina-referencia.md](../00-objetivo-e-maquina-referencia.md), [04-infraestrutura.md](../04-infraestrutura.md), [09-setup-e-scripts.md](../09-setup-e-scripts.md).
- **Status:** Coberto. Makefile `make verify` pode invocar os scripts em docs/scripts.

## 003 — Minikube, Redis e Ollama com limite 65%

- **Tabela de limites (65%):** [04-infraestrutura.md](../04-infraestrutura.md) — tabela "Limites de recursos (65% da máquina)" com CPU, RAM, VRAM e SSD (cluster vs host).
- **Modelos recomendados:** Mesmo documento — "Modelos recomendados (quantizados 4-bit)": Developer `deepseek-coder:6.7b`, Architect/QA/CyberSec `llama3:8b` ou `mistral:7b`, UX/DevOps `phi3:mini` (CPU).
- **Deploy:** Minikube com `--cpus=10 --memory=20g` (e opcionalmente `MINIKUBE_CPUS`/`MINIKUBE_MEMORY`), Redis e Ollama via `make up` e [scripts/setup.sh](../../scripts/setup.sh).
- **Status:** Coberto. Issue [003-minikube-redis-ollama-65.md](003-minikube-redis-ollama-65.md) atendida pela doc 04 e pelo Makefile/setup.

## 008 — Docker multi-stage e imagens enxutas

- **Gateway OpenClaw (Fase 0):** [k8s/management-team/openclaw/Dockerfile](../../k8s/management-team/openclaw/Dockerfile) usa base `node:22-bookworm-slim`, instala apenas `curl`, `git` e `openclaw@latest`, limpa apt lists — imagem enxuta.
- **Multi-stage por agente:** A issue 008 pede multi-stage com estágio builder e runtime ~300 MB **por agente**. Na Fase 0 há um único gateway (OpenClaw); pods por agente (Fase 1) usarão Dockerfiles multi-stage quando cada agente tiver sua própria imagem.
- **Status:** Validado para Fase 0 (imagem gateway enxuta). Multi-stage por agente fica para Fase 1 (010–019).

---

**Conclusão:** 001, 003 e 008 estão validados; gaps restantes (ex.: multi-stage por agente) estão explícitos para as fases seguintes.
