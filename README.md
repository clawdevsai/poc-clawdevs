# ClawDevs — Time de Agentes de IA em Kubernetes

> **"Qualquer um pode ter seu ClawDevs."** — Diego Silva Morais

**ClawDevs** é um enxame de **nove agentes de IA** (CEO, PO, DevOps/SRE, Architect, Developer, QA, CyberSec, UX, DBA) orquestrados em **Kubernetes** (Minikube local), com estado em **Redis Streams**, inferência local via **Ollama** e em nuvem via **Google Gemini/OpenRouter**. O time opera 24×7 na máquina do Diretor, desenvolvendo qualquer projeto em qualquer linguagem de programação.

**Criador:** Diego Silva Morais

---

## 🚀 Início rápido

```bash
# 1. Verificar se sua máquina é equivalente à de referência
./scripts/verify-machine.sh

# 2. Setup "um clique" (dependências, Minikube, Redis, Ollama, OpenClaw)
./scripts/setup.sh

# 3. Recarregar o shell
source ~/.bashrc

# 4. Aplicar manifestos Kubernetes
make apply-all

# 5. Baixar modelos Ollama
make pull-models

# 6. Ver status
make status
```

---

## 📚 Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/README.md](docs/README.md) | Documentação técnica completa |
| [docs/issues/README.md](docs/issues/README.md) | Backlog de 59 issues (12 fases) |
| [docs/00-objetivo-e-maquina-referencia.md](docs/00-objetivo-e-maquina-referencia.md) | Máquina de referência e objetivo |
| [docs/03-arquitetura.md](docs/03-arquitetura.md) | Arquitetura Redis Streams |
| [docs/05-seguranca-e-etica.md](docs/05-seguranca-e-etica.md) | Segurança Zero Trust |

---

## 🏗 Estrutura do Repositório

```
clawdevs/
├── scripts/                  # Scripts operacionais (Phase 0)
│   ├── setup.sh              # Setup "um clique" [Issue 002]
│   ├── verify-machine.sh     # Verificação de hardware [Issue 001]
│   ├── gpu_lock.py           # GPU Lock Redis TTL dinâmico [Issue 006]
│   ├── m4a_to_md.py          # Transcrição M4A → MD [Issue 009]
│   └── unblock-degradation.sh # Desbloqueio do freio de mão [Issue 017]
│
├── k8s/                      # Manifestos Kubernetes
│   ├── namespace/            # Namespace ai-agents [Issue 003]
│   ├── limits/               # ResourceQuota + LimitRange 65% [Issue 004]
│   ├── redis/                # Redis Streams (Event Bus) [Issue 005]
│   ├── ollama/               # Ollama com GPU + PVC [Issue 003]
│   ├── agents/               # Deployments dos 9 agentes [Issues 010-014]
│   └── gateway/              # RBAC, NetworkPolicy, Kill Switch [Issues 025, 027]
│
├── orchestrator/             # Orquestrador Python
│   ├── gateway/
│   │   └── gateway.py        # Token Bucket, VFM, degradação, watchdog [Issues 126, 129, 017, 124]
│   └── consumers/
│       ├── base_consumer.py  # Consumer base (Redis Streams, idempotente) [Issues 005, 007]
│       └── review_pipeline.py # Slot único de revisão (Arch+QA+Sec+DBA) [Issue 125]
│
├── security/
│   └── sandbox/
│       └── quarantine_pipeline.py # Quarentena: SAST, entropia, assinaturas [Issues 020, 028, 128]
│
├── memory/
│   └── hot/
│       └── elite_memory.py   # Memória Elite 6 camadas + WAL + curadoria [Issues 051, 052]
│
├── config/
│   └── agents/
│       └── agents-config.yaml # Manifesto de configuração dos 9 agentes [Issue 040]
│
├── soul/                     # Prompts de identidade (SOUL) dos agentes
│   ├── CEO.md               # → docs/soul/CEO.md (fonte canônica)
│   └── ...
│
├── docs/                     # Documentação técnica completa
│   ├── README.md             # Índice da documentação
│   ├── issues/README.md      # Backlog de 59 issues
│   └── soul/                 # SOUL files (fonte canônica)
│
├── Dockerfile.base           # Imagem base multi-stage [Issue 008]
├── requirements.base.txt     # Dependências Python base
├── Makefile                  # Operação do cluster
└── README.md                 # Este arquivo
```

---

## 🖥 Máquina de Referência

| Recurso | Especificação | Limite Cluster (65%) |
|---------|---------------|----------------------|
| **CPU** | AMD Ryzen 7 5800X (16 threads) | 10 CPUs |
| **GPU** | NVIDIA RTX 3060 Ti (8 GB VRAM) | ~7 GB para Ollama |
| **RAM** | 31 GB | 20 GB |
| **SSD** | NVMe 1TB | 120 GB para PVCs |

---

## 🤖 Os 9 Agentes

| Agente | Modelo | Hardware | Função Principal |
|--------|--------|----------|-----------------|
| **CEO** | Gemini 1.5 Pro | Nuvem | Estratégia, interface Diretor |
| **PO** | Gemini 1.5 Flash | Nuvem | Backlog, Issues, rascunho |
| **DevOps/SRE** | Phi-3 Mini | CPU only | IaC, CI/CD, monitoramento |
| **Architect** | Llama 3 8B | GPU | ADRs, revisão de rascunhos, code review |
| **Developer** | DeepSeek-Coder 6.7B | GPU | Implementação via OpenCode |
| **QA** | Llama 3 8B | GPU | Testes, E2E, auditor dívida técnica |
| **CyberSec** | Mistral 7B | GPU | OWASP, SAST, segurança |
| **UX** | Phi-3 Mini | CPU only | Frontend, acessibilidade |
| **DBA** | Llama 3 8B | GPU | Banco de dados, migrations |

---

## 🔐 Segurança (Zero Trust)

- **NetworkPolicy** deny-all + egress whitelist estática
- **Pipeline de Quarentena Automatizada**: SAST (semgrep) + entropia contextual + assinaturas
- **Kill Switch**: `kubectl label pod <pod> security=quarantine`
- **Sandbox efêmero** para dependências com restrições seccomp/eBPF
- **Zonas de Confiança**: publicadores confiáveis (Google, Vercel, Microsoft) sem aprovação direta

---

## 📊 Controles de Governança

| Mecanismo | Descrição |
|-----------|-----------|
| **Token Bucket CEO** | Máx. 5 eventos estratégicos/hora |
| **VFM Score** | CEO descarta eventos com ROI negativo antes do Gateway |
| **Five Strikes** | 5 tentativas → escalação na nuvem → backlog PO |
| **Freio de Mão** | Pausa esteira se >12% das tarefas em rota de fuga |
| **Cluster Acéfalo** | Retomada automática em 3 ciclos estáveis sem comando humano |
| **Aprovação por Omissão** | Apenas cosmético (CSS/UI/MD), timer 6h |
| **Disjuntor Draft** | 3 rejeições consecutivas por épico → RAG health check |

---

## 🛠 Comandos Úteis

```bash
make status          # Status completo do cluster
make logs-ceo        # Logs do CEO em tempo real
make logs-all        # Logs de todos os agentes
make test-redis      # Testa Redis
make test-ollama     # Verifica modelos disponíveis
make unblock-brake   # Desbloqueia freio de mão (somente após revisar MEMORY.md)
make quarantine POD=<pod>  # Isola pod suspeito
make dashboard       # Dashboard Kubernetes no browser
```

---

## 📋 Fases de Implementação (Issues)

| Fase | Issues | Descrição |
|------|--------|-----------|
| **0** | 001–009, 124, 125 | Fundação: máquina, setup, Minikube, Redis, Ollama, GPU |
| **1** | 010–019 | Agentes: 9 agentes, SOUL, prompts, código de conduta |
| **2** | 020–029, 126, 128 | Segurança: Zero Trust, quarentena, sandbox, SAST |
| **3** | 030–039, 127 | Operações: autonomia, five strikes, freio de mão |
| **4** | 040–049 | Configuração: perfis, FinOps, truncamento, TTL |
| **5** | 050–059 | Self-improvement: WAL, memória Elite, learnings |
| **6** | 060–069 | Habilidades transversais: escrita humanizada, docs |
| **7** | 070–089 | Ferramentas: browser, summarize, gh CLI |
| **8** | 090–099 | Skills: descoberta, criação, auto-atualização |
| **9** | 100–109 | Integrações: API Gateway, Exa Search, dados |
| **10** | 110–119 | Frontend/UX |
| **11** | 120–129 | Avançado: War Room, Chaos Engineering, balanceamento |

---

## 📄 Licença

Ver [LICENSE](LICENSE).
