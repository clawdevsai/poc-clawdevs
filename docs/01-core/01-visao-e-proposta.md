# Visão e Proposta

## Objetivo

Implementar o **ClawDevs** — time de desenvolvimento de software 100% autônomo — em que agentes de IA colaborativos atuam em conjunto para construir e manter um ecossistema de desenvolvimento de alta performance **na máquina do Diretor**, **prontos para trabalhar 24 por 7**. O ClawDevs desenvolve **qualquer projeto em qualquer linguagem de programação** para o Diretor. O Diretor (humano) atua como decisor estratégico e é acionado apenas para decisões de alto impacto ou impasses.

**Modo de auto-evolução:** Existe um caso especial em que o repositório alvo é o **próprio ClawDevs** e a evolução é autônoma: os agentes melhoram o projeto entre si, sem validação ou aprovação do Diretor durante a execução (início e parada da tarefa **#self_evolution** são exclusivos do Diretor via Telegram). Detalhes em [36-auto-evolucao-clawdevs.md](36-auto-evolucao-clawdevs.md).

**Prioridades (não negociáveis):** (1) **Cibersegurança** — resistência a ataques cibernéticos (injeção de prompt, RCE, skills/dependências maliciosas, exfiltração); segurança não é negociada por custo ou velocidade. (2) **Custo baixíssimo** — de API e de hardware. (3) **Performance segura e altíssima** — toda escolha técnica (Ollama vs nuvem, truncamento, FinOps, GPU Lock, balanceamento) e **toda camada de segurança** deve ser avaliada sob esses critérios. Controles de segurança priorizam **verificação determinística na borda** (script, regex, análise estática, whitelist) para não gastar GPU/tokens — ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

**Como será desenvolvido:** O setup inicial (Minikube, Redis, Ollama, OpenClaw) é o **bloco de fundação — passo zero** do ClawDevs. O ambiente alvo é a **máquina de referência** documentada em [00-objetivo-e-maquina-referencia.md](00-objetivo-e-maquina-referencia.md); desenvolvedores com máquina equivalente podem replicar o ClawDevs seguindo esta documentação. A evolução para múltiplos agentes operando em paralelo exige orquestração (Kubernetes), filas de eventos (Redis Streams) e trava de GPU para evitar colapso de memória; essa base está documentada em [03-arquitetura.md](03-arquitetura.md) e [04-infraestrutura.md](04-infraestrutura.md). A diferença de performance entre nuvem e máquina local é grande: inferência local (Ollama) sofre gargalos de hardware e deve respeitar o **limite do Kubernetes** — o cluster é configurado para consumir no máximo **65% do hardware**; orquestração, estado e **volumes** ficam dentro do Kubernetes. APIs em nuvem consomem tokens e créditos com validade — recomenda-se calibrar expectativas e configurar freio de gastos desde o início.

## Estrutura dos Agentes (resumo)

| Agente | Função principal |
|--------|------------------|
| **CEO** | Estratégia, pesquisa de mercado, gestão de stakeholders, interface com o Diretor. |
| **Product Owner (PO)** | Backlog, priorização, Issues no GitHub, Kanban, contexto RAG para tarefas. |
| **DevOps / SRE** | IaC, CI/CD, repositórios, FinOps, *code review* de infraestrutura. |
| **Architect** | Governança técnica, *code review*, Fitness Functions, ADRs, merge de PRs. |
| **Developer** | Implementação e codificação; submete PRs; não realiza merge. |
| **QA** | Garantia de qualidade, testes de integração, *code review* focado em bugs e estabilidade. |
| **CyberSec** | Segurança, conformidade (LGPD, OWASP), SAST/DAST, auditoria de PRs. |
| **UX** | Experiência do usuário, *code review* de frontend, acessibilidade. |
| **DBA** | Validação de normas de banco, performance e baixo custo de hardware/espaço; queries precisas e configuração; *code review* da camada de dados. |
| **Governance Proposer** | Propor ajustes a rules, soul, skills, task e configs em **repo GitHub dedicado** (cron + busca internet); PR para Diretor aprovar; após merge, aplicar modificações localmente (pull + sync). Validação humana obrigatória no PR. Ver [35-governance-proposer.md](35-governance-proposer.md). |

Detalhamento completo em [02-agentes.md](02-agentes.md). **Risco na transição estratégia→execução:** se o CEO não filtrar ideias e tarefas antes de enviar ao PO, o custo de API em nuvem estoura e o projeto falha na gestão de tarefas desde o início; ver [02-agentes.md](02-agentes.md) (seção CEO).

## Ideias de expansão

### 1. Dashboard de Orquestração ("War Room")

Interface visual em que cada agente aparece como avatar ativo: estado do Agente CEO (pesquisa em tempo real), Agente Developer (branch em edição), Agente CyberSec (alertas). Objetivo: tornar a automação auditável e visual.

### 2. Chaos Engineering para IA

Cenários de estresse: Issue com requisitos contraditórios ou biblioteca obsoleta para validar se o Agente Architect e o Agente CyberSec barram o PR. Gera um "manual de falhas" para calibrar prompts e garantir que o *kill switch* (Q-Suite) funcione sob pressão.

### 3. Integração OpenClaw como interface externa

O OpenClaw atua como interface de voz ou chat (WhatsApp/Telegram) entre o Diretor e o Agente CEO. Exemplo: comando por áudio — *"Pergunte ao CEO como está o burn rate e se o DevOps reduziu os custos de AWS"* — e resposta consolidada em segundos.

## Autonomia nível 4 (alta)

O sistema opera "silencioso por padrão". O Agente CEO é o único ponto de contato com o Diretor e filtra o ruído; o Diretor é acionado apenas para decisões estratégicas ou impasses éticos/financeiros.

### 1. Matriz de escalonamento

- **Decisões autônomas (silenciosas):** escolha de bibliotecas compatíveis, correções de bugs, ajustes de UI, otimização de queries.
- **Decisões de notificação (relatório semanal):** mudanças de cronograma, conclusão de grandes funcionalidades, relatórios FinOps.
- **Decisões de notificação (digest diário):** aprovações menores e notificações não críticas são agrupadas em digest diário assíncrono; detalhes em [05-seguranca-e-etica.md](05-seguranca-e-etica.md) (matriz de escalonamento probabilística).
- **Decisões de interrupção (chamada ao Diretor):** alteração radical de escopo, estouro de orçamento de nuvem, dilemas de privacidade, deadlock entre Agente CyberSec e Agente Architect, ou impasse Developer–Architect quando a recusa do Architect tiver **tag de vulnerabilidade crítica (cybersec)** — nesse caso o CEO não pode forçar o merge (ver abaixo).
- **Desempate pelo CEO (antes de acionar o Diretor):** Em impasses **puramente técnicos** entre Developer e Architect (ex.: estilo de código, padrão de design), o **Agente CEO atua como juiz de desempate**. O CEO avalia o código debatido **estritamente pelo impacto no valor de negócio** e pode destravar a esteira **antes** de escalar ao humano. **Regra estrita:** o CEO **não tem autoridade sobre segurança**. Se a recusa do Architect tiver **tag de vulnerabilidade crítica (cybersec)**, o CEO **não pode forçar o merge**; o impasse escala para o Diretor. O sistema resolve a maioria das divergências estilísticas sozinho e chama o humano apenas quando há risco real de segurança.
- **Degradação automática (sem esperar humano):** **Impasse Developer–Architect:** após **2ª rejeição (2º strike)** o orquestrador injeta **prompt de compromisso** no Architect (gerar o código exato que aprovaria o PR). Se o **5º strike** for atingido, o orquestrador **empacota o contexto** e **roteia para arbitragem na nuvem** (modelo superior reescreve); só em falha dessa escalação marca PR como draft/bloqueado, **devolve a issue ao backlog do PO** (a issue não se perde), remove da fila de GPU e Developer segue para próxima tarefa. O **PO** deve analisar **todo o histórico** e encontrar **solução com o Architect**; a tarefa **retorna ao desenvolvimento**. Ver [06-operacoes.md](06-operacoes.md).

### 2. Canal de transparência (Shadow Mode)

O Agente CEO mantém um **log de raciocínio** acessível (painel ou arquivo), permitindo ao Diretor entender o motivo das decisões e ajustar a "temperatura" da autonomia em tempo real, sem microgerenciamento.

### 3. Aprovação por omissão (apenas cosmético)

Aprovação por omissão aplica-se **somente** a impasses **estritamente cosméticos** (diff com apenas CSS, componentes de UI isolados ou formatação markdown), definidos de forma **determinística** (sem LLM para "baixo risco"). Se o CEO enviar alerta desse tipo e o Diretor **não responder** no prazo configurado (ex.: **6 horas**), o orquestrador dispara **degradação aceitável**: o CEO **aprova por omissão** a rota mais conservadora/barata, **destrava a esteira** e **registra a decisão** em **MEMORY.md** para auditoria posterior. O humano audita as decisões por omissão pelo histórico (ex.: no dia seguinte). **Impasse de código lógico ou backend:** não se usa timer; o orquestrador aplica **5 strikes** e a issue **volta ao backlog do PO** (Developer pega outra tarefa). A tarefa **não se perde**: o **PO** analisa **todo o histórico** e encontra uma **solução com o Architect**; em seguida a tarefa **retorna ao desenvolvimento**. Ver [06-operacoes.md](06-operacoes.md) e [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md).

---

## Próximos passos (escalabilidade)

O guia foca na execução orquestrada no Minikube com um único cluster. Para **OpenClaw e OpenCode atuando juntos como equipe autônoma** sem derrubar o ambiente quando o uso diário exigir mais processamento concorrente:

- **Orquestração:** O passo natural é manter e evoluir o uso de **Kubernetes** (Minikube local; em produção, cluster completo). Evita colapso ao escalar de um único container para múltiplos pods.
- **Filas e GPU Lock:** Usar **filas de eventos** (Redis Streams) com **trava de GPU** garante que, independentemente de quantos agentes enviem solicitações concorrentes, só uma inferência carrega o modelo pesado por vez — evita estouro de memória e educa sobre como ambientes reais gerenciam enxames de agentes. Ver [03-arquitetura.md](03-arquitetura.md) e [04-infraestrutura.md](04-infraestrutura.md).
