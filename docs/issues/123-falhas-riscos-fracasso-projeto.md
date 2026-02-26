# [team-devs-ai] Falhas e riscos que podem levar ao fracasso do projeto

**Fase:** 1 — Governança / Operação  
**Labels:** risk, failure-mode, contingency

## Objetivo

Documentar falhas e riscos já identificados na documentação do projeto que, se não tratados, podem levar ao **fracasso operacional ou financeiro** do time de agentes. Cada item indica onde está a lacuna e o que falta para mitigar.

---

## 1. Cluster acéfalo quando CEO/PO estão na nuvem e a internet cai

**Onde está:** [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) — Riscos residuais, item (3). **Especificação completa:** [06-operacoes.md](../06-operacoes.md) (seção *Contingência: cluster acéfalo*). **Issue de implementação:** [124-contingencia-cluster-acefalo.md](124-contingencia-cluster-acefalo.md).

**Problema:** Se o CEO (e o PO) estiverem em nuvem e a internet cair, o cluster local deixa de receber `cmd:strategy` e novos comandos. O fluxo estratégico para; os agentes locais podem continuar consumindo backlog do Redis até acabar, mas **não há comando novo**. O plano de contingência **agora está especificado** na documentação.

**Solução especificada (resumo):**

- **Timeout configurável** (ex.: 5 min) sem comando com **tag de estratégia do CEO** no Redis → orquestrador considera nuvem inacessível.
- **Quem detecta:** orquestrador (ou componente de borda) monitora o Redis; **quem age:** DevOps local (já monitora hardware; detecção automática, sem LLM).
- **Ação automática:** DevOps **não** usa git stash; executa **commit do estado atual em branch efêmera de recuperação** (ex.: `recovery-failsafe-<timestamp>`); persiste estado da fila no **LanceDB**; **pausa** consumo da fila que disputa o lock de GPU.
- **Recuperação (retomada automática):** durante a pausa, orquestrador executa **health check contínuo** (ping em endpoints a cada 5 min, sem tokens); quando a conectividade estiver estável por **3 ciclos consecutivos**, orquestrador **acorda automaticamente** o DevOps e executa script de retomada (checkout limpo; se divergência ou conflitos, Architect prioridade zero resolve na branch de recuperação; restaura fila e retoma consumo). **Nenhum comando humano** para destravar; orquestrador envia **notificação assíncrona** (Telegram/Slack ou digest) ao Diretor com tempo de inatividade e confirmação de retomada bem-sucedida.

**Critérios de aceite (para a issue 124):** Implementar heartbeat/detecção no Redis, ação do DevOps (commit em branch efêmera + persistência LanceDB + pausa), **health check contínuo** durante a pausa, **retomada automática** (3 ciclos estáveis, checkout limpo + Architect para conflitos) e notificação assíncrona ao Diretor; timeout configurável (env ou config JSON).

---

## 2. CEO como único ponto de comando estratégico — custo e gargalo

**Onde está:** [01-visao-e-proposta.md](../01-visao-e-proposta.md), [02-agentes.md](../02-agentes.md) (seção CEO).

**Problema:** O CEO é o **único** que publica `cmd:strategy` e filtra o que vai ao PO. Se o CEO **não filtrar** ideias e tarefas (ou for mal configurado/promptado), "cada tarefa ou ideia enviada ao time consome orçamento de API" e o sistema entra em **colapso financeiro**. A mitigação é comportamental (prompt, constraint), **não** determinística na infraestrutura.

**Falha possível:** Estouro do freio de gastos ($5/dia) por excesso de chamadas CEO→PO ou por tarefas demais geradas a partir de visão ampla; paralisia prematura por custo, não por valor entregue.

**O que falta / já especificado:**

- **Fitness no raciocínio do CEO (issue 129):** CEO deve gerar **VFM_CEO_score.json** e descartar internamente eventos com threshold negativo **antes** de enviar ao Gateway; previne desperdício na raiz cognitiva. Ver [soul/CEO.md](../soul/CEO.md), [13-habilidades-proativas.md](../13-habilidades-proativas.md).
- **Controle na borda:** Limite de eventos `cmd:strategy` por período (ex.: por dia ou por sessão) no orquestrador ou no Gateway (token bucket — issue 126), além do freio de $5/dia.
- **Métrica de filtragem:** Medir razão "ideias/tarefas enviadas pelo CEO" vs "tarefas efetivamente priorizadas no backlog" para detectar CEO que não filtra (degradação por eficiência — issue 126; alertar no digest ou pausar se passar threshold).

**Critérios de aceite sugeridos:**

- Regra no Gateway ou orquestrador: máximo de N eventos `cmd:strategy` por janela configurável (com documentação em [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md)).
- (Opcional) Métrica e alerta quando a taxa de "tarefas geradas vs tarefas filtradas" indicar risco de custo; documentar em FinOps.

---

## 3. PO e alucinação de escopo (RAG desatualizado ou falha)

**Onde está:** [02-agentes.md](../02-agentes.md) (PO — "Onde pode falhar"), [03-arquitetura.md](../03-arquitetura.md) (ciclo de rascunho).

**Problema:** Se o RAG falhar ou trouxer documentação **desatualizada**, o PO pode criar tarefas **tecnicamente impossíveis** na base atual. O ciclo de rascunho (draft → Architect valida → draft_rejected) mitiga, mas se o Architect aprovar um draft com base em contexto incompleto ou se o RAG envenenar várias tarefas seguidas, o time gasta recursos até travar em tarefas impossíveis.

**Falha possível:** Muitas issues em draft_rejected em loop ou muitas tarefas chegando ao Developer que o Architect depois barra; desperdício de GPU e tempo; orçamento de degradação (10–15%) pode ser atingido por causa de escopo mal definido, não por impasse de código.

**O que falta:**

- **Sinal de saúde do RAG:** Métrica ou checklist (ex.: data da última atualização da doc indexada, cobertura dos arquivos críticos). Alertar no digest se RAG estiver desatualizado.
- **Escalação de draft_rejected:** Se o mesmo tipo de rejeição (ex.: "impossível na arquitetura atual") se repetir mais de K vezes no sprint, orquestrador pode escalar ao Diretor ou ao CEO (revisão de escopo ou de documentação), em vez de deixar o PO e o Architect em loop.

**Critérios de aceite sugeridos:**

- Documentar em [02-agentes.md](../02-agentes.md) ou [06-operacoes.md](../06-operacoes.md): condição em que excesso de draft_rejected dispara escalação (CEO/Diretor) ou pausa para revisão de doc/escopo.
- (Opcional) Métrica de "draft_rejected por causa raiz" e limiar de alerta.

---

## 4. Validação reversa PO pós-sumarização — origem dos critérios de aceite

**Onde está:** [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Validação reversa (PO), **Segregação dos critérios de aceite**), [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) (Onde ficam os critérios de aceite), [12-ferramenta-summarize.md](../12-ferramenta-summarize.md). **Issue de implementação:** [041-truncamento-contexto-finops.md](041-truncamento-contexto-finops.md).

**Problema:** Após o pre-flight Summarize, o **PO deve comparar o resumo gerado com os critérios de aceite originais** das tarefas. Se os critérios estiverem **no mesmo buffer que foi sumarizado**, o PO recebe só o resumo e **perde a referência imutável** — não consegue rejeitar o truncamento de forma confiável.

**Solução especificada (resumo):**

- **Segregação obrigatória:** Critérios de aceite **não** entram no bloco sumarizado. Duas opções: **(A) Tag de proteção:** critérios com tag especial no Markdown (ex.: `<!-- CRITERIOS_ACEITE -->`); script de limpeza do DevOps com **regex** para **ignorar** blocos dentro dessa tag; sumarizador não processa esses blocos. **(B) Payload duplo:** orquestrador armazena critérios em **arquivo separado** (ex.: SESSION-STATE.md ou session.md por issue) e envia à nuvem **resumo + critérios intactos**; PO recebe os dois e faz validação reversa.
- Documentação em 07, 28 e 12 atualizada com onde ficam os critérios e como o PO os acessa.

**Critérios de aceite (para a issue 041):** Pipeline explicita que critérios de aceite ficam em tag protegida (regex no script DevOps) ou em arquivo separado (payload duplo); PO sempre recebe resumo + critérios intactos.

---

## 5. Orçamento de degradação — recalibragem sem workflow definido

**Onde está:** [06-operacoes.md](../06-operacoes.md) (Orçamento de degradação, **Workflow de recuperação pós-degradação**), [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md). **Issue de implementação:** [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md) (e/ou issue de operações).

**Problema:** Quando mais de 10–15% das tarefas do sprint caem em 5º strike ou aprovação por omissão cosmética, a esteira é pausada até "recalibragem". O **workflow de recuperação** agora está definido na documentação.

**Solução especificada (resumo):**

- **Pré-freio de mão:** Ao atingir 10–15%, orquestrador primeiro aciona **loop de consenso automatizado** (QA + Architect propõem ajuste temporário, testam em uma tarefa crítica). Só se o loop **falhar** (ou não for aplicável) a esteira é pausada.
- **Responsável (após pausa):** **Diretor humano** (recalibragem e comando de desbloqueio).
- **Ao pausar:** Orquestrador **gera automaticamente** **relatório de degradação** (Markdown no repositório): sumário de issues falhadas, trechos de impasse, histórico de prompts, erro mastigado para o humano.
- **Checklist antes de reativar:** Diretor revisa MEMORY.md e relatório; ajusta limiares/critérios no config (JSON do Gateway ou dos agentes).
- **Retomada:** **Comando explícito de desbloqueio** (ex.: script `./scripts/unblock-degradation.sh` ou CLI) — **somente** após o Diretor executar esse comando os agentes voltam a consumir o Redis. Nenhum script ou agente pode reativar por conta própria.

**Critérios de aceite (para a issue 017 ou operações):** Orquestrador gera relatório de degradação ao pausar; comando de terminal/CLI de desbloqueio implementado; documentação em 06 e 07 reflete o workflow.

---

## 6. Skill loop e context overload — mitigação genérica

**Onde está:** [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Riscos de configuração).

**Problema:** Dois riscos citados: (1) **Context overload** — "memória infinita em todos os agentes pode esgotar 32 GB de RAM em minutos"; (2) **Skill loop** — "agente em loop chamando Skill (ex.: Google); usar timeout ou Max_Calls por tarefa". A mitigação é genérica ("usar timeout ou Max_Calls"); **não** está definido na arquitetura onde esses limites são aplicados (Gateway? orquestrador? OpenClaw config?) nem valores recomendados.

**Falha possível:** OOM ou travamento por contexto; ou consumo infinito de API/custo por skill em loop, até freio de $5/dia (paralisia).

**O que falta:**

- **Skill loop:** Definir em qual camada se aplica Max_Calls/timeout por tarefa (ex.: OpenClaw, orquestrador); documentar em [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) ou [04-infraestrutura.md](../04-infraestrutura.md); valor padrão sugerido (ex.: N calls por skill por tarefa).
- **Context overload:** Reforçar que os limites de memória (janela deslizante, TTL Redis, max tokens no Gateway) já documentados são a mitigação principal; deixar explícito que "memória infinita" é anti-padrão e que config padrão deve ter limites (referência a 07 e 28).

**Critérios de aceite sugeridos:**

- Documentar onde e como aplicar Max_Calls/timeout por skill por tarefa; valor padrão ou range recomendado.
- Uma linha em 07 ou 04: config de memória sem limites explícitos é anti-padrão; referência aos limites já descritos.

---

## 7. Resumo executivo para o Diretor


| #   | Risco                                                  | Impacto | Status / Lacuna principal                                                | Doc principal / Issue   |
| --- | ------------------------------------------------------ | ------- | ----------------------------------------------------------------------- | ----------------------- |
| 1   | Cluster acéfalo (CEO/nuvem + internet cai)             | Alto    | **Especificado:** heartbeat Redis, commit em branch efêmera de recuperação, LanceDB, **retomada automática** (health check 5 min, 3 ciclos estáveis, checkout limpo + Architect para conflitos), notificação assíncrona ao Diretor; sem comando humano | 06-operacoes, 124       |
| 2   | CEO não filtra → custo estoura                         | Alto    | Sem limite determinístico de cmd:strategy; só freio $/dia               | 01, 02, 07              |
| 3   | PO alucinação de escopo (RAG)                          | Médio   | Sem escalação de draft_rejected em loop                                 | 02, 03, 06              |
| 4   | PO não consegue validar resumo (critérios sumarizados) | Médio   | **Especificado:** tag de proteção ou payload duplo; PO recebe critérios intactos | 07, 28, 041             |
| 5   | Recalibragem pós-degradação indefinida                 | Médio   | **Especificado:** relatório auto, checklist Diretor, comando explícito de desbloqueio | 06, 07, 017             |
| 6   | Skill loop / context overload                          | Médio   | Timeout/Max_Calls e anti-padrão de memória não definidos na arquitetura | 07, 04                  |


Prioridade sugerida para não deixar o projeto fracassar: **1 (contingência CEO/nuvem)** — issue 124 — e **2 (limite de cmd:strategy / filtragem)**; em seguida 4 (041) e 5 (017); depois 3 e 6.

---

## Referências

- [01-visao-e-proposta.md](../01-visao-e-proposta.md)
- [02-agentes.md](../02-agentes.md)
- [03-arquitetura.md](../03-arquitetura.md)
- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md)
- [06-operacoes.md](../06-operacoes.md)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md)
- [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md)

