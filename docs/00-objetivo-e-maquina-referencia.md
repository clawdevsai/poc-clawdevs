# Objetivo e máquina de referência

**ClawDevs** é o nome do ecossistema: **enxame de agentes de desenvolvimento de software autônomos** (nove agentes de IA) na máquina do Diretor, prontos 24 por 7. O projeto foi criado por **Diego Silva Morais**, dono e desenvolvedor do **ClawDevs**.

**Objetivo principal:** **Qualquer um pode ter seu ClawDevs** — qualquer pessoa (Diretor, desenvolvedor, empreendedor) pode ter seu **ClawDevs** (time de desenvolvimento de software com agentes de IA) **na sua máquina**, **prontos para trabalhar 24 por 7**. Esta documentação e a máquina de referência existem para que o **ClawDevs** seja replicável e operável de forma segura e sustentável por quem tiver hardware equivalente.

Este documento define **o que desenvolver** (para agentes) e a **máquina de referência** em que o ambiente **ClawDevs** foi validado.

---

## Para agentes: o que desenvolver

**Objetivo:** O **ClawDevs** — time de desenvolvimento de software 100% autônomo — em que nove agentes de IA (CEO, PO, DevOps/SRE, Architect, Developer, QA, CyberSec, UX, DBA) colaboram para construir e manter software. O **escopo de desenvolvimento** é **qualquer projeto** (qualquer domínio, qualquer stack, **qualquer linguagem de programação**) na máquina do Diretor, conforme as prioridades do projeto (cibersegurança, custo, performance). O stack de execução abaixo é o **ambiente de execução** do time — não restringe a linguagem ou o tipo de projeto desenvolvido. O stack de execução é:

- **Kubernetes** (Minikube local) — orquestração dos pods dos agentes.
- **OpenClaw** — orquestrador e interface com o Diretor (voz/chat, ex.: Telegram).
- **Ollama** — inferência local (modelos no cluster, baixo custo).
- **Provedores integrados OpenClaw em nuvem** quando aprovado (Ollama cloud, OpenRouter, Qwen, Moonshot AI, OpenAI, Hugging Face — ex.: OpenRouter FreeRide para baixo custo).
- **OpenCode** — ferramenta de geração de código usada pelo Agente Developer.

O **ambiente de execução é 100% dentro do Kubernetes**: pods dos agentes, Redis, Ollama e **volumes (PVC/workspace, etc.)** ficam no cluster. O **limite do cluster é 65% do hardware** (Minikube + ResourceQuota); ver [04-infraestrutura.md](04-infraestrutura.md).

**Prioridades (não negociáveis):** (1) **Cibersegurança** — resistência a ataques cibernéticos (injeção de prompt, RCE, cadeia de suprimentos, exfiltração); segurança nunca é trocada por custo ou velocidade. (2) **Custo baixíssimo** — de API (nuvem) e de hardware (cluster em ~65% da máquina). (3) **Performance segura e altíssima** — alta produtividade na máquina do Diretor sem colapso de recursos. Toda decisão de arquitetura, provedor (Ollama vs nuvem), pipeline (truncamento, FinOps), operação (GPU Lock, balanceamento) e **controles de segurança** deve ser avaliada sob esses critérios. O cluster usa cerca de 65% do hardware; o restante fica para o SO e uso diário. Controles de segurança são desenhados para **não** consumir hardware extra desnecessário: validações determinísticas em CPU, análise estática em hooks, egress por whitelist estática, rotação de tokens — ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

**Replicabilidade:** **Qualquer um** com **máquina igual à de referência** (ou melhor) pode montar o **ClawDevs** na sua máquina e ter seu **ClawDevs** 24 por 7. As especificações e os comandos para verificar a máquina estão na seção [Máquina de referência](#máquina-de-referência) abaixo e em [04-infraestrutura.md](04-infraestrutura.md).

---

## Máquina de referência

Specs verificadas por comando no ambiente em que esta documentação foi validada. Quem tiver CPU, GPU, RAM e disco **equivalentes ou melhores** pode seguir esta doc para replicar o time.

| Recurso | Valor (verificado) |
|---------|--------------------|
| **CPU** | AMD Ryzen 7 5800X, 8 cores, 16 threads (x86_64) |
| **GPU** | NVIDIA GeForce RTX 3060 Ti, 8 GB VRAM, CUDA 13.0, Driver 580.119.02 |
| **RAM** | 31 GB total (~20 GB disponível em uso normal) |
| **SSD** | Netac NVMe 1TB (931,5G); partição raiz 402G (169G usados, 214G livres) |

### Comandos para verificar sua máquina

Execute estes comandos (somente leitura) para conferir se sua máquina é equivalente:

- **CPU:** `lscpu` (modelo em "Nome do modelo", threads em "CPU(s)")
- **GPU:** `nvidia-smi` (modelo, VRAM, driver)
- **RAM:** `free -h` (total na primeira linha, coluna "total")
- **Disco:** `lsblk -d -o NAME,SIZE,ROTA,MODEL` e `df -h /` (partição raiz e espaço)

Para um resumo automatizado, use o script [scripts/verify-machine.sh](scripts/verify-machine.sh) ou consulte [scripts/verify-machine.md](scripts/verify-machine.md) (comandos manuais e documentação). Ver [09-setup-e-scripts.md](09-setup-e-scripts.md) para o setup completo e [04-infraestrutura.md](04-infraestrutura.md) para limites de recursos (65% da máquina de referência).
