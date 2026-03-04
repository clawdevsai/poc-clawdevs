# Memória de longo prazo (Elite)

Os agentes do enxame adotam um **sistema de memória em camadas** inspirado no padrão *Elite Longterm Memory*: nunca perder contexto, nunca esquecer decisões, nunca repetir erros. Este documento consolida as **seis camadas** (Hot RAM, Warm Store, Cold Store, Arquivo curado, Backup em nuvem opcional, Autoextração opcional), o **protocolo WAL**, a **higiene de memória** e a integração com o workspace OpenClaw e com [10-self-improvement-agentes.md](10-self-improvement-agentes.md) e [13-habilidades-proativas.md](13-habilidades-proativas.md).

**Referência de origem:** Padrões do ecossistema *Elite Longterm Memory* (WAL, LanceDB, Git-Notes, Mem0), adaptados ao time de agentes autônomos, OpenClaw e postura Zero Trust.

---

## Visão geral da arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMÓRIA DE LONGO PRAZO (ELITE)               │
├─────────────────────────────────────────────────────────────────┤
│  Camada 1       Camada 2        Camada 3        Camada 4        │
│  HOT RAM        WARM STORE      COLD STORE      ARQUIVO CURADO  │
│  SESSION-       LanceDB        Git-Notes       MEMORY.md       │
│  STATE.md       (vetores)       (decisões)      + memory/       │
│  (sobrevive     (busca         (estruturado,   (legível,       │
│   compactação)   semântica)     branch-aware)   diários)        │
│       │             │               │               │          │
│       └─────────────┴───────────────┴───────────────┘          │
│                             │                                   │
│  Camada 5 (opcional)        ▼                                   │
│  CLOUD BACKUP        Consolidação e recall                       │
│  (SuperMemory)       (memory_search, RAG)                       │
│  Camada 6 (opcional)                                            │
│  AUTOEXTRAÇÃO (Mem0) — redução de tokens                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## As seis camadas

### Camada 1: HOT RAM (SESSION-STATE.md)

**Estado ativo da tarefa/sessão.** Sobrevive à compactação e a reinícios.

- **Arquivo:** `SESSION-STATE.md` no workspace OpenClaw.
- **Conteúdo típico:** Current Task, Key Context, Pending Actions, Recent Decisions. **Invariantes de negócio:** regras absolutas definidas pelo Diretor (ex.: "token de login expira em 5 min") devem ser marcadas com **tag especial** no texto; o script de limpeza do DevOps usa **regex** para **nunca** remover linhas com essa tag — assim as regras críticas sobrevivem à compactação da janela de memória. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (seção 2.3).
- **Onde ficam os critérios de aceite originais (para validação reversa do PO):** Os critérios de aceite de cada issue **não** podem ficar apenas no buffer que será sumarizado; senão o PO recebe só o resumo e perde a referência para comparar. Devem ficar em **(1)** bloco com **tag de proteção** no Markdown (ex.: `<!-- CRITERIOS_ACEITE -->`), que o script de limpeza do DevOps ignora por regex e o sumarizador não processa; ou **(2)** em **arquivo separado** (ex.: SESSION-STATE.md ou `session.md` por issue), com o orquestrador enviando **payload duplo** à nuvem (resumo + critérios intactos). O PO **sempre** acessa os critérios intactos para fazer a validação reversa. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (Pipeline de truncamento e sumarização, segregação dos critérios de aceite).
- **Gancho de validação de contexto:** Antes da sumarização na nuvem, um modelo local pode varrer o buffer de trabalho e propor **extração** de intenções do usuário ou regras informais (sem tag) para o SESSION-STATE — preserva valor de negócio e mitiga amnésia funcional. **Validação reversa (PO):** após a sumarização, o PO compara o resumo com os **critérios de aceite originais** (que devem estar disponíveis intactos, conforme acima); se o resumo omitir critério fundamental, o PO rejeita o truncamento e o sistema reestrutura o bloco. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (Pipeline de truncamento e sumarização).
- **Regra:** Escrever **antes** de responder (protocolo WAL). Gatilho: mensagem do usuário com correções, decisões, preferências, nomes, prazos.

Detalhes do WAL e do uso de SESSION-STATE em [13-habilidades-proativas.md](13-habilidades-proativas.md) e [10-self-improvement-agentes.md](10-self-improvement-agentes.md).

### Camada 2: WARM STORE (vetores / LanceDB)

**Busca semântica** sobre memórias. Recall automático ou manual quando o OpenClaw tiver suporte (ex.: plugin memory-lancedb).

- **Uso:** `memory_search` (ou equivalente) no início da sessão e antes de afirmar "não tenho essa informação".
- **Armazenar:** preferências e decisões importantes com alta importância (ex.: `memory_store` com importance=0.9 quando disponível). **MicroADRs:** o Agente Architect gera **microADRs** (registros de decisão arquitetural em JSON estrito) ao aprovar PRs; esses registros são **imutáveis** e **nunca sumarizados** — anexados diretamente ao Warm Store, fora do pipeline de sumarização. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (seção 2.3).
- **Higiene:** revisar vetores periodicamente; remover itens irrelevantes (`memory_forget` ou equivalente) para evitar ruído e desperdício de tokens. MicroADRs não entram no critério de remoção por irrelevância.

Configuração (quando aplicável): em `~/.openclaw/openclaw.json`, `memorySearch.enabled: true`, `plugins.memory-lancedb` com `autoRecall` e `minImportance` conforme necessidade. Exige `OPENAI_API_KEY` para embeddings.

### Camada 3: COLD STORE (Git-Notes) — opcional

**Decisões estruturadas**, branch-aware, permanentes.

- **Uso:** armazenar decisões técnicas e de produto de forma silenciosa (não anunciar ao usuário a cada store).
- **Exemplo:** "Usar React para frontend", "Tailwind, não vanilla CSS".
- **Recuperação:** consultar por tema (ex.: "frontend", "stack") quando precisar de contexto de decisões passadas.

Requer script/tool de Git-Notes no workspace (ex.: `memory.py -p $DIR remember '{"type":"decision","content":"..."}' -t tech -i h` e `get "frontend"`). Pode ser instalado como skill ou mantido como script interno; instalação de skills segue [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) e Zero Trust.

### Camada 4: ARQUIVO CURADO (MEMORY.md + memory/)

**Memória legível por humanos.** Diários e destilação de aprendizado.

- **MEMORY.md:** memória de longo prazo curada (preferências do usuário, projetos, decisões, lições aprendidas, preferências). Inclui **decisões por omissão cosmética** (data, contexto, rota escolhida) quando o CEO aprova por omissão após timer sem resposta do Diretor — aplica-se **apenas** a impasses estritamente cosméticos (CSS, UI isolada, markdown); para auditoria pelo Diretor. Ver [06-operacoes.md](06-operacoes.md) e [01-visao-e-proposta.md](01-visao-e-proposta.md).
- **memory/YYYY-MM-DD.md:** log do dia.
- **memory/working-buffer.md:** zona de perigo entre ~60% de contexto e compactação; recuperação pós-compactação (ver [13-habilidades-proativas.md](13-habilidades-proativas.md)). **Quando o working buffer for persistido no Redis** (ex.: buffer de conversas do stream), configurar **TTL** nas chaves para que mensagens antigas **expirem automaticamente** — o "lixo digital" evapora da memória sem depender do agente DevOps para limpar; a previsibilidade é lei da infraestrutura (mesmo princípio do TTL do GPU Lock). Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) e [04-infraestrutura.md](04-infraestrutura.md).

Estrutura já descrita em [10-self-improvement-agentes.md](10-self-improvement-agentes.md). Ao final da sessão: atualizar SESSION-STATE; mover itens significativos para MEMORY.md; criar/atualizar o diário do dia.

### Camada 5: CLOUD BACKUP (SuperMemory) — opcional

Sincronização entre dispositivos e backup em nuvem. Só configurar quando aprovado pelo Diretor e com credenciais gerenciadas de forma segura (secrets, nunca em repositório). Variável `SUPERMEMORY_API_KEY` em ambiente controlado.

### Camada 6: AUTOEXTRAÇÃO (Mem0) — recomendado para redução de tokens

Extração automática de fatos a partir de conversas; reduz volume de contexto enviado ao modelo (~80% de redução em cenários típicos).

- **Uso:** quando disponível no ambiente, integrar Mem0 para adicionar mensagens e buscar memórias por usuário/sessão.
- **Benefícios:** preferências, decisões e fatos extraídos e deduplicados automaticamente; menos dependência de histórico bruto.
- **Requisito:** `MEM0_API_KEY` (ou equivalente) configurado de forma segura; instalação/uso alinhados a Zero Trust.

---

## Protocolo WAL (Write-Ahead Log)

**Regra crítica:** escrever estado **antes** de responder, não depois.

| Gatilho | Ação |
|--------|------|
| Usuário exprime preferência | Escrever em SESSION-STATE.md → depois responder |
| Usuário toma decisão | Escrever em SESSION-STATE.md → depois responder |
| Usuário informa prazo ou valor concreto | Escrever em SESSION-STATE.md → depois responder |
| Usuário corrige o agente | Escrever em SESSION-STATE.md → depois responder |

Se o agente responder primeiro e houver compactação ou falha antes de salvar, o contexto se perde. O WAL garante durabilidade.

---

## Instruções por momento da sessão

### No início da sessão

1. Ler **SESSION-STATE.md** (contexto quente).
2. Executar **memory_search** (ou equivalente) para contexto relevante.
3. Verificar **memory/YYYY-MM-DD.md** (e dia anterior) para atividade recente.

### Durante a conversa

1. **Usuário dá detalhe concreto?** → Escrever em SESSION-STATE.md **antes** de responder.
2. **Decisão importante?** → Registrar no Cold Store (Git-Notes) de forma silenciosa, quando disponível.
3. **Preferência expressa?** → `memory_store` com importância alta (ex.: 0.9) quando o Warm Store estiver habilitado.

### No encerramento da sessão

1. Atualizar SESSION-STATE.md com o estado final.
2. Mover itens significativos para MEMORY.md quando valerem para longo prazo.
3. Criar ou atualizar o diário em **memory/YYYY-MM-DD.md**.

---

## Higiene de memória (semanal)

1. **SESSION-STATE.md** — arquivar tarefas concluídas; manter só o ativo/relevante.
2. **Warm Store** — listar memórias recentes (ex.: `memory_recall query="*" limit=50`); remover vetores irrelevantes.
3. **Diários** — consolidar logs antigos em MEMORY.md quando fizer sentido; manter MEMORY.md enxuto (<5KB de resumo quando possível).
4. **Estrutura opcional** — organizar `memory/` em subpastas (ex.: `projects/`, `decisions/`, `lessons/`) e manter MEMORY.md como índice ou resumo.

---

## Por que a memória falha (e como corrigir)

| Falha | Causa provável | Correção |
|-------|----------------|----------|
| Esquece tudo entre sessões | memory_search desabilitado ou sem chave de embeddings | Habilitar busca semântica e configurar OPENAI_API_KEY (ou provedor equivalente) |
| Arquivos não carregados | Agente não lê SESSION-STATE/MEMORY no bootstrap | Incluir leitura de SESSION-STATE e MEMORY nas regras do agente (AGENTS.md / SOUL) |
| Fatos não capturados | Nenhuma extração automática nem registro manual | Usar Mem0 quando aprovado ou disciplina de registro em MEMORY.md e diários |
| Subagentes sem contexto | Contexto não herdado | Passar contexto essencial no prompt da tarefa ao spawnar subagente |
| Repete erros | Lições não registradas | Registrar em memory/lessons.md e em .learnings/; promover para MEMORY.md quando aplicável |

---

## Inicialização do workspace

Garantir que o workspace tenha:

- **SESSION-STATE.md** — template com Current Task, Key Context, Pending Actions, Recent Decisions.
- **MEMORY.md** — seções sugeridas: About the User, Projects, Decisions Log, Lessons Learned, Preferences.
- **memory/** — pasta para diários (YYYY-MM-DD.md) e, se usado, working-buffer.md.

Comandos equivalentes ao *elite-memory* (quando a capacidade estiver disponível como skill ou script):

- `elite-memory init` — criar SESSION-STATE.md, MEMORY.md e pasta memory/ se não existirem.
- `elite-memory status` — verificar saúde (existência dos arquivos, tamanho).
- `elite-memory today` — criar ou abrir o diário do dia.

Se não houver CLI, criar os arquivos manualmente conforme templates em [10-self-improvement-agentes.md](10-self-improvement-agentes.md).

---

## Configuração prática (memory-setup)

Os agentes devem ter a **habilidade de configurar e usar memória persistente** (evitar "cérebro de goldfish"): habilitar busca semântica, criar a estrutura de arquivos e seguir o protocolo de recall. O conteúdo abaixo incorpora as práticas do padrão *memory-setup* (Moltbot/Clawdbot/OpenClaw).

### 1. Habilitar memory search na config

No arquivo de configuração do orquestrador (ex.: `~/.openclaw/openclaw.json` ou `~/.clawdbot/clawdbot.json`), adicionar:

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "voyage",
    "sources": ["memory", "sessions"],
    "indexMode": "hot",
    "minScore": 0.3,
    "maxResults": 20
  }
}
```

| Opção | Finalidade | Recomendado |
|-------|------------|-------------|
| `enabled` | Ativar busca em memória | `true` |
| `provider` | Provedor de embeddings | `"voyage"` ou `"openai"` |
| `sources` | O que indexar | `["memory", "sessions"]` |
| `indexMode` | Quando indexar | `"hot"` (tempo real) |
| `minScore` | Limiar de relevância | `0.3` (menor = mais resultados) |
| `maxResults` | Máximo de trechos retornados | `20` |

**Provedores:** `voyage` (Voyage AI), `openai` (OpenAI), `local` (embeddings locais, sem API).  
**Fontes:** `memory` (MEMORY.md + memory/*.md), `sessions` (transcrições de conversas).  
Variáveis de ambiente quando aplicável: `VOYAGE_API_KEY`, `OPENAI_API_KEY`.

### 2. Estrutura de memória no workspace

Além de `MEMORY.md` e `memory/YYYY-MM-DD.md`, pode-se organizar:

```
workspace/
├── MEMORY.md              # Memória curada de longo prazo
└── memory/
    ├── logs/              # Diários (YYYY-MM-DD.md)
    ├── projects/          # Contexto por projeto
    ├── groups/            # Contexto de grupos/sessões
    └── system/            # Preferências, notas de setup
```

O diário pode ficar em `memory/logs/YYYY-MM-DD.md` ou diretamente em `memory/YYYY-MM-DD.md`; o importante é manter o formato consistente.

### 3. Template MEMORY.md

Inicializar `MEMORY.md` na raiz do workspace com seções como:

- **Sobre [nome do usuário]** — fatos, preferências, contexto.
- **Projetos ativos** — resumos e status.
- **Decisões e lições** — escolhas importantes, lições aprendidas.
- **Preferências** — estilo de comunicação, ferramentas e fluxos.

### 4. Formato de diário

Em `memory/logs/YYYY-MM-DD.md` (ou `memory/YYYY-MM-DD.md`):

```markdown
# YYYY-MM-DD — Diário do dia

## [Hora] — [Evento/Tarefa]
- O que aconteceu
- Decisões tomadas
- Ações de acompanhamento

## [Hora] — [Outro evento]
- Detalhes
```

### 5. Instruções para AGENTS.md (recall)

Incluir no AGENTS.md (ou equivalente) para o agente **antes** de responder sobre trabalho anterior, decisões, datas, pessoas, preferências ou todos:

1. Executar **memory_search** com consulta relevante.
2. Usar **memory_get** para linhas específicas se necessário.
3. Se a confiança for baixa após a busca, informar que verificou a memória e não encontrou algo conclusivo.

Assim o agente deixa de "esquecer" entre sessões e passa a consultar memória de forma explícita.

### 6. Troubleshooting

| Problema | Causa provável | Correção |
|----------|----------------|----------|
| Busca em memória não funciona | `memorySearch.enabled` falso ou MEMORY.md ausente | Ativar na config, criar MEMORY.md na raiz, reiniciar gateway (ex.: `clawdbot gateway restart`) |
| Resultados pouco relevantes | Limiar alto ou poucos resultados | Reduzir `minScore` (ex.: 0.2), aumentar `maxResults` (ex.: 30); conferir se os arquivos de memória têm conteúdo útil |
| Erros de provedor | Chave de API ausente ou inválida | Voyage: `VOYAGE_API_KEY`; OpenAI: `OPENAI_API_KEY`; ou usar provedor `local` se não houver chaves |

### 7. Verificação

Validar que a memória está ativa:

- **Usuário:** "O que você lembra sobre [assunto passado]?"
- **Agente:** deve executar busca em memória e retornar contexto relevante quando existir.

Se o agente não usar memória, a config não está aplicada ou o gateway precisa ser reiniciado.

---

## Relação com a documentação

- [10-self-improvement-agentes.md](10-self-improvement-agentes.md) — Estrutura do workspace (AGENTS.md, SOUL.md, TOOLS.md, SESSION-STATE, MEMORY.md, memory/, .learnings/); promoção para memória; WAL e busca unificada.
- [13-habilidades-proativas.md](13-habilidades-proativas.md) — Pilares proativo, persistente e autoaprimoramento; WAL, Working Buffer, recuperação pós-compactação; busca unificada; heartbeat (incluindo verificação de memória).
- [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) — Pipeline de truncamento e memória em duas camadas; integração com custo de contexto e RAG.
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Zero Trust; não logar dados sensíveis ou tokens em memória ou .learnings.
- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — Instalação de skills de memória (ex.: LanceDB, Git-Notes, Mem0) somente após checklist e aprovação.
