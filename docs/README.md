# ClawDevs AI — Resumo

**ClawDevs AI** (ou **ClawDevs**) é um **ecossistema de agentes de IA** que funciona como um **time de desenvolvimento de software autônomo** na sua máquina — **24 por 7**. A ideia central: **qualquer um pode ter seu ClawDevs**: um time de nove agentes (CEO, PO, Architect, Developer, QA, DevOps, CyberSec, UX, DBA) orquestrados em **Kubernetes**, com estado em **Redis**, inferência local em **Ollama** e interface via **OpenClaw** (Telegram, Slack, voz). Tudo roda **dentro do cluster**, com limite de **65% do hardware**, em stack **open source e custo zero** para o núcleo.

**Criador do projeto:** **Diego Silva Morais**.

---

## O que é o ClawDevs AI

- **Time de agentes:** Nove agentes de IA com papéis definidos (estratégia, produto, arquitetura, código, testes, segurança, UX, dados, infra) que colaboram como um time real: backlog, issues, PRs, revisões, merge, deploy.
- **Na sua máquina:** O ambiente inteiro (pods, Redis, Ollama, OpenClaw, volumes) roda no **Kubernetes** (Minikube local). Quem tiver **máquina equivalente à de referência** (CPU, GPU, RAM, disco documentados) pode replicar o ClawDevs e ter o time na própria máquina.
- **Qualquer projeto, qualquer linguagem:** O ClawDevs não está preso a uma stack ou linguagem; o Diretor (humano) define o projeto e as prioridades; o time desenvolve em qualquer domínio e linguagem.
- **Autonomia nível 4:** O **CEO** é o único ponto de contato com o Diretor; a maior parte das decisões (bugs, UI, otimizações, cronograma) é autônoma ou notificada por digest; o humano é acionado só em decisões estratégicas, orçamento, segurança crítica ou impasses que exijam desempate.
- **Auto-evolução:** O repositório pode ser o **próprio ClawDevs** (#self_evolution): os agentes melhoram o projeto entre si; **início e parada** dessa tarefa são **exclusivos do Diretor** (ex.: via Telegram).

---

## O que você consegue fazer com o ClawDevs AI

- **Ter um time de dev sempre disponível:** Acionar o time por chat ou voz (Telegram/Slack), pedir pesquisa, backlog, arquitetura, implementação, testes, revisão de segurança e UX, sem depender de horário ou fila externa.
- **Desenvolver e manter qualquer projeto:** Do protótipo ao produto: o PO prioriza o backlog, o Architect governa a base de código, o Developer implementa (com OpenCode), QA e CyberSec revisam, DevOps cuida de CI/CD e infra; o CEO consolida e reporta ao Diretor.
- **Controlar custo e risco:** Inferência local (Ollama) no cluster reduz custo de API; uso de nuvem (OpenRouter, etc.) é opcional e com **limite de gastos**. Segurança (Zero Trust, OWASP, CISO, kill switch por temperatura) está na base do desenho.
- **Replicar o ambiente:** Com a **máquina de referência** (specs e comandos de verificação na documentação), qualquer pessoa pode subir o mesmo ambiente e operar o ClawDevs de forma sustentável.
- **Evoluir o próprio ClawDevs:** No modo #self_evolution, o Diretor inicia/para a tarefa e o time melhora regras, SOUL, skills e configs via PR em repositório dedicado, com aprovação humana.

---

## Stack e princípios

- **Kubernetes (Minikube)** — orquestração dos agentes e serviços.
- **OpenClaw** — gateway, orquestrador e interface (voz/chat); configuração e workspace no K8s.
- **Ollama** — inferência local no cluster; provedores em nuvem opcionais (OpenRouter, etc.) quando aprovado.
- **Redis** — estado global, filas (Streams), GPU Lock, kill switch.
- **OpenCode** — geração de código no agente Developer.

**Prioridades (não negociáveis):** (1) **Cibersegurança** — Zero Trust, defesa em profundidade, sem trocar segurança por custo ou velocidade. (2) **Custo baixíssimo** — cluster em ~65% do hardware; APIs em nuvem com freio de gastos. (3) **Alta performance** — produtividade sem colapso de recursos; controles de segurança eficientes (CPU, whitelist, análise estática).

**Regra do projeto:** Open source, custo zero no núcleo, alta performance; máximo uso do OpenClaw (config, bindings, session, memory, tools) — código novo só quando não houver solução no OpenClaw.

---

## Para onde ir a partir daqui

| Se você quer… | Onde ir |
|---------------|--------|
| **Sumário completo** (todos os docs por tema e por arquivo) | [INDEX.md](INDEX.md) |
| Objetivo, stack e máquina de referência | Doc 00 (objetivo e máquina) no INDEX |
| Visão, agentes e autonomia nível 4 | Doc 01 (visão e proposta) no INDEX |
| Configurar e rodar (setup) | Doc 09 (setup e scripts) no INDEX |
| Revisões pós-crítica e termos-chave | [revisoes-analistas-e-termos.md](07-operations/revisoes-analistas-e-termos.md) |

**Terminologia rápida:** **Diretor** = humano decisor. **ClawDevs** = ecossistema (enxame de 9 agentes no K8s com OpenClaw). **OpenClaw** = orquestrador e interface. **Ollama** = inferência local. **OpenCode** = geração de código no Developer. Mais termos: ver revisões e INDEX.
