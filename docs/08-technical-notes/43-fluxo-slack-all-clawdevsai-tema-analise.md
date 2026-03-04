# Fluxo Slack #all-clawdevsai: tema para análise

Este documento descreve o fluxo em que o **Diretor** coloca um **tema para analisar** no canal **#all-clawdevsai** no Slack; os **agentes** discutem **um por vez**, cada um na sua especialidade, até o **PO** e o **CEO** decidirem; o **CEO** pergunta ao Diretor se ele inicia/aprova a tarefa; em seguida o fluxo normal (já documentado) segue.

## Onde acontece

- **Canal:** `#all-clawdevsai` no Slack (ClawDevsAI).
- **Quem inicia:** Diretor (humano) postando no canal um tema ou pergunta para análise.
- **Quem participa:** Todos os agentes (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA), **um por vez**, na ordem definida abaixo.

## Passo a passo (pelo Slack)

1. **Diretor** escreve no **#all-clawdevsai** o tema a analisar (ex.: *“Quero analisar: migrar o módulo X para Kubernetes”* ou *“Tema: como reduzir custo de API em nuvem”*). Pode mencionar o app (@ClawdevsAI) para garantir que o gateway processe.
2. **CEO** (ou o agente que receber a mensagem no canal) reconhece que é um **tema para análise** vindo do Diretor e inicia a **rodada de opiniões**.
3. **Rodada — um agente por vez**, na ordem abaixo, cada um dando a **sua opinião na sua especialidade** (em mensagens no mesmo canal/thread):
   - DevOps/SRE (infra, CI/CD, custo infra)
   - Architect (viabilidade técnica, governança)
   - Developer (esforço de implementação)
   - QA (testes, qualidade)
   - CyberSec (segurança, conformidade)
   - UX (experiência do usuário, se couber)
   - DBA (dados, queries, se couber)
   - PO (backlog, priorização, valor)
   - CEO (estratégia, custo-benefício, resumo)
4. **PO e CEO** sintetizam e **decidem** a recomendação (ex.: “fazer em fases”, “não fazer agora”, “fazer com escopo X”).
5. **CEO** pergunta ao **Diretor** no canal: *“Aprovamos fazer [resumo]. Quer que eu inicie essa tarefa?”* (ou equivalente).
6. **Diretor** responde no Slack (ex.: *“Sim, pode iniciar”*).
7. A partir daí o **fluxo normal** segue (CEO/PO/backlog/issues/desenvolvimento conforme [02-agentes.md](02-agentes.md), [06-operacoes.md](06-operacoes.md) e documentação do OpenClaw).

## Configuração técnica

- O canal **#all-clawdevsai** está na allowlist do Slack no OpenClaw (`channels.slack.groupPolicy: allowlist`, `channels.slack.channels.<ID>`). O ID do canal é configurável: **`OPENCLAW_SLACK_ALL_CLAWDEVSAI_CHANNEL_ID`** (ou `SLACK_ALL_CLAWDEVSAI_CHANNEL_ID`) no `.env` — ver [.env.example](../.env.example); no cluster o script `k8s-openclaw-secret-from-env.sh` grava no Secret; padrão: `C0AHSCLSQKC` (#all-clawdevsai).
- O app **ClawdevsAI** deve estar **adicionado ao canal** (Integrações → Adicionar apps → ClawdevsAI).
- O **Diretor** deve estar na allowlist de DM (`SLACK_DIRECTOR_USER_ID` ou `SLACK_ALLOWED_USER_IDS`) para que mensagens no canal sejam autorizadas, conforme política do gateway.
- Discussões entre agentes no Slack usam **Ollama (LLM local GPU)** conforme política do projeto.

## Referências

- [openclaw-config-ref.md](openclaw-config-ref.md) — Config OpenClaw (tudo no K8s); uso com Slack.
- [docs/openclaw-sub-agents-architecture.md](openclaw-sub-agents-architecture.md) — Sub-agents e roteamento.
- [02-agentes.md](02-agentes.md) — Definição dos agentes.
- [OpenClaw — Slack](https://docs.openclaw.ai/channels/slack) — Canal Slack no OpenClaw.
