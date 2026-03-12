# ClawDevsAI - Validacao do Fluxo e Ajustes

## Objetivo
Este documento valida o que ja esta pronto no sistema multiagente `clawdevs-ai` e define ajustes para fechar o fluxo desejado (CEO, PM/PO, Architect, Developer, QA, DevOps, DBA, CyberSec).

## Status Atual (baseado no codigo)

### Fluxo implementado hoje
`Diretor (UI/Telegram) -> cmd:strategy -> PO -> draft.2.issue -> Architect -> task:backlog -> Developer -> code:ready -> pr:review -> QA + DBA + CyberSec -> consenso (approve => event:devops | blocked => task:backlog) -> (>=6 rounds => Architect-review) -> DevOps`

### Agentes ativos no runtime
- PO
- Architect-draft
- Developer
- QA
- DBA
- CyberSec
- Architect-review (escalonamento de decisao final)
- DevOps
- Interface Telegram (CEO conversacional para diretor)
- Orquestrador de governanca (strikes/degradacao/invalid output)

### Canais/integrações ativos
- Redis Streams: `cmd:strategy`, `draft.2.issue`, `task:backlog`, `code:ready`, `pr:review`, `event:devops`, `orchestrator:events`
- Dashboard operacional: `http://localhost:3000/`
- GitHub API (leitura de PRs no dashboard e no Telegram)

## Validacao do Fluxo Desejado (1..17)

| Etapa desejada | Status | Evidencia |
|---|---|---|
| 1. CEO pesquisa e documenta demanda | **Parcial** | `telegram_director` gera resposta de CEO e pode fazer busca web, mas nao persiste documento formal de estrategia por item de forma obrigatoria |
| 2. CEO envia para PM/PO | **Implementado** | Publicacao em `cmd:strategy` |
| 3. PM/PO cria User Stories | **Parcial** | PO recebe diretriz e pode decompor via OpenClaw, mas nao existe contrato explicito "user story" versionado no backend |
| 4. PM/PO envia User Stories para Architect | **Implementado** | Publicacao em `draft.2.issue` |
| 5. Architect gera tasks/issues por User Story | **Implementado** | Architect-draft aprova/rejeita e publica backlog |
| 6. Issues em repo + dashboard simultaneamente | **Parcial** | Dashboard ve estado no Redis; criacao no issue tracker depende da execucao do PO/skills no OpenClaw e configuracao GitHub |
| 7. Developer inicia desenvolvimento | **Implementado** | Consumo de `task:backlog` |
| 8. Developer so inicia nova task apos merge da anterior | **Implementado (v1)** | Gate por `project:v1:developer:{id}:active_issue` e `project:v1:issue:{id}:pr_merged` no `DeveloperAgent` |
| 9. Developer cria PR | **Parcial** | Processo esperado no agente, sem enforce hard no backend |
| 10. PR aciona QA/DevOps/Architect/DBA/CyberSec | **Parcial** | QA, DBA e CyberSec foram ligados ao stream `pr:review`; Architect-review atua no escalonamento e DevOps segue no pos-merge |
| 11. Agentes revisam e comentam | **Implementado (v2)** | QA/DBA/CyberSec revisam em `pr:review`, consenso fecha rodada e publica comentarios na PR quando `GITHUB_TOKEN`/`repo`/`pr` estao configurados |
| 12. Developer corrige feedbacks | **Parcial** | Atualizacao de PR pode republicar `code:ready` e gerar nova rodada em `pr:review` |
| 13. Nova rodada apos update de PR | **Implementado (v1)** | Cada novo `publish_code_ready` incrementa rodada em `project:v1:issue:{id}:pr_review_round` |
| 14. Limite de 5 rodadas | **Implementado (v1)** | Acima de 5 emite `architect_final_decision_required` em `orchestrator:events` |
| 15. Apos 5 rodadas Architect decide merge | **Parcial** | Escalada para `Architect-review` foi implementada; merge automatico ainda depende da acao do agente |
| 16. Architect libera proxima task apos merge | **Implementado (v1)** | `publish_deploy_event` marca merge e libera lock de issue ativa por developer |
| 17. Architect prioriza ordem de tasks | **Parcial** | Prioridade no payload existe, mas sem fila priorizada forte e politicas de ordenacao centralizadas por Architect |

## Ajustes aplicados nesta revisao
- Correção da documentacao de fluxo no `README.md` para explicitar a entrada do Diretor (UI/Telegram).
- Correção do fluxo no `app/README.md` para refletir a etapa `code:ready -> QA` antes de `event:devops`.
- Criação desta validacao formal para guiar implementacao incremental sem divergencia entre "fluxo desejado" e "codigo vivo".

## Proxima evolucao recomendada (prioridade alta)

1. Consolidar status final de PR no merge gate
- Comentarios de reviewers e consenso na PR ja estao implementados.
- Proximo passo: validar estado `merged` via GitHub API antes da liberacao final de proxima task.

2. Adicionar agentes de revisao faltantes
- Novos papeis: `Architect-review`, `DBA`, `CyberSec`.
- Cada agente retorna `approve|request_changes` com razao objetiva.

3. Consolidar rodada por PR (nao apenas por issue)
- Estado atual: `project:v1:issue:{id}:pr_review_round`.
- Proximo passo: indexar por PR quando `pr` estiver presente para suportar multiplas PRs da mesma issue.

4. Endurecer gate de sequenciamento do Developer por merge
- Estado atual: gate funcional por issue ativa/merge.
- Proximo passo: validar tambem status da PR no GitHub antes da liberacao.

5. Integração dupla obrigatoria de issue
- Validacao transacional/logica:
  - issue criada no tracker (GitHub)
  - issue refletida no Redis/dashboard
- Se um lado falhar, emitir `issue_sync_failed` e manter em `Refinamento`.

## Regra operacional consolidada (estado alvo)
- Uma issue ativa por Developer.
- Nenhuma nova issue sem merge da anterior.
- Revisao obrigatoria por QA, DevOps, Architect-review, DBA e CyberSec.
- Maximo de 5 rodadas de revisao por PR.
- Architect tem decisao final no limite da quinta rodada.
