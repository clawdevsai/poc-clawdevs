# Contexto da conversa em canal compartilhado entre agentes

Mecanismo para **compartilhar o contexto da conversa** (ex. Slack) entre os agentes, já que cada agente tem sessão própria (`per-account-channel-peer`) e não enxerga automaticamente o que os outros disseram na mesma thread.

---

## Problema

No canal (ex. #all-clawdevsai) ou em uma thread, quando o CEO escreve e depois o PO é acordado por menção, o PO **não** recebe o histórico da thread na sessão dele — a sessão do PO só tem as mensagens dirigidas ao PO. Para o PO responder com contexto (saber o que o CEO pediu, o que o usuário disse), é preciso **compartilhar esse contexto** de forma explícita.

---

## Solução: arquivo de contexto compartilhado

Um único arquivo em memória compartilhada é lido e atualizado por **todos** os agentes que participam do mesmo canal/thread:

| Arquivo | Uso |
|--------|-----|
| `/workspace/shared/memory/conversa-canal-compartilhada.md` | Contexto da conversa atual no canal/thread. Cada agente **lê** antes de responder e **atualiza** após responder com o último intercâmbio (quem disse o quê). |

Assim, o próximo agente (ou o mesmo em outro turno) vê o que já foi dito e pode responder com continuidade.

---

## Regra para os agentes

1. **Antes de responder** em canal/thread compartilhado: ler `conversa-canal-compartilhada.md` para obter o contexto (últimas mensagens, quem pediu o quê, tema da discussão).
2. **Após responder**: atualizar esse arquivo com o **último intercâmbio** — por exemplo:
   - usuário / CEO / PO disse X;
   - você (agente Y) respondeu Z.
   - Manter resumo recente (últimas 1–2 trocas ou um parágrafo) para não inflar o arquivo.

A regra está em **MEMORY.md** de cada agente (soul) e, onde aplicável, em **AGENTS.md** do workspace (ex. CEO).

---

## Inicialização

O arquivo é criado pelo job de init de memória (`init-memory-configmap.yaml` + job que monta `/workspace`). Conteúdo inicial: cabeçalho explicando o uso e seção “Último contexto” vazia ou “Nenhum ainda”.

---

## Onde está configurado

- **Init:** `k8s/management-team/openclaw/init-memory-configmap.yaml` — criação de `conversa-canal-compartilhada.md` em `/workspace/shared/memory/`.
- **Soul (MEMORY.md):** todos os agentes (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA, Governance) — lista do arquivo + regra “ao participar de conversa em canal: ler e atualizar”.
- **Workspace CEO:** `workspace-ceo-configmap.yaml` (AGENTS.md) — seção “Contexto compartilhado em canal”.

---

## Limitações

- O contexto é **voluntário**: depende de cada agente escrever no arquivo após responder. Se um agente não atualizar, o próximo pode ter contexto desatualizado.
- Um único arquivo para **toda** a conversa: se houver vários canais/threads ao mesmo tempo, o conteúdo pode misturar-se (o arquivo funciona como “última conversa ativa”). Para múltiplas threads distintas no futuro, poderia existir um arquivo por thread (ex. `conversa-canal-{channel_id}-{thread_ts}.md`), o que exigiria que o gateway ou o agente soubesse channel/thread_ts — por ora fica um único arquivo.

---

## Referências

- [interacao-agentes-mensageria.md](../03-agents/agents-devs/interacao-agentes-mensageria.md) — conversa compartilhada no canal/thread, um agente por vez.
- Memória compartilhada: `k8s/management-team/openclaw/init-memory-configmap.yaml` (strategy, architecture, backlog, incidents, **conversa-canal-compartilhada**).
