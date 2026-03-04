# Self-Improvement dos Agentes

Captura de learnings, erros e correções para melhoria contínua do **ClawDevs** (enxame). Integração com o workspace do OpenClaw (AGENTS.md, SOUL.md, TOOLS.md) e promoção de descobertas para memória de longo prazo. Comportamento **proativo e persistente** (WAL, Working Buffer, recuperação pós-compactação) e guardrails de evolução (ADL/VFM) — detalhes em [13-habilidades-proativas.md](13-habilidades-proativas.md). O sistema de **memória em seis camadas** (Hot RAM, Warm Store, Cold Store, arquivo curado, cloud opcional, autoextração opcional) e a higiene de memória estão consolidados em [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md). O mesmo documento inclui a **configuração prática** (memorySearch na config, estrutura MEMORY.md e memory/, diários, recall em AGENTS.md e troubleshooting). Decisões que viram **microADR** (Architect, ao aprovar PR) ou **invariantes de negócio** (tag no estado da sessão) **não** entram no funil de resumo — ficam imutáveis na memória vetorial ou protegidas por regex no script de limpeza; ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (seção 2.3).

---

## Visão geral

Os agentes (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA) operam em sessões com contexto injetado pelo OpenClaw. Para que o sistema **aprenda** com falhas, correções do Diretor e descobertas técnicas, usa-se um fluxo de **self-improvement**: registrar em `.learnings/` e, quando aplicável, **promover** para os arquivos de workspace que alimentam as próximas sessões. Além disso, os agentes adotam **resourcefulness** (tentar várias abordagens antes de desistir) e **verificação antes de reportar** (não dizer "pronto" sem testar o resultado).

---

## Estrutura do workspace (OpenClaw)

O OpenClaw injeta estes arquivos em toda sessão:

```
~/.openclaw/workspace/
├── AGENTS.md          # Fluxos multiagente, delegação, handoff
├── SOUL.md            # Diretrizes comportamentais, tom, princípios (alinhado a soul/)
├── TOOLS.md           # Capacidades de ferramentas, gotchas de integração
├── MEMORY.md          # Memória de longo prazo (sessão principal)
├── SESSION-STATE.md  # Estado ativo da tarefa/sessão (alvo do protocolo WAL)
├── memory/            # Memória diária e zona de perigo
│   ├── YYYY-MM-DD.md
│   └── working-buffer.md   # Log entre 60% contexto e compactação (recuperação)
└── .learnings/        # Logs do self-improvement
    ├── LEARNINGS.md   # Correções, lacunas de conhecimento, melhores práticas
    ├── ERRORS.md      # Falhas de comando, exceções, timeouts
    └── FEATURE_REQUESTS.md  # Capacidades solicitadas pelo usuário
```

Criar o diretório e os arquivos de log:

```bash
mkdir -p ~/.openclaw/workspace/.learnings
# Criar LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md (cabeçalho + ---)
```

---

## Quando registrar

| Situação | Arquivo | Categoria / nota |
|----------|---------|-------------------|
| Comando ou operação falha | `.learnings/ERRORS.md` | Incluir comando, saída de erro, contexto |
| Diretor/usuário corrige o agente | `.learnings/LEARNINGS.md` | `category: correction` |
| Usuário pede capacidade inexistente | `.learnings/FEATURE_REQUESTS.md` | Contexto e complexidade estimada; se recorrente, considerar criar skill — ver [29-criacao-de-skills.md](29-criacao-de-skills.md) |
| API ou ferramenta externa falha | `.learnings/ERRORS.md` | Detalhes de integração |
| Conhecimento desatualizado ou incorreto | `.learnings/LEARNINGS.md` | `category: knowledge_gap` |
| Descoberta de abordagem melhor | `.learnings/LEARNINGS.md` | `category: best_practice` |

**Revisar** `.learnings/` antes de tarefas maiores e ao concluir features.

---

## Formato dos registros

### ID

`TIPO-AAAAMMDD-XXX`: `LRN` (learning), `ERR` (error), `FEAT` (feature); data; sequencial (ex.: `001`, `A7B`).

### Entrada em LEARNINGS.md

- **Logged**, **Priority** (low | medium | high | critical), **Status** (pending | resolved | promoted), **Area** (frontend | backend | infra | tests | docs | config).
- **Summary** (uma linha), **Details**, **Suggested Action**, **Metadata** (Source, Related Files, Tags, See Also, Pattern-Key quando for padrão recorrente).

### Entrada em ERRORS.md

- **Summary**, **Error** (bloco com saída real), **Context** (comando, parâmetros, ambiente), **Suggested Fix**, **Metadata** (Reproducible, Related Files, See Also).

### Entrada em FEATURE_REQUESTS.md

- **Requested Capability**, **User Context**, **Complexity Estimate** (simple | medium | complex), **Suggested Implementation**, **Metadata**.

Ao resolver: alterar **Status** para `resolved` e adicionar bloco **Resolution** (Resolved, Commit/PR, Notes).

---

## Promoção para memória do workspace (curadoria centralizada)

**Risco:** Nove agentes trabalhando em paralelo podem registrar aprendizados contraditórios (ex.: Developer registra "abordagem X" como sucesso; CyberSec marca a mesma abordagem como vulnerabilidade). Promoção orgânica e distribuída por cada agente para SOUL.md/AGENTS.md/TOOLS.md levaria a **conflitos lógicos**, **amnésia seletiva** ou **corrupção do arquivo de identidade central** — o enxame viraria um cabo de guerra de instruções conflitantes.

**Regra:** Nenhum agente promove diretamente para os arquivos globais (SOUL.md, AGENTS.md, TOOLS.md). A promoção é um **processo formal de merge request**, com **validação cruzada** e **curadoria por um agente com autoridade superior**, em **sessão isolada** (não nas filas do Redis do dia a dia).

### Protocolo de consenso de aprendizado (pre-flight)

Antes de qualquer item em `.learnings/` ser elegível para o curador, ele passa por um **filtro sanitário** na máquina local:

1. **Sumarização prévia (pre-flight):** O orquestrador submete o novo learning a uma avaliação rápida de impacto.
2. **Agentes guardiões:** QA (qualidade) e CyberSec (segurança) rodam **teste rápido** sobre o conteúdo proposto — não para debater elegância, mas para **garantir que o aprendizado não viole** diretrizes cruciais do projeto (ex.: regras OWASP, limites de CPU/performance definidos pelo Diretor).
3. Itens que falharem nesse filtro **não** entram na fila de processamento do curador; a entrada permanece em `.learnings/` com status `pending` ou `rejected_preflight`.

### Curadoria em sessão isolada (merge de conhecimento)

1. **Gatilho:** Evento de **merge de conhecimento** acionado por **CronJob** (ex.: execução em janela isolada, similar a jobs de atualização de ambiente em madrugada).
2. **Sessão isolada:** A curadoria roda em **seção de execução totalmente isolada** — não consome as filas do Redis onde o desenvolvimento do dia a dia ocorre; protege a operação principal.
3. **Agente curador:** O **Architect** (ou, conforme peso da decisão, o **CyberSec**) é o único responsável nessa sessão: lê todo o diretório `.learnings/` com itens ainda não processados, **analisa discrepâncias**, usa o **contexto arquitetural de alto nível** para **resolver contradições lógicas** ativamente e produz um **único artefato consolidado** (JSON ou Markdown limpo).
4. **Injeção segura:** O arquivo consolidado é então **injetado de forma segura** na identidade global (SOUL.md, AGENTS.md ou TOOLS.md conforme tipo de conteúdo). As entradas em `.learnings/` são atualizadas: `Status: promoted`, campo `Promoted: <arquivo>`.

| Tipo de conteúdo | Destino no artefato consolidado | Exemplo |
|------------------|----------------------------------|--------|
| Padrões comportamentais / tom | SOUL.md | "Ser conciso; evitar disclaimers desnecessários" |
| Melhorias de fluxo / delegação | AGENTS.md | "Usar sub-agentes para tarefas longas; sessions_send para handoff" |
| Gotchas de ferramentas | TOOLS.md | "Git push exige auth configurada; checar com gh auth status" |

Os SOULs por agente em [soul/](soul/) são a base dos system prompts; o `SOUL.md` do workspace complementa com diretrizes gerais de comportamento aplicáveis a todos. Detalhes de orquestração (CronJob, isolamento) em [03-arquitetura.md](03-arquitetura.md) (Merge de conhecimento).

**Diferença em relação ao Governance Proposer:** A curadoria acima (Architect/CyberSec) **injeta** learnings em SOUL.md/AGENTS.md/TOOLS.md do **workspace** em sessão isolada. O **Governance Proposer** atua sobre um **repositório Git dedicado** (rules, soul, skills, task e configs): propõe alterações via **PR** para o **Diretor** aprovar e fazer merge no GitHub; **após o merge**, o próprio agente faz pull da main e aplica/sincroniza as modificações no workspace. Assim, mudanças de governança passam por validação humana obrigatória no PR. Ver [35-governance-proposer.md](35-governance-proposer.md).

---

## Comunicação entre sessões (OpenClaw)

Ferramentas para compartilhar learnings entre sessões/agentes:

- **sessions_list** — Listar sessões ativas/recentes.
- **sessions_history** — Ler transcript de outra sessão.
- **sessions_send** — Enviar mensagem (ex.: learning) para outra sessão.
- **sessions_spawn** — Criar sub-agente para tarefa em background.

Útil para CEO/PO repassar contexto ao Developer, ou DevOps registrar incidente acessível aos demais.

---

## Hook opcional (OpenClaw)

Para lembrete automático no bootstrap do agente:

```bash
# Copiar hook para o OpenClaw
cp -r <skill>/hooks/openclaw ~/.openclaw/hooks/self-improvement
openclaw hooks enable self-improvement
```

O hook dispara em `agent:bootstrap` (antes da injeção dos arquivos do workspace) e adiciona um bloco de lembrete para avaliar e registrar learnings.

Eventos disponíveis (referência): `agent:bootstrap`, `command:new`, `command:reset`, `command:stop`, `gateway:startup`.

---

## Prioridade e áreas

| Prioridade | Uso |
|------------|-----|
| critical | Bloqueia funcionalidade central, risco de perda de dados ou segurança |
| high | Impacto relevante, fluxos comuns, problema recorrente |
| medium | Impacto moderado, workaround existe |
| low | Inconveniente menor, edge case |

**Areas:** `frontend`, `backend`, `infra`, `tests`, `docs`, `config` — para filtrar learnings por região do código.

---

## Protocolos de persistência de contexto (resumo)

- **WAL:** Ao detectar correções, decisões, nomes ou preferências na mensagem do humano, **escrever primeiro** em SESSION-STATE.md e **depois** responder. Ver [13-habilidades-proativas.md](13-habilidades-proativas.md).
- **Working Buffer:** A partir de ~60% de uso de contexto, registrar toda troca em `memory/working-buffer.md`; após compactação, recuperar lendo o buffer e SESSION-STATE antes de continuar.
- **Recuperação:** Nunca perguntar "sobre o que estávamos falando?" — ler working-buffer e SESSION-STATE e consolidar antes de responder.
- **Busca unificada:** Antes de dizer "não tenho essa informação", buscar em memória diária, MEMORY.md, transcripts e fallback exato (grep).

## Resourcefulness e guardrails

- **Resourcefulness:** Quando algo não funcionar, tentar abordagens **diversas** (CLI, browser, busca, sub-agentes) antes de pedir ajuda. **Diversidade de ferramenta (obrigatória):** se uma abordagem com a **mesma ferramenta** falhar **duas vezes consecutivas** pelo **mesmo motivo** (ex.: headless timeout, elemento não encontrado), o **orquestrador bloqueia o uso dessa ferramenta** no escopo daquela tarefa — o agente é forçado a mudar **vetor** (ex.: CLI nativo, API direta, outra skill). Evita loops cegos que esgotam orçamento e GPU. O **contador de persistência** é integrado ao **Gateway FinOps**: cada retry em modo de falha tem **peso financeiro** (multiplicador por número da tentativa no pre-flight); ao atingir o gatilho, o orquestrador **interrompe a execução**, devolve a tarefa ao **backlog do PO** e **libera travas de hardware** (ex.: GPU) para o restante do enxame. **Regra geral:** qualquer interrupção (FinOps ou outra) — a tarefa **sempre** volta ao backlog do PO; a issue nunca se perde. Ver [13-habilidades-proativas.md](13-habilidades-proativas.md) e [06-operacoes.md](06-operacoes.md).
- **Verificar antes de reportar (VBR):** Só reportar "pronto" após testar o resultado do ponto de vista do usuário.
- **Evolução segura (ADL/VFM):** Princípios literários (estabilidade > novidade, valor ponderado) são aplicados via **funções de aptidão quantitativas** e **auditoria por regex**; ver [13-habilidades-proativas.md](13-habilidades-proativas.md).

## Boas práticas

1. **Registrar logo** — contexto mais fresco após o evento.
2. **Ser específico** — quem for corrigir precisa entender rápido.
3. **Incluir passos de reprodução** — sobretudo em ERRORS.md.
4. **Vincular arquivos** — Metadata com Related Files.
5. **Sugerir correção concreta** — não só "investigar".
6. **Registrar para curadoria** — itens amplamente aplicáveis ficam em .learnings/ com status adequado; a promoção para SOUL.md/AGENTS.md/TOOLS.md é feita pelo curador em sessão isolada (não pelo agente diretamente).
7. **Entradas recorrentes** — usar **See Also** entre entradas; aumentar prioridade se o problema se repete; considerar correção sistêmica (doc ou automação).
8. **WAL antes de responder** — capturar correções e decisões em SESSION-STATE antes de enviar a resposta.

---

## Relação com a documentação

- **28-memoria-longo-prazo-elite.md** — Seis camadas de memória (Hot RAM, Warm Store, Cold Store, arquivo curado, cloud, autoextração), WAL, instruções por momento da sessão e higiene de memória; este doc (10) cobre a estrutura do workspace e a promoção para memória; o 28 detalha o modelo completo.
- **13-habilidades-proativas.md** — Pilares proativo, persistente e autoaprimoramento; WAL, Working Buffer, recuperação pós-compactação; heartbeats; ADL/VFM; crons autônomo vs promptado.
- **07-configuracao-e-prompts.md** — Perfis por agente, memória, truncamento; o pipeline de contexto deve seguir operando **antes** do envio à nuvem; learnings não substituem o controle de custo por truncamento/sumarização.
- **05-seguranca-e-etica.md** — Skills de terceiros (ex.: Claw Hub); varredura na borda; não logar dados sensíveis ou tokens em .learnings.
- **soul/** — Identidade por agente; SOUL.md do workspace estende com regras gerais de comportamento e self-improvement.
