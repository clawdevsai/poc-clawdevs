# Sistema Multi-Agent Supervisor em OpenClaw: Arquitetura e Padrões

## Resumo Executivo

Para implementar um sistema robusto de supervisor delegando para 3 agentes especializados em OpenClaw, recomenda-se o padrão **Hierárquico Supervisor-Workers com Isolamento de Sessão**. Este padrão garante:

- Isolamento de contexto entre agentes
- Delegação segura via `sessions_spawn`
- Persistência de estado independente
- Resiliência mediante timeouts e retry
- Auditoria clara de fluxos de trabalho

---

## 1. Padrão Recomendado: Supervisor Hierárquico com Workers Isolados

### 1.1 Estrutura de Agentes

```
openclaw agents add supervisor
openclaw agents add agent-analista
openclaw agents add agent-desenvolvedor
openclaw agents add agent-validador
```

**Cada agente é uma instância completamente isolada:**
- Workspace próprio: `~/.openclaw/agents/<id>/workspace`
- Sessions independentes: `~/.openclaw/agents/<id>/sessions`
- Auth profiles isolados: `~/.openclaw/agents/<id>/agent/auth-profiles.json`
- Não há colisão de estado entre agentes

### 1.2 Fluxo de Delegação

O supervisor recebe uma tarefa complexa e a decompõe:

```
[Usuário]
    ↓
[Supervisor]
    ├─→ sessions_spawn → [Agente Analista]  (análise de requisitos)
    ├─→ sessions_spawn → [Agente Dev]       (implementação)
    └─→ sessions_spawn → [Agente Validador] (QA e aprovação)
    ↓
[Resultado Consolidado]
```

### 1.3 Implementação do Supervisor

A lógica do supervisor reside no arquivo `AGENTS.md`:

```markdown
# Instruções do Supervisor

Você é um coordenador de projetos IA que delega trabalhos especializados.

## Responsabilidades

1. **Análise de Entrada**
   - Interpretar requisitos do usuário
   - Identificar escopo e complexidade
   - Preparar briefing para workers

2. **Delegação Estruturada**
   - Usar `sessions_spawn` para cada subtarefa
   - Passar contexto claro em `task` parameter
   - Respeitar timeouts (padrão 60s por worker)

3. **Integração de Resultados**
   - Consolidar outputs dos 3 workers
   - Resolver conflitos ou inconsistências
   - Fornecer resposta unificada ao usuário

## Workers Disponíveis

- `agent-analista`: Analisa requisitos, decompõe problemas
- `agent-desenvolvedor`: Implementa soluções, escreve código
- `agent-validador`: Testa, valida qualidade, aprova entregas

## Fluxo Padrão de Delegação

```
Tipo de Requisição → Workers Envolvidos
─────────────────────────────────────────
Análise técnica  → Analista + Validador
Feature nova     → Analista + Dev + Validador
Bug fix          → Dev + Validador
Refatoração      → Dev (paralelo com Validador)
```

## Protocolos de Comunicação

1. Cada `sessions_spawn` recebe um `task` bem-definido
2. Incluir contexto necessário (requisitos, arquivos, constrains)
3. Aguardar resultado com timeout de 60s
4. Tratamento de erro: tentar novamente ou escalar para Dev
```

---

## 2. Padrão de Delegação Robusto

### 2.1 Tool: sessions_spawn com Tratamento de Erro

Use a ferramenta `sessions_spawn` com configuração defensiva:

```markdown
# Template de Delegação Robusta

Para delegar análise:
```
sessions_spawn:
  task: |
    Analise os seguintes requisitos e forneça:
    1. Escopo claro
    2. Dependências identificadas
    3. Riscos e recomendações

    Requisitos: {contexto_usuario}
  model: claude-opus-4-1
  runTimeoutSeconds: 60
  sandbox:
    mode: all
    scope: spawned
```

Para delegar desenvolvimento:
```
sessions_spawn:
  task: |
    Implemente a solução conforme a análise:

    Requisitos Originais: {requisitos}
    Análise Fornecida: {output_analista}
    Constrains: {constrains}

    Entregue código testado e documentado.
  model: claude-opus-4-1
  runTimeoutSeconds: 90
  attachments: [{file: arquivo_referencia.py}]
```

Para delegar validação:
```
sessions_spawn:
  task: |
    Valide a implementação:
    1. Testes (cobertura > 80%)
    2. Conformidade (requisitos originais)
    3. Qualidade (code standards)
    4. Performance

    Análise Original: {output_analista}
    Implementação: {output_dev}

    Aprove ou liste críticas.
  model: claude-opus-4-1
  runTimeoutSeconds: 60
```
```

### 2.2 Tratamento de Falhas

**Implementar retry em 3 camadas:**

1. **Nível de Ferramenta** (OpenClaw automático)
   - Retry Policy padrão: 3 tentativas
   - Max delay: 30 segundos
   - Jitter: 10%

2. **Nível de Supervisor**
   ```markdown
   # No AGENTS.md do Supervisor

   SE worker falhar com timeout (>60s):
   - Log do erro
   - Tentar novamente COM mais contexto
   - Se falhar 2x: Escalar manualmente

   SE worker falhar com erro lógico:
   - Analisar output parcial
   - Fornecer feedback corretivo
   - Tentar novamente com ajustes
   ```

3. **Nível de Sessão**
   - Usar `/status` para verificar saúde de cada worker
   - Monitorar `lastInputSeconds` via presença
   - Resetar sessão desbravada com `/reset`

---

## 3. Isolamento e Segurança

### 3.1 Configuração de Sandbox por Agente

Em `~/.openclaw/openclaw.json`:

```json5
{
  agents: {
    list: [
      {
        id: "supervisor",
        sandbox: { mode: "off" },
        tools: {
          allow: ["sessions_spawn", "sessions_list", "sessions_history"],
          deny: ["exec", "file:write"]
        }
      },
      {
        id: "agent-analista",
        sandbox: {
          mode: "all",
          scope: "spawned"
        },
        tools: {
          allow: ["read", "sessions_spawn"],
          deny: ["exec", "file:write"]
        }
      },
      {
        id: "agent-desenvolvedor",
        sandbox: {
          mode: "all",
          scope: "spawned",
          docker: {
            setupCommand: "apt-get update && apt-get install -y python3 git"
          }
        },
        tools: {
          allow: ["read", "exec", "write"],
          deny: []
        }
      },
      {
        id: "agent-validador",
        sandbox: {
          mode: "all",
          scope: "spawned"
        },
        tools: {
          allow: ["read", "exec"],
          deny: ["write"]
        }
      }
    ]
  }
}
```

### 3.2 Gerenciamento de Sessão Multi-Agent

```json5
{
  session: {
    sendPolicy: {
      rules: [
        {
          action: "deny",
          match: { keyPrefix: "agent-analista:" }
        }
      ],
      default: "allow"
    },
    defaults: {
      dmScope: "per-account-channel-peer",
      resetPolicy: {
        idleMinutes: 120,
        dailyReset: "04:00"
      }
    }
  }
}
```

---

## 4. Estrutura de Arquivos por Agente

### 4.1 Supervisor Workspace

```
~/.openclaw/agents/supervisor/workspace/
├── AGENTS.md              # Instruções de delegação
├── IDENTITY.md            # "Supervisor de Projetos IA"
├── TOOLS.md               # Documentação de sessions_spawn
├── MEMORY.md              # Histórico de projetos completados
└── memory/
    └── YYYY-MM-DD.md      # Logs diários de delegações
```

### 4.2 Agente Especialista Workspace

```
~/.openclaw/agents/agent-analista/workspace/
├── AGENTS.md              # "Especialista em Análise"
├── IDENTITY.md            # Persona e expertise
├── TOOLS.md               # Tools específicas (análise, parsing)
└── templates/
    ├── analise-template.md
    └── requisitos-checklist.md
```

Similar para `agent-desenvolvedor` e `agent-validador`.

---

## 5. Robustez: Padrões Avançados

### 5.1 Circuit Breaker para Workers Falhando

No supervisor, implementar lógica defensiva:

```markdown
# Circuit Breaker Pattern (em AGENTS.md)

REGRA: Se um worker falha 3x consecutivas:
1. Logar evento crítico em MEMORY.md
2. Aguardar human feedback
3. NÃO tentar delegação até aprovação

Implementação:
- Manter contador por worker em memory/meta.json
- Resetar contador a cada sucesso
- Escalar para human intervention em threshold

Exemplo em MEMORY.md:
```
2026-03-31 | CIRCUIT BREAKER ATIVADO
Worker: agent-desenvolvedor
Tentativas falhadas: 3
Motivo: Timeout persistente
Status: Aguardando intervenção manual
```
```

### 5.2 Agregação de Resultados com Versionamento

Manter rastreabilidade de outputs:

```markdown
# Estrutura de Resultado (em MEMORY.md)

## Projeto: [ID_UNICO]

| Aspecto | Analista | Dev | Validador | Status |
|---------|----------|-----|-----------|--------|
| Escopo | ✅ OK | - | ✅ Conforme | PASS |
| Código | - | ✅ Entregue | ✅ OK | PASS |
| Testes | - | ✅ 85% | ✅ Validado | PASS |

Rastreamento:
- timestamp_analista: 2026-03-31T10:15:00Z
- timestamp_dev: 2026-03-31T10:45:00Z
- timestamp_validador: 2026-03-31T11:10:00Z

Versão Final: v1.0 (aprovada para deploy)
```

### 5.3 Monitoramento de Saúde

Usar tools built-in OpenClaw:

```markdown
# Monitoramento Regular (em AGENTS.md)

A cada ciclo, o supervisor pode:
1. Chamar `sessions_list` com `kinds: ["main"]`
2. Verificar `lastInputSeconds` de cada worker
3. Checar `messageLimit` para crescimento anormal
4. Registrar em memory para análise

Comando útil:
openclaw gateway call sessions.list --json | jq '.[] | select(.key | startswith("agent-")) | {key, messageCount, lastActivity}'
```

---

## 6. Resiliência contra Degradação de Performance

### 6.1 Fallback e Model Downgrade

```markdown
# Estratégia de Resiliência (em AGENTS.md)

Hierarquia de Models:
1. **Primário**: claude-opus-4-1 (melhor qualidade)
2. **Fallback**: claude-3.5-sonnet-20241022 (rápido, bom)
3. **Degradado**: claude-3-haiku-20240307 (rápido, simples)

Critério de Downgrade:
- Timeout > 60s → próxima tentativa com Sonnet
- Timeout > 90s → próxima tentativa com Haiku
- Rejeição de conteúdo → consultar supervisor

Implementação:
sessions_spawn:
  task: "..."
  model: claude-opus-4-1  # será degradado se necessário
  runTimeoutSeconds: 60
```

### 6.2 Caching de Análises Recorrentes

```markdown
# Cache de Saídas (em memory/cache.json)

Manter registro de:
```json
{
  "análises_padrão": {
    "Python-Django": {
      "escopo": "Framework web Python com ORM",
      "dependências": ["Django", "PostgreSQL", "Redis"],
      "timestamp": "2026-03-31T10:00:00Z"
    }
  },
  "ttl_horas": 168
}
```

Se entrada similar à anterior, reutilizar análise com confirmação
```

---

## 7. Fluxo Completo de Exemplo

### Requisição: "Implementar API GraphQL com autenticação JWT"

**T=0: Entrada no Supervisor**
```
Usuário: "Preciso de uma API GraphQL com JWT para uma app mobile"
Supervisor: Analisa → identifica 3 fases
```

**T=5: Delegação para Analista**
```
sessions_spawn:
  task: "Analise requisitos para API GraphQL com JWT.
         Contexto: app mobile, usuários finais 100k+.
         Forneça: escopo, arquitetura, riscos."
  model: claude-opus-4-1
  timeout: 60s
```

**T=10: Recebimento Output Analista**
```
Analista entrega:
- Arquitetura: Apollo Server + Express
- Auth: JWT com refresh tokens
- Riscos: Rate limiting, CORS, token rotation
```

**T=15: Delegação para Desenvolvedor**
```
sessions_spawn:
  task: "Implemente a API GraphQL conforme análise.
         Requisitos originais: [...]
         Análise arquitetura: [...]
         Entregue: server.js, schema.graphql, testes com Jest"
  model: claude-opus-4-1
  timeout: 90s
  attachments: [package.json, .env.example]
```

**T=30: Recebimento Output Dev**
```
Dev entrega:
- server.js (500 linhas)
- schema.graphql (150 linhas)
- auth.middleware.js
- tests/ (8 testes passando)
```

**T=35: Delegação para Validador**
```
sessions_spawn:
  task: "Valide a implementação GraphQL.
         Requisitos: [...]
         Código: [...]
         Checklist: cobertura testes, JWT compliance, CORS, rate limit"
  model: claude-opus-4-1
  timeout: 60s
```

**T=45: Resultado Final**
```
Validador aprova com:
✅ Testes: 85% cobertura
✅ Segurança: JWT correto, CORS configurado
✅ Performance: Queries N+1 mitigadas
⚠️  Recomendação: Adicionar DataLoader para otimização futura

Supervisor consolida e entrega ao usuário:
- Status: APROVADO
- Arquivos: api.tar.gz
- Próximos passos: Deploy em staging
```

---

## 8. Checklist de Robustez

### Antes de Produção

- [ ] Cada agente tem workspace isolado (`openclaw agents list`)
- [ ] Sandbox configurado por especialidade (dev com exec, analista readonly)
- [ ] Retry policy configurado em `~/.openclaw/openclaw.json`
- [ ] `dmScope: "per-account-channel-peer"` para evitar vazamento de contexto
- [ ] Timeouts realistas por tipo de tarefa (60s análise, 90s dev, 60s validação)
- [ ] Memory e logging de delegações em `MEMORY.md` ou `memory/YYYY-MM-DD.md`
- [ ] Circuit breaker implementado em caso de falhas repetidas
- [ ] Teste end-to-end com tarefa realista (análise + dev + validação)
- [ ] Monitoramento via `openclaw status` e `/status` em chat
- [ ] Backup de workspaces em Git privado

### Monitoramento Contínuo

- [ ] Revisar `memory/YYYY-MM-DD.md` diariamente para anomalias
- [ ] Rodar `openclaw doctor` semanalmente
- [ ] Verificar session size com `/context detail` se cresce muito
- [ ] Ativar compaction manual com `/compact` quando contexto > 70%
- [ ] Resetar workers desbravados com `/reset` periodicamente

---

## 9. Variações e Extensões

### 9.1 Supervisor Dual-Tier (2 níveis)

Para mais complexidade:

```
[Supervisor Principal]
    ├→ [Supervisor Técnico]
    │   ├→ [Dev]
    │   └→ [QA]
    └→ [Supervisor Produto]
        ├→ [Product Manager]
        └→ [Designer]
```

Usar `sessions_spawn` em cascata.

### 9.2 Round-Robin entre Workers

Se múltiplos workers do mesmo tipo:

```markdown
# Load Balance (em AGENTS.md)

Workers: agent-dev-01, agent-dev-02, agent-dev-03
Política: Distribuir por timestamp da última tarefa

currentWorker = workers[taskCount % workers.length]
sessions_spawn: ...worker: currentWorker
```

### 9.3 Feedback Loop com Supervisor

Workers podem pedir esclarecimento:

```
Agent-Dev para Supervisor:
"Análise ambígua em ponto X. Necessário esclarecimento do usuário.
 Opções: A) Usar default B) Esperar feedback"

Supervisor responde:
"Usar opção A (default), continuar com implementação"
```

---

## Conclusão

A arquitetura **Supervisor Hierárquico com Workers Isolados** em OpenClaw oferece:

✅ **Isolamento**: Cada agente opera em contexto independente
✅ **Robustez**: Timeouts, retries, circuit breakers, fallbacks
✅ **Rastreabilidade**: Memory, logs, versionamento de outputs
✅ **Escalabilidade**: Suporta 3+ workers, potencial para parallelismo
✅ **Resiliência**: Degrada gracefully, tenta alternativas, escalas para human

A chave é ser **defensivo**: sempre esperar falhas, sempre logar, sempre fornecer fallback.
