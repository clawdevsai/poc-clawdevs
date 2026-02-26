# Infraestrutura: Minikube, recursos e Ollama

Infraestrutura do **ClawDevs**: ambiente alvo **Pop!_OS** (System76), com drivers NVIDIA e *container toolkit* integrados. O cluster Minikube do ClawDevs usa cerca de **65%** do hardware para manter o host estável.

**Máquina de referência:** Os valores abaixo referem-se à máquina de referência documentada em [00-objetivo-e-maquina-referencia.md](00-objetivo-e-maquina-referencia.md). Use os comandos listados naquele documento (ou o script [scripts/verify-machine.sh](scripts/verify-machine.sh)) para conferir se sua máquina é equivalente.

**Aviso técnico (performance local):** A inferência local com Ollama exige **gerenciamento explícito de hardware**. Sem reservar parte da capacidade para o sistema operacional, a máquina pode travar. Recomenda-se limitar o uso de memória e CPU do cluster a aproximadamente **65%** da capacidade total, deixando o restante para o SO e aplicações do host.

**Boundary do ecossistema:** Todo o **ClawDevs** — pods, Redis, Ollama, estado e **volumes persistentes** — está **dentro do Kubernetes**. O volume de trabalho e os dados persistentes são PVCs (ou volumes equivalentes) no cluster; nada crítico do runtime fica fora do Minikube.

## Preparação do terreno (Pop!_OS + Minikube)

Garantir que o Minikube enxergue a GPU. No Pop!_OS, usar o driver Docker ou KVM.

**Comando de inicialização sugerido:**

```bash
minikube start --driver=docker --addons=nvidia-device-plugin --cpus=10 --memory=20g
```

Isso reserva aproximadamente 62,5% do Ryzen 5800X e da RAM (16 threads → 10; 31 GB → 20 GB), respeitando o limite de 65%.

## Limites de recursos (65% da máquina)

**Limite do Kubernetes:** O **limite do Kubernetes** é consumir **65% do hardware**. Esse teto é aplicado via `minikube start` (--cpus, --memory) e via ResourceQuota/LimitRange no namespace; o cluster não deve exceder 65% da capacidade da máquina.

| Recurso | Total máquina | Reservado para o cluster (Minikube) | Sobra para o host (Pop!_OS) |
|---------|----------------|-------------------------------------|-----------------------------|
| **CPU (threads)** | 16 | 10 | 6 |
| **RAM** | 31 GB | 20 GB | 11 GB |
| **VRAM (GPU)** | 8 GB | ~7 GB (Ollama dinâmico) | 1 GB |
| **SSD (NVMe)** | Partição raiz 402G (máq. ref.: NVMe 1TB) | 120 GB (PVC/partição) | Restante para SO |

## Arquitetura Hub & Spoke (modelos locais)

Com 8 GB de VRAM, rodar um modelo por agente simultaneamente é inviável. Solução: **um único Pod central de inferência (Ollama)** dentro do Minikube.

- Todos os agentes locais (Dev, QA, Architect, etc.) enviam requisições via API interna para esse serviço.
- O Ollama gerencia a fila e carrega o modelo necessário (com **GPU Lock** para apenas um uso por vez).

**Estratégia de uso de hardware:** Maximizar GPU e CPU dentro do limite de 65%; pipeline explícito ou **slot único de revisão** (um job adquire o lock uma vez e executa Architect + QA + CyberSec + DBA em sequência com o mesmo modelo). Configurar **OLLAMA_KEEP_ALIVE** e **agrupamento por modelo** para evitar trocas desnecessárias na VRAM. Ver [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md).

**Modelos recomendados (quantizados 4-bit):**

- **Developer:** `deepseek-coder:6.7b`
- **Architect / QA / CyberSec:** `llama3:8b` ou `mistral:7b`
- **UX / DevOps:** `phi3:mini` (leve; **obrigatório em CPU** — ver node selectors abaixo)

## Alocação de recursos por agente (estimativa)

| Agente | Tipo de modelo sugerido | Recurso principal |
|--------|-------------------------|-------------------|
| **CEO / PO** | GPT-4o ou Claude 3.5 / Gemini (API via OpenClaw) | Internet / baixa CPU |
| **Developer** | DeepSeek-Coder-V2 / Qwen2.5-Coder (local) | GPU (RTX 3060 Ti) |
| **Architect / QA** | Llama-3-8B (local) | GPU / RAM |
| **DevOps / CyberSec** | Modelos SLM (Phi-3 ou Gemma 2B) | CPU (Ryzen 5800X) |
| **Estágio pré-GPU** | SLM (Phi-3 Mini, FI-Tree) para sintaxe/lint/SOLID | CPU (antes da fila do lock); batching de PRs reduz chamadas à GPU |

## Resource Quota e LimitRange (Kubernetes)

Garantir que o namespace do enxame respeite o **limite do Kubernetes de 65% do hardware** (não ultrapasse esse teto) e que cada container tenha limites padrão.

**Exemplo `limits.yaml`** (inclui node selectors para reservar GPU aos agentes técnicos):

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: limite-65-por-cento
  namespace: ai-agents
spec:
  hard:
    requests.cpu: "8"
    limits.cpu: "10"
    requests.memory: 16Gi
    limits.memory: 20Gi
    pods: "15"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: limites-por-agente
  namespace: ai-agents
spec:
  limits:
  - default:
      cpu: "2"
      memory: "2Gi"
    defaultRequest:
      cpu: "500m"
      memory: "512Mi"
    type: Container
---
# Node selectors (fundação): DevOps e UX apenas em CPU (Phi-3 Mini).
# Pods Developer, Architect e QA podem solicitar GPU; DevOps e UX não.
# Exemplo para pod DevOps/UX — nodeSelector força nó sem GPU ou fila CPU:
# nodeSelector:
#   workload-type: cpu-only
# (Configurar nós/labels no Minikube conforme topologia: CPU-only vs GPU.)
```

Os manifests dos pods de **DevOps** e **UX** devem incluir `nodeSelector` (ou taints/tolerations equivalentes) para que rodem **exclusivamente** em CPU com modelo Phi-3 Mini, reservando a VRAM da RTX para Developer, Architect e QA.

## Deployment do Ollama (com GPU)

O Ollama precisa de acesso exclusivo à GPU no Minikube. Exemplo de deployment (namespace `ai-agents`):

- `nvidia.com/gpu: 1` nos `resources.limits` do container.
- Variável `OLLAMA_KEEP_ALIVE`: configurável (ex.: `5m` para manter modelo na VRAM por 5 minutos; recomenda-se alinhar à estratégia de slot único / agrupamento por modelo — ver [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md); ou `0` para descarregar após cada resposta e liberar VRAM para outros agentes).
- Volume persistente para modelos (ex.: `hostPath` ou PVC no NVMe).

Ver [09-setup-e-scripts.md](09-setup-e-scripts.md) para o YAML completo e integração no setup.

## GPU Lock (conceito e referência)

Antes de disputar o lock, o fluxo pode passar pelo **estágio pré-GPU** (validação em CPU com SLM — sintaxe, lint, SOLID) e pela opção de **batching de PRs** (revisão em lote pelo Architect), reduzindo contenção e uso de VRAM; ver [03-arquitetura.md](03-arquitetura.md). Para evitar OOM, apenas um pod deve usar o Ollama (e portanto a GPU) por vez. O **script de GPU Lock** usa Redis (`SETNX` com **TTL dinâmico**): o agente que for usar a GPU adquire o lock; os outros aguardam em loop até obter o lock ou até o timeout. O TTL é calculado em função do payload do evento (ex.: contagem de linhas do diff/PR no Redis): payload com mais de 500 linhas → TTL 120 s; caso contrário → TTL 60 s. Ao terminar, o agente libera o lock. **Garantia de não travar o cluster:** o orquestrador deve aplicar **hard timeout no Kubernetes** (ex.: 120 segundos de uso contínuo de GPU): se o pod exceder, o Kubernetes **mata o pod** independentemente do release no Redis; a tarefa volta para a fila (com penalidade, se configurado). Assim, mesmo em caso de OOM ou travamento do processo, o lock não fica órfão. Implementação em Python: ver [scripts/gpu_lock.md](scripts/gpu_lock.md), [09-setup-e-scripts.md](09-setup-e-scripts.md). Recuperação manual em [06-operacoes.md](06-operacoes.md) como último recurso.

## Docker: imagem base enxuta

Para não estourar o disco (na máquina de referência a partição raiz tem 402G; reserva ~120G para o cluster), usar **multi-stage build** e imagem base limpa. Cada agente não deve passar de ~300 MB (sem contar o modelo LLM, que fica em volume compartilhado).

**Estratégia:**

- Estágio 1 (builder): instalar dependências Python com `--no-cache-dir`.
- Estágio 2 (runtime): copiar apenas `/root/.local` e o código; `ENV PYTHONDONTWRITEBYTECODE=1` e `PYTHONUNBUFFERED=1`; instalar apenas o essencial (git, curl) para OpenCode/OpenClaw.
- Evitar gravar logs em disco dentro do container; direcionar para stdout do Kubernetes.

## Riscos de infraestrutura e mitigação

| Risco | Severidade | Mitigação |
|-------|------------|-----------|
| OOM (GPU) | Crítica | Singleton de inferência (Ollama) + GPU Lock + **truncamento na borda** (script na entrada do stream, limite de tokens, truncamento bruto) |
| Lock órfão (processo morre sem liberar) | Crítica | **Hard timeout no Kubernetes** (ex.: 120 s): pod morto ao exceder; tarefa volta à fila. Não depender do agente para release. Ver [06-operacoes.md](06-operacoes.md). |
| Colisão por expiração do lock | Alta | TTL dinâmico (por payload/PR); balanceamento GPU/CPU; PriorityClasses para evict gracioso — ver [03-arquitetura.md](03-arquitetura.md) |
| Picos de CPU | Alta | `cpulimit` e cgroups via Kubernetes Resources |
| Disco cheio | Alta | Deduplicação, volumes compartilhados (NFS/HostPath), limpeza de cache e `log-size` do Docker/K8s |
| Custos de API | Média | Cache de RAG para o CEO não repetir perguntas; controle no Gateway (max tokens/request) e pre-flight Summarize — ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) |
| Deadlocks | Média | Timeout rigoroso em cada pod de agente |
| Acúmulo de contexto no Redis | Média | **TTL nas chaves do working buffer:** configurar TTL para que mensagens antigas do buffer de conversas expirem automaticamente no Redis; o "lixo digital" evapora sem depender do agente DevOps. Mesmo princípio do TTL do GPU Lock (ver [scripts/gpu_lock.md](scripts/gpu_lock.md)); previsibilidade na infraestrutura. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) e [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md). |
| Corrupção de estado em pausa térmica | Alta | **Protocolo de checkpoint:** aos 80°C o DevOps injeta evento no Redis para **commit em branch efêmera de recuperação** (ex.: `recovery-failsafe-<timestamp>`) no repositório de trabalho (antes do Q-Suite aos 82°C). **Redis Streams idempotente:** consumidor só envia ACK após conclusão em disco; em pausa brusca a mensagem permanece na fila. **Recuperação automática:** ao voltar temp. ~65°C, orquestrador acorda pods, executa **checkout limpo**; se houver divergência no índice ou conflitos, **Architect (tarefa prioridade zero)** resolve na branch de recuperação; Redis reentrega tarefa pendente — sem comandos manuais no terminal. Ver [06-operacoes.md](06-operacoes.md) e [03-arquitetura.md](03-arquitetura.md). |
| **Cluster acéfalo (CEO/PO na nuvem + internet cai)** | **Alta** | **Protocolo de contingência local:** orquestrador monitora Redis; se nenhum comando estratégico do CEO em **time-out configurável** (ex.: 5 min), DevOps local é acionado: **commit do estado em branch efêmera de recuperação** (ex.: `recovery-failsafe-<timestamp>`), persistência da fila no LanceDB, **pausa** do consumo da fila de GPU. **Retomada automática:** health check contínuo (ping endpoints a cada 5 min, sem tokens); quando conectividade estável por **3 ciclos consecutivos**, orquestrador acorda DevOps e executa script de retomada (checkout limpo; Architect prioridade zero se conflitos; restaura fila e retoma consumo). **Sem comando humano**; Diretor recebe apenas notificação assíncrona. Ver [06-operacoes.md](06-operacoes.md) (seção *Contingência: cluster acéfalo*). |

## Configuração dos agentes (OpenClaw e OpenCode)

- **Pods CEO e PO (nuvem):** containers leves com chaves de API (OpenAI/Anthropic/Google). O OpenClaw faz a ponte com sistema de arquivos e internet.
- **Pod Developer (local):** OpenCode instalado; volume PVC no NVMe para o código persistir. O resultado do sandbox de dependências (npm/pip) passa por **quarentena de disco** e **análise determinística de diff** antes de ser incorporado ao repositório no NVMe — detalhes em [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md).
- **Pods CyberSec/Architect:** podem atuar como sidecars ou Jobs disparados quando o Developer faz *commit* (event-driven).
