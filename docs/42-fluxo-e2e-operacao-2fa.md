# Fluxo E2E: Operação 2FA (016)

Cenário end-to-end do ClawDevs: **"Implementar login com autenticação de dois fatores (2FA) via e-mail"**. Do pedido do Diretor até a notificação de conclusão, passando por CEO → PO → backlog → validação de rascunho → Developer → revisão (Architect, CyberSec, DBA) → QA/UX → CEO. Complementa [08-exemplo-de-fluxo.md](08-exemplo-de-fluxo.md) com fases alinhadas aos critérios da issue 016.

## Cenário

O Diretor pede: *"Quero implementar um sistema de login com autenticação de dois fatores (2FA) via e-mail."*

---

## Fases (critérios 016)

### 1. Planejamento (CEO, PO — nuvem)

- **CEO:** Recebe a ordem (Telegram), pesquisa melhores práticas de 2FA, define diretriz (ex.: tokens temporários TOTP, segurança máxima, baixo custo). Publica no Redis em **cmd:strategy** (tag de estratégia).
- **PO:** Lê a diretriz, cria Issues no GitHub (ex.: #1 Schema do banco, #2 Lógica de envio de e-mail, #3 Interface de verificação). Publica prioridade no Redis (**task:backlog**). Não altera requisitos em desenvolvimento exceto **technical_blocker**.

**Redis:** `cmd:strategy`, `task:backlog`; chaves de estado (ex.: `project:v1:issue:id`). Contrato de publicação e campos mínimos: [38-redis-streams-estado-global.md](38-redis-streams-estado-global.md) (§2). Para testes: [scripts/publish_event_redis.py](../scripts/publish_event_redis.py) (issue 018).

### 2. Validação de rascunho (PO → Architect)

- **PO** publica rascunho em **draft.2.issue** (conteúdo das Issues para validação técnica).
- **Architect** avalia viabilidade (diffs, ADRs, padrões). Emite **draft_rejected** ou aprova. Só após aprovação a tarefa vai para desenvolvimento. **Technical_blocker** formalizado pelo Architect permite exceção de mudança de escopo pelo PO.

**Redis:** `draft.2.issue`, `draft_rejected`; aprovação → tarefa liberada para DevOps/Developer.

### 3. Preparação (DevOps)

- **DevOps:** Cria branch (ex.: `feature/2fa-auth`), verifica hardware (65%), dispara **GPU Lock** (TTL dinâmico) para reservar VRAM. Publica evento ou atualiza estado para o Developer consumir.

**Redis:** Estado da branch; GPU Lock via script [scripts/gpu_lock.py](../scripts/gpu_lock.py).

### 4. Execução (Developer)

- **Developer:** Obtém GPU Lock, recebe contexto das Issues (RAG/Redis). Implementa em OpenCode (código, modelos de banco, lógica do token). Commit na branch; libera GPU. Publica **code:ready** no Redis.

**Redis:** `code:ready` (stream consumido pelo slot único Revisão pós-Dev — 125).

### 5. Revisão (slot único: Architect → QA → CyberSec → DBA)

- Um consumidor (job Revisão pós-Dev) adquire GPU Lock uma vez e executa em sequência: **Architect** (code review, só diffs do PR), **QA** (testes), **CyberSec** (segurança, TTL do token), **DBA** (schema, queries, índices). Cada um aprova ou devolve ao Developer. Architect não reescreve código; instrui. CyberSec barra ausência de TTL; DBA barra migrations/queries fora do padrão ou sem índice onde necessário.

**Redis:** `code:ready` consumido; XACK após conclusão. Ver [39-consumer-groups-pipeline-revisao.md](39-consumer-groups-pipeline-revisao.md).

### 6. Validação (QA, UX)

- **QA:** Testes automatizados no sandbox; bloqueia merge em falhas críticas. Não conserta bugs; cria Issues.
- **UX:** Revisão de frontend (acessibilidade, foco automático no campo 2FA, etc.). Não sugere mudanças pesadas sem Architect.

### 7. Fechamento (CEO)

- **CEO:** Recebe relatório final via Redis. Notifica o Diretor no Telegram (ex.: "2FA pronto na branch main. Custo: $X e Y minutos. Deploy para staging?").

---

## Eventos e estado (Redis)

| Stream / chave | Uso |
|----------------|-----|
| `cmd:strategy` | Diretriz do CEO (tag de estratégia; heartbeat para contingência 124). |
| `task:backlog` | Priorização e tarefas do PO. |
| `draft.2.issue` | Rascunho para Architect validar. |
| `draft_rejected` | Rejeição do Architect (ciclo até aprovação). |
| `code:ready` | Código pronto para revisão (consumido pelo slot único). |
| `project:v1:issue:id` | Estado por issue (ex.: status, critérios de aceite). |

---

## Pontos de risco (016)

- **Loop Architect / Developer:** Se discussão infinita, DevOps pode cortar por tempo de GPU (TTL) ou escalar ao Diretor (five strikes).
- **CyberSec:** Barra ausência de TTL no token 2FA; exige correção antes do merge.
- **DBA:** Barra merge se migrations/queries violarem normas ou comprometerem performance (ex.: falta de índice na coluna de expiração do token → full scan).
- **Mudança de escopo em tarefa em desenvolvimento:** **Proibida** exceto **technical_blocker** formalizado pelo Architect. Caso contrário: timing loop, nada entregue (regra PO).
- **Alucinação de escopo (PO):** RAG pode falhar; ciclo draft.2.issue → Architect reduz risco de tarefas impossíveis na base atual.

Referências: [02-agentes.md](02-agentes.md), [03-arquitetura.md](03-arquitetura.md), [06-operacoes.md](06-operacoes.md), [docs/issues/016-exemplo-fluxo-operacao-2fa.md](issues/016-exemplo-fluxo-operacao-2fa.md).
