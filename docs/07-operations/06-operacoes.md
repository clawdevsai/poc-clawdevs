# Operações: Primeiros socorros e prevenção

Operações do **ClawDevs**. O **objetivo operacional é autonomia nível 4**: o cluster deve recuperar-se sozinho sempre que possível (evict por prioridade, balanceamento dinâmico GPU/CPU; ver [03-arquitetura.md](03-arquitetura.md)). A **recuperação padrão** após pausa térmica é **automática** (checkpoint aos 80°C, Redis com ACK só após conclusão em disco, retomada com checkout limpo e, se houver conflito, resolução pelo Architect na branch de recuperação antes de reentregar a tarefa pendente). O manual de primeiros socorros abaixo é **último recurso** — quando os mecanismos automáticos não forem suficientes (ex.: driver zumbi, colisão por expiração do lock). A intervenção humana no terminal (fases 1–3) deve ser a **exceção**, não a regra.

---

## Contingência: cluster acéfalo (queda de conectividade com CEO/PO na nuvem)

**Cenário de risco:** O Agente CEO e o Product Owner rodam na nuvem (APIs Gemini, etc.); o time técnico roda localmente (RTX 3060 Ti). Se a **internet cair**, o fluxo estratégico para imediatamente, mas a execução local **não** — os agentes locais continuam consumindo a fila do Redis sem novo comando estratégico, podendo esgotar a GPU em tarefas desalinhadas e corromper o estado da aplicação. É necessário um **protocolo de fallback 100% local e determinístico**, sem depender de intervenção humana no momento do pânico nem de esperar a nuvem voltar.

**Responsável pela detecção:** O **orquestrador** (ou componente de borda que monitora o Redis local) monitora a **ação** no Redis. O **Agente DevOps local** já monitora o hardware; portanto é o ator que **executa** a contingência assim que o orquestrador sinalizar falha — a detecção em si é **automática** (sem bater em LLM).

**Regras obrigatórias:**

1. **Heartbeat no Redis local:** O orquestrador considera "nuvem inacessível" quando **nenhum comando com tag de estratégia do CEO** for recebido no Redis por um **time-out configurável** (ex.: **5 minutos** de silêncio absoluto). O valor deve ser configurável (ex.: variável de ambiente ou chave no config JSON).
2. **Ação imediata ao estourar o time-out:** No instante em que o time-out estoura, o **DevOps local** é acionado (via evento de prioridade máxima no Redis). O DevOps **não** usa `git stash`. Em vez disso:
   - **Executa commit do estado atual** (quebrado ou não) em uma **branch dedicada efêmera**, ex.: `recovery-failsafe-YYYYMMDD-HHMMSS`, isolando o estado de forma rastreável e evitando conflitos de merge silenciosos na retomada.
   - **Persiste o estado da fila do Redis** no banco vetorial **LanceDB** (já usado pelo projeto para memória).
   - **Pausa instantaneamente** o consumo da fila que disputa o lock de GPU; os agentes locais deixam de consumir novos eventos até a retomada.
3. **Retomada automática (sem intervenção humana):** A retomada após cluster acéfalo é **totalmente automática**; o Diretor **não** precisa executar nenhum comando para destravar. Durante a pausa, o orquestrador executa **health check contínuo**: ping em endpoints (ex.: API Google Gemini, serviços de autenticação) a cada **5 minutos**, **sem gastar tokens** (apenas teste de rede). Quando a conectividade retornar com **latência estável por 3 ciclos consecutivos** (evitar flapping), o orquestrador **acorda automaticamente** o DevOps e dispara o script de retomada:
   - Executa **checkout limpo** (volta à branch de trabalho principal a partir da branch efêmera de recuperação).
   - Se houver **divergência no índice** (falha de merge ou estado sujo detectado pelo script) ou conflitos na branch de recuperação, o orquestrador aciona o **Architect** em **tarefa de prioridade zero** para **inspecionar e resolver o conflito estrutural** na branch de recuperação. Se a resolução ficar dentro do limite de 5 strikes do Architect, a fila do Redis volta a ser consumida.
   - Restaura o estado da fila a partir do LanceDB (se aplicável) e **retoma o consumo** da fila automaticamente. **Nenhuma intervenção humana** para destravar após cluster acéfalo.
4. **Fechamento do ciclo de governança:** O orquestrador envia **notificação assíncrona** ao Diretor (Telegram/Slack ou digest diário), informando: (a) que a contingência foi acionada, (b) o **tempo de inatividade**, (c) que a **retomada automática** foi concluída com sucesso (ou que houve necessidade de Architect e o resultado). O Diretor **não** é bloqueio ativo; a notificação é informativa. O risco vira processo controlado e auditável.

**Referência:** [05-seguranca-e-etica.md](05-seguranca-e-etica.md) (riscos residuais), [03-arquitetura.md](03-arquitetura.md) (Blackboard e resiliência), [04-infraestrutura.md](04-infraestrutura.md) (riscos). Implementação técnica: issue de contingência CEO/nuvem (heartbeat + commit em branch efêmera + persistência LanceDB + health check + retomada automática + Architect para conflitos). **Nota:** O comando explícito de desbloqueio (ex.: `./scripts/unblock-degradation.sh`) aplica-se **apenas** ao **workflow de recuperação pós-degradação** (orçamento 10–15% das tarefas na rota de fuga), não ao cluster acéfalo — ver seção *Workflow de recuperação pós-degradação* abaixo.

Quando a GPU trava no Kubernetes no Pop!_OS, o driver pode levar a interface gráfica junto ou entrar em estado "zumbi". Na máquina de referência (ver [00-objetivo-e-maquina-referencia.md](00-objetivo-e-maquina-referencia.md)) a GPU é uma RTX 3060 Ti 8GB. Seguir as fases abaixo **na ordem**, antes de desligar o gabinete (para evitar corromper o NVMe).

---

## Manual de primeiros socorros: GPU travou (recuperação manual)

Use as fases abaixo quando evict por prioridade e balanceamento não resolverem (ex.: colisão por expiração do lock, driver em estado zumbi).

### Fase 1: Diagnóstico rápido (host)

No Pop!_OS, **fora do Minikube**, abrir um terminal e executar:

```bash
nvidia-smi
```

- **Se o comando travar:** o driver em nível de kernel falhou. Ir para a **Fase 3**.
- **Se mostrar "Memory Leak" ou processos zumbis:** há pods segurando VRAM indevidamente. Ir para a **Fase 2**.

### Fase 2: Reset cirúrgico (Kubernetes)

Se o sistema ainda responde, isolar e derrubar apenas o que está causando o problema.

1. **Derrubar o serviço de inferência (Ollama):**
   ```bash
   kubectl delete pod -l app=ollama -n ai-agents --force
   ```

2. **Limpar o lock do Redis** (caso o script de GPU Lock tenha ficado travado):
   ```bash
   kubectl exec -n ai-agents deploy/redis -- redis-cli DEL gpu_active_lock
   ```
   (Chave do lock: `gpu_active_lock`. Script: [scripts/gpu_lock.py](../scripts/gpu_lock.py).)

3. **Reiniciar o Device Plugin da NVIDIA:**
   ```bash
   kubectl delete pod -n kube-system -l app=nvidia-device-plugin-daemonset
   ```

### Fase 3: Reset de driver (opção nuclear)

Se `nvidia-smi` não responde e a tela está instável, forçar o Linux a liberar a GPU sem reiniciar a máquina.

1. **Parar o Minikube:**
   ```bash
   minikube stop
   ```

2. **Listar e encerrar processos que usam a GPU:**
   ```bash
   sudo fuser -v /dev/nvidia*
   sudo fuser -kv /dev/nvidia*
   ```
   **Atenção:** isso pode fechar a interface gráfica.

3. **Recarregar o driver (se necessário):**
   ```bash
   sudo modprobe -r nvidia_uvm && sudo modprobe nvidia_uvm
   ```

### Fase 4: Modo de recuperação (NVMe e RAM)

Se o problema foi falta de disco (ex.: 200 GB cheios) ou RAM, o Minikube pode entrar em estado `Evicted`.

- **Limpeza de logs e imagens:**
  ```bash
  minikube ssh "docker system prune -a --volumes"
  ```

- **Aumentar o limite de inotify** (comum em ambientes com muitos agentes):
  ```bash
  sudo sysctl fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p
  ```

---

## Prevenção

- **Estratégia de uso de hardware (GPU/CPU):** Um **consumidor GPU por etapa ou slot único** — não múltiplos agentes disputando o mesmo evento; pipeline explícito ou job "Revisão pós-Dev" que adquire o lock uma vez e executa Architect, QA, CyberSec e DBA em sequência. Maximiza utilização da GPU e da CPU dentro do limite de 65%. Ver [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md).
- **Validação em CPU antes do lock de GPU:** O orquestrador submete artefatos (diff/código) a um SLM em CPU (sintaxe, lint, SOLID) antes de a tarefa entrar na fila que disputa o lock; o Architect usa GPU só para análises que exigem complexidade. **Batching de PRs:** o orquestrador pode acumular micro-alterações para revisão em lote pelo Architect, pagando a latência de carregamento do modelo uma vez. Ver [03-arquitetura.md](03-arquitetura.md).
- **Hard timeout no Kubernetes (lock de GPU):** Primeira linha de defesa contra lock órfão (processo morre sem liberar). Configurar os pods/Jobs que usam GPU com **activeDeadlineSeconds** (ex.: 120 s); ao exceder, o K8s mata o pod e a tarefa volta à fila. Exemplo YAML em [04-infraestrutura.md](04-infraestrutura.md) (seção GPU Lock) e [k8s/development-team/gpu-lock-hard-timeout-example.yaml](../k8s/development-team/gpu-lock-hard-timeout-example.yaml). Recuperação manual (limpar `gpu_active_lock` no Redis) é **último recurso**. Script do lock: [scripts/gpu_lock.py](../scripts/gpu_lock.py).
- **Protocolo transacional de checkpoint (pausa térmica):** Recalibrar o monitoramento do DevOps para agir aos **80°C** (gatilho **pré-crítico**), não apenas aos 82°C. Aos **80°C** o DevOps **não** derruba os pods; **injeta um evento de prioridade máxima no Redis** ordenando **commit do estado atual em branch efêmera de recuperação** (ex.: `recovery-failsafe-YYYYMMDD-HHMMSS`) — isolando o estado de forma rastreável antes do calor derrubar a execução (evita conflitos que `git stash` + `stash pop` causariam em ambiente multiagente). O **82°C** permanece como corte de força (Q-Suite): pausar todos os agentes locais quando necessário. Assim o hardware é protegido do derretimento térmico e o software da corrupção de dados (repo e fila).
- **Redis Streams — transações idempotentes:** Todos os payloads no Redis Streams devem ser tratados como **transações idempotentes**. O consumidor **não** envia ACK até o trabalho estar **100% concluído em disco**. Se o pod for pausado aos 82°C no susto, a mensagem não recebe ACK e permanece **pendente na fila**; na retomada, o Redis reentrega a tarefa e o agente retoma do ponto exato.
- **Retomada automática:** Quando a temperatura voltar a ~65°C, o orquestrador **acorda os pods sozinho**, executa **checkout limpo** (volta à branch de trabalho principal). Se houver **divergência no índice** ou conflitos na branch de recuperação, o orquestrador aciona o **Architect** em **tarefa de prioridade zero** para inspecionar e resolver o conflito na branch de recuperação **antes** de reentregar a tarefa; só então os agentes voltam a escutar o Redis e o Redis **reentregue** a tarefa pendente. Nenhuma necessidade de comandos manuais no terminal (fases 1–3 do manual só quando a recuperação automática falhar).
- **Tarefas interrompidas (regra obrigatória):** Nenhuma tarefa interrompida (FinOps, timeout K8s, pausa térmica, falha de arbitragem, etc.) pode ser **descartada**. Sempre **devolver ao backlog do Product Owner**; a issue **não se perde**. Ver [03-arquitetura.md](03-arquitetura.md) (Blackboard e resiliência).
- **Diversidade de ferramenta (persistência):** Se uma abordagem com a **mesma ferramenta** falhar **duas vezes consecutivas** pelo **mesmo motivo** (ex.: headless timeout, elemento não encontrado), o orquestrador **bloqueia o acesso a essa ferramenta** no escopo daquela tarefa — o agente é forçado a mudar vetor (CLI, API, outra skill). Evita loops que esgotam orçamento e GPU. Regra aplicada no orquestrador (fluxo zero trust).
- **Governança do CEO (token bucket e degradação por eficiência):** O **token bucket** (limite de eventos de estratégia por janela) e a **degradação por eficiência** (razão CEO/PO; rebaixamento para modelo local em CPU) evitam paralisia por exaustão financeira **antes** de a cota $5/dia ser atingida. Controle primário sustentável na infraestrutura; $5/dia permanece freio de emergência. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) e [05-seguranca-e-etica.md](05-seguranca-e-etica.md).
- **Persistência acoplada ao FinOps:** O contador de tentativas de resolução é integrado ao **Gateway FinOps**. No pre-flight de sumarização, o custo estimado da chamada é multiplicado pelo **número da tentativa atual** (penalidade progressiva). Quando o gatilho for atingido (ex.: aprovar a chamada comprometeria a cota diária restante), o orquestrador **interrompe a execução** daquela tarefa, **devolve ao backlog do PO** e **libera as travas de hardware** (GPU, etc.) para os outros agentes — degradação graciosa, sem estourar orçamento nem exaustão térmica. Ver [13-habilidades-proativas.md](13-habilidades-proativas.md) e [10-self-improvement-agentes.md](10-self-improvement-agentes.md).
- **Uso de VRAM:** Evitar modelos FP16. Usar modelos quantizados **GGUF** ou **EXL2** (ex.: Q4_K_M para RTX 3060 Ti).
- **Monitoramento:** Manter um terminal com `watch -n 1 nvidia-smi` para acompanhar uso de VRAM e temperatura em tempo real.

## Disjuntor de draft_rejected (ciclo PO–Architect)

Quando o PO gera tarefas com base em RAG desatualizado (embeds antigos, refatoração não documentada), o Architect pode devolver **draft_rejected** repetidamente; o PO reescreve com o **mesmo contexto defeituoso** e o ciclo pode esgotar GPU e fila antes de a cota global de degradação (10–15%) ser atingida. Para **intervenção precoce**, o orquestrador aplica um **disjuntor** focado na frequência de rejeições **por épico**.

- **Regra do disjuntor:** O orquestrador **rastreia rejeições por épico**. Se a **mesma épico** receber **draft_rejected 3 vezes consecutivas**, a tarefa é **congelada imediatamente** no Redis Streams (estancar o loop). Este disjuntor atua **antes** da cota global de degradação; não substitui o orçamento de degradação, complementa-o.
- **Autocura (RAG health check):** Ao acionar o disjuntor, o orquestrador instancia uma **sessão isolada** (subagente) que executa **health check determinístico** do RAG — **sem LLM**: (1) checar as **datas de indexação** dos documentos que o PO usou vs **último commit na main**; (2) checar se a **estrutura de pastas** mencionada na épico existe no disco; (3) se houver conflito não documentado → **forçar atualização da memória local** do orquestrador (base de conhecimento). Ao **descongelar** a épico, o PO recebe a rejeição **envelopada no contexto saneado** (documentação/indexação atualizada). Outras tarefas seguem rodando; não é necessário humano para desbloquear a autocura. Ver [03-arquitetura.md](03-arquitetura.md) (Ciclo de rascunho).

## Prevenção de deadlock (Five Strikes e fallback contextual)

Quando o Developer e o Architect **discordam no mesmo PR**, o orquestrador aplica um **mecanismo de fallback contextual** antes de abandonar a tarefa, evitando que funcionalidades essenciais (ex.: alteração de schema de banco) fiquem incompletas por falha de consenso.

- **Após 2ª rejeição (2º strike):** O orquestrador injeta um **prompt de compromisso** no Architect: alterar temporariamente as restrições para que o Architect **gere o trecho de código exato** que tornaria o PR aprovado (revisor atua como coautor e fecha a lacuna lógica).
- **Se o 5º strike for atingido:** Em vez de abandonar a tarefa imediatamente, o orquestrador **empacota o contexto completo do impasse** (histórico de discussões e tentativas frustradas) e **roteia para a nuvem** para **arbitragem avançada**: um modelo superior reescreve a lógica para satisfazer ambos os lados. A esteira continua girando de forma funcional e tarefas críticas não ficam em limbo.
- **Abandono apenas em exceção:** Só se a escalação para arbitragem na nuvem falhar, o orquestrador marca o PR como **draft** ou **bloqueado**, **devolve a issue ao backlog do PO** (e remove a tarefa da fila da GPU); o Developer pega a próxima tarefa válida do backlog. A issue **não se perde** — permanece no backlog do Product Owner. **Tratamento obrigatório:** o PO deve **analisar todo o histórico** do impasse e **encontrar uma solução em conjunto com o Architect** (requisitos, critérios de aceite ou abordagem técnica); em seguida a tarefa **volta para o desenvolvimento** (reprioritizada, reentra na esteira). A exceção deve ser documentada. Ver [01-visao-e-proposta.md](01-visao-e-proposta.md) e [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md).

### Orçamento de degradação

Para evitar que a rota de fuga (5º strike concluído em abandono + aprovação por omissão **cosmética**) acumule **dívida técnica silenciosa** sem intervenção, o orquestrador mantém uma **métrica acumulativa**: contagem de eventos de 5ª strike (abandono) e de eventos de aprovação por omissão **cosmética**. Se **mais de 10–15% das tarefas do sprint** caírem nessa rota de fuga (valor configurável), o orquestrador **não** aciona o freio de mão global imediatamente; primeiro executa o **loop de consenso automatizado (pré-freio de mão)** abaixo. Só se esse loop falhar (ou não for aplicável) é que o DevOps dispara alerta crítico, aciona **freio de mão** e **pausa a esteira**; a esteira **só retoma** após o **workflow de recuperação** (recalibragem pelo Diretor e **comando explícito de desbloqueio**). Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (métrica configurável no Gateway).

#### Loop de consenso automatizado (pré-freio de mão)

**Condição de acionamento:** O loop é acionado quando o limite configurável (10–15% das tarefas do sprint na rota de fuga) for **atingido**. Opcional: exigir um **número mínimo de tarefas no sprint** para evitar acionar o loop em sprint vazio (valor configurável).

**Passos:** (1) O orquestrador cria um **subfluxo isolado** em que os agentes **QA** e **Architect** recebem o **Degradation Report** (ou o conteúdo/rascunho que será usado no relatório) como **input de contexto**. (2) QA e Architect propõem um **ajuste temporário** — por exemplo, flexibilizar critérios de aceite do PO ou fitness functions do Architect para aquele sprint. (3) O sistema **testa em uma única tarefa crítica**: a tarefa é escolhida de forma **determinística** (ex.: primeira da fila pendente ou por prioridade configurada). (4) **Critério de sucesso:** a tentativa de autocorreção **resolve de forma segura** se, na tarefa pilot, o PR for aprovado pelo Architect sem novo 5º strike (critério verificável). (5) Se **resolver**, a esteira segue sem acordar o Diretor; se **falhar**, o orquestrador aciona o **freio de mão** e segue o **workflow de recuperação pós-degradação** abaixo (relatório em Markdown, checklist Diretor, comando explícito de desbloqueio).

**QA como auditor da dívida técnica:** O agente **QA** deve focar **testes exploratórios** estritamente nas **áreas onde a aprovação por omissão cosmética foi acionada** (regiões sinalizadas pelo orquestrador ou em MEMORY.md). Objetivo: garantir que a decisão rápida (rota conservadora) não quebrou integrações futuras; o QA atua como auditor dessa dívida técnica. Ver [02-agentes.md](02-agentes.md) (Agente QA).

#### Workflow de recuperação pós-degradação (obrigatório)

Este workflow aplica-se **somente** ao cenário de **orçamento de degradação** (10–15% das tarefas na rota de fuga). **Não** se confunde com a contingência de **cluster acéfalo** (queda de internet), que tem **retomada automática** sem comando humano — ver seção *Contingência: cluster acéfalo* acima. Este workflow é acionado **apenas após** a falha do loop de consenso automatizado (pré-freio de mão) acima, ou quando o loop não for aplicável (ex.: sprint sem tarefas suficientes para pilot). A pausa por orçamento de degradação **não** pode virar paralisia indefinida. É obrigatório um **fluxo de trabalho padronizado de recuperação** que dê ao Diretor diagnóstico claro e exija **comando explícito de desbloqueio** para reativar o cluster.

1. **No momento em que a esteira pausa:** O orquestrador **gera automaticamente** um **relatório de degradação** (arquivo Markdown no repositório, ex.: `docs/agents-devs/degradation-report-YYYY-MM-DD.md` ou caminho configurável). O Diretor **não** deve ter de garimpar logs no terminal. O relatório deve conter:
   - **Sumário** de quais issues falharam (5º strike ou aprovação por omissão cosmética).
   - **Trechos de código** ou referências ao impasse (ex.: PRs bloqueados, diff relevante).
   - **Histórico de prompts** ou contexto do impasse (resumido, para o humano entender a causa).
   - **Erro mastigado** para o humano (ex.: "Architect rejeitou 3x por padrão de design; Developer não alterou; 5º strike atingido").

2. **Checklist obrigatório antes de reativar:** Antes de reativar a esteira, o **Diretor** deve:
   - Revisar o **MEMORY.md** (e o relatório de degradação).
   - Ajustar os **limiares de exigência** ou critérios no **arquivo de configuração** (ex.: JSON do Gateway ou config dos agentes) conforme necessário — por exemplo, recalibrar prompts do Architect ou critérios de aceite do PO.

3. **Comando explícito de desbloqueio:** A retomada da esteira **não** ocorre automaticamente após um tempo nem por detecção de mudança de arquivos. O orquestrador (ou Gateway) deve expor um **comando de terminal específico** (ex.: `./scripts/unblock-degradation.sh` ou comando equivalente no CLI do projeto). **Somente** após o Diretor executar esse comando explicitamente é que os agentes **ficam autorizados** a voltar a consumir eventos do Redis. Esse comando funciona como **assinatura operacional** de que o humano assumiu o controle e corrigiu a rota; sem ele, o cluster permanece em estado de exceção.

4. **Responsável:** O **Diretor humano** é o responsável pela recalibragem e pelo comando de desbloqueio. Nenhum script nem agente pode reativar a esteira por conta própria após pausa por orçamento de degradação.

## Aprovação por omissão (timer duro — apenas cosmético)

O timer e a aprovação por omissão aplicam-se **somente** quando o impasse for **estritamente cosmético**: o diff envolve **apenas** arquivos CSS, componentes de UI isolados ou formatação de markdown. A classificação é **determinística** (ex.: por extensão ou glob de arquivos), **sem** uso de LLM para classificar "baixo risco". Se o Diretor **não responder** dentro do prazo configurado (ex.: **6 horas**), o orquestrador dispara a degradação aceitável: o CEO **aprova por omissão** a rota mais conservadora/barata, **destrava a esteira** e **registra a decisão** em **MEMORY.md** para auditoria posterior. No dia seguinte o humano audita as decisões por omissão pelo histórico. Ver [01-visao-e-proposta.md](01-visao-e-proposta.md) e [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md).

**Impasse de código lógico ou backend:** Se o impasse envolver **código lógico ou backend**, **não** se dispara aprovação por omissão. O orquestrador aplica a **mesma lógica de 5 strikes** acima: a issue **volta ao backlog do PO** (Developer pega outra tarefa do backlog). A tarefa **não se perde**: o **PO** deve **analisar todo o histórico** e **encontrar uma solução com o Architect** (requisitos, critérios de aceite ou abordagem técnica); em seguida a tarefa **retorna ao desenvolvimento** (reprioritizada, reentra na esteira).

## Chaves Redis e scripts (Fase 3 — implementação)

- **Strikes por issue:** `project:v1:issue:{id}:strikes` — contagem de rejeições (Architect/QA/CyberSec). Script: [scripts/strikes.py](../scripts/strikes.py) (`increment`, `get`, `reset`). Ao 2º strike: evento `trigger_architect_fallback` no stream `orchestrator:events`. Ao 5º: incremento em `project:v1:orchestrator:five_strikes_count` e evento `issue_back_to_po`.
- **Aprovação por omissão cosmética:** Timer 6 h por issue em `project:v1:issue:{id}:cosmetic_timer_end`; arquivos em `project:v1:issue:{id}:cosmetic_timer_files`. Classificação determinística: [scripts/cosmetic_omission.py](../scripts/cosmetic_omission.py) (`is-cosmetic`, `start-timer`, `check-timers`). Registro em **MEMORY.md** e lista QA: [docs/agents-devs/MEMORY.md](../agents-devs/MEMORY.md), [docs/agents-devs/areas-for-qa-audit.md](../agents-devs/areas-for-qa-audit.md).
- **Orçamento de degradação:** `project:v1:orchestrator:five_strikes_count`, `project:v1:orchestrator:omission_cosmetic_count`, `project:v1:orchestrator:sprint_task_count`. Freio de mão: `orchestration:pause_degradation`. Loop de consenso: `project:v1:orchestrator:consensus_loop_in_progress`, `project:v1:orchestrator:consensus_pilot_result` (`success` | `fail`). Script para definir resultado do pilot: [scripts/set_consensus_pilot_result.py](../scripts/set_consensus_pilot_result.py).
- **Digest diário:** Stream `digest:daily`; script [scripts/digest_daily.py](../scripts/digest_daily.py) gera `docs/agents-devs/digest-YYYY-MM-DD.md`. Alertas imediatos (degradação, segurança, $5/dia) são enviados no momento pelo orquestrador/gateway, não pelo digest.

### Alertas e consumidores via Slack (Fase 3)

- **Stream `orchestrator:events`:** Eventos como `trigger_architect_fallback`, `issue_back_to_po`, `consensus_loop_requested` são publicados neste stream. Um **consumidor** ([scripts/consumer_orchestrator_events_slack.py](../scripts/consumer_orchestrator_events_slack.py)) lê o stream e envia cada evento ao Slack (canal de alertas do orquestrador — app e canal próprios).
- **Envio ao Slack (orquestrador):** [scripts/slack_notify.py](../scripts/slack_notify.py) com prefixo `ORCHESTRATOR_` — usa `ORCHESTRATOR_SLACK_WEBHOOK_URL` ou `ORCHESTRATOR_SLACK_BOT_TOKEN` + `ORCHESTRATOR_SLACK_ALERTS_CHANNEL_ID` no `.env`; no cluster o Secret `orchestrator-slack` injeta `SLACK_WEBHOOK_URL` / `SLACK_BOT_TOKEN` / `SLACK_ALERTS_CHANNEL_ID`. **Referência:** lista completa de variáveis de ambiente em [.env.example](../.env.example) (Slack por agente, Orquestrador, Telegram, Ollama).
- **Alerta imediato (freio de mão):** Quando o orquestrador aciona o freio de mão por orçamento de degradação, além de escrever o relatório ele **envia uma mensagem imediata** ao Slack (chamada direta a `slack_notify.py` com prefixo orquestrador).
- **Subfluxo do loop de consenso:** [scripts/consensus_loop_runner.py](../scripts/consensus_loop_runner.py) — quando `KEY_CONSENSUS_IN_PROGRESS` está setada, carrega o relatório de degradação, notifica Slack e define o resultado do pilot via [scripts/set_consensus_pilot_result.py](../scripts/set_consensus_pilot_result.py). Pode ser executado por CronJob (ex.: a cada 2 min) ou uma vez (`--once`).
- **Automação no cluster:** CronJobs e Deployments em [k8s/orchestrator/](../k8s/orchestrator/) — digest diário (18:00 UTC), check-timers cosmético (a cada 10 min), autonomia (orchestrator-autonomy), disjuntor (127), consumidor Slack, contingência acéfalo (124). Aplicar: `make orchestrator-configmap`, `make configmap-acefalo` (se usar contingência), criar Secret `orchestrator-slack`, depois `make orchestrator-apply` ou `make up`. Ver [k8s/orchestrator/README.md](../k8s/orchestrator/README.md).

### Runbook — Pipeline explícito e slot único (125)

- **Developer:** Único consumidor designado de "tarefa pronta para desenvolvimento"; adquire **GPU Lock**, codifica, publica em `code:ready` e libera o lock. Trigger: [developer_worker](k8s/development-team/developer/) ou equivalente que consome `task:backlog` e usa [gpu_lock](app/features/gpu_lock.py).
- **Revisão pós-Dev:** **Slot único** — um único consumidor (pod `revisao-pos-dev`) é acionado por `code:ready`; adquire o GPU Lock **uma vez** e executa em sequência Architect → QA → CyberSec → DBA (e opcionalmente UX) no mesmo modelo, sem liberar o lock entre etapas. Ver [estrategia-uso-hardware-gpu-cpu.md](../02-infra/estrategia-uso-hardware-gpu-cpu.md) e [k8s/development-team/revisao-pos-dev/](../k8s/development-team/revisao-pos-dev/).
- **Verificação:** Garantir que os ConfigMaps do pipeline (`developer-scripts`, `revisao-slot-scripts`) estão aplicados e que os deployments usam GPU Lock e respeitam `cluster:pause_consumption` (contingência 124 e kill switch).
