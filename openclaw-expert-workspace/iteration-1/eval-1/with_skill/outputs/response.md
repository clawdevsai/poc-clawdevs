# O Agent Loop no OpenClaw: Guia Completo

Excelente pergunta! Vou explicar como o agent loop funciona do início ao fim, transformando uma mensagem em respostas e ações.

## O Que É o Agent Loop?

O **agent loop** é a execução real e completa de um agente em OpenClaw. Ele segue este caminho:

```
mensagem de entrada → assembly do contexto → inferência do modelo → execução de ferramentas → streaming de respostas → persistência no histórico
```

É um processo serializado por sessão que emite eventos de ciclo de vida e streaming enquanto o modelo pensa, chama ferramentas e produz output.

## Fluxo Completo: Intake até Persistência

### 1. Entry Point - Recebimento da Solicitação

Existem dois pontos de entrada principais:

- **Gateway RPC**: métodos `agent` e `agent.wait`
- **CLI**: comando `agent`

```python
# Pseudocódigo: Validação inicial no Gateway
def agent_request(sessionKey, messages, params):
    # 1. Valida parâmetros
    validate_params(params)

    # 2. Resolve a sessão (por sessionKey ou sessionId)
    session = resolve_session(sessionKey)

    # 3. Persiste metadata da sessão
    persist_session_metadata(session)

    # 4. Retorna imediatamente com runId
    return {
        "runId": generate_run_id(),
        "acceptedAt": current_time(),
        "status": "accepted"
    }
```

### 2. Resolução de Model + Defaults

O `agentCommand` resolve as configurações iniciais:

```typescript
// TypeScript: Resolução de modelo e defaults
async function agentCommand(runId: string, session: Session) {
    // Resolve model + thinking/verbose defaults
    const model = resolve_model(session.config.model);
    const thinkingEnabled = resolve_thinking(session.config);
    const verbose = resolve_verbose(session.config);

    // Carrega snapshot de skills da sessão
    const skills = load_skills_snapshot(session);

    // Injeta skills no ambiente e prompt
    env.skills = skills;

    // Chama o runtime pi-agent-core
    return await runEmbeddedPiAgent(session, model, skills);
}
```

### 3. Resolução de Workspace + Sessão

Antes da execução:

```go
// Go: Preparação de workspace
func prepareSession(sessionKey string) {
    // Resolve e cria workspace
    workspace := resolveWorkspace(sessionKey)

    // Redirects para sandbox se necessário
    if isSandboxed {
        workspace = redirectToSandboxRoot(workspace)
    }

    // Adquire write lock da sessão
    sessionLock := acquireSessionWriteLock(sessionKey)
    defer sessionLock.Release()

    // Abre SessionManager
    manager := openSessionManager(sessionKey)

    // Pronto para streaming
    return preparedSession{
        workspace: workspace,
        manager: manager,
        lock: sessionLock,
    }
}
```

### 4. Assembly do Prompt

O sistema constrói o prompt combinando várias camadas:

```python
# Pseudocódigo: Construção do System Prompt
def build_system_prompt(session, skills, overrides):
    # Começa com o prompt base do OpenClaw
    base_prompt = load_base_openclaw_prompt()

    # Adiciona prompt de skills
    skills_prompt = generate_skills_prompt(skills)

    # Resolve e injeta arquivos de bootstrap/contexto
    bootstrap_files = resolve_bootstrap_files(session)
    bootstrap_context = inject_bootstrap_context(bootstrap_files)

    # Aplica overrides por-run
    final_prompt = combine_prompts([
        base_prompt,
        bootstrap_context,
        skills_prompt,
        overrides.system_prompt or "",
    ])

    # Enforce limites de tokens específicos do modelo
    enforce_model_token_limits(final_prompt, session.model)

    return final_prompt
```

### 5. Hook: Antes da Resolução do Modelo

Se houver hooks configurados, este é o momento em que `before_model_resolve` é disparado:

```typescript
// TypeScript: Plugin hooks
async function executeHooks(phase: string, context: any) {
    const hooks = loadHooks(phase);

    for (const hook of hooks) {
        // before_model_resolve: sem mensagens ainda, pode override provider/model
        if (phase === "before_model_resolve") {
            const result = await hook.handler(context);
            if (result.model) {
                context.model = result.model;
            }
        }

        // before_prompt_build: após carregar sessão
        if (phase === "before_prompt_build") {
            if (result.prependContext) {
                context.prependContext = result.prependContext;
            }
            if (result.systemPrompt) {
                context.systemPrompt = result.systemPrompt;
            }
        }
    }

    return context;
}
```

### 6. Execução Serializada - Queueing

OpenClaw serializa runs para prevenir race conditions:

```go
// Go: Sistema de fila por sessão
type QueueLane struct {
    sessionKey string
    runQueue   chan *AgentRun
    globalLane chan *AgentRun
}

func (q *QueueLane) enqueueRun(run *AgentRun) {
    // Serializa dentro da lane da sessão
    q.runQueue <- run

    // Opcionalmente passa por global lane também
    if q.globalLane != nil {
        q.globalLane <- run
    }

    // Espera fila serializar antes de continuar
    <-run.Started
}
```

### 7. Chamada do Runtime PI-Agent-Core

O heart do loop é o runtime embarcado:

```python
# Pseudocódigo: Execução do modelo
async def runEmbeddedPiAgent(session, model, skills):
    # Resolve model + auth profile
    auth_profile = resolve_auth_profile(model)

    # Constrói pi session (estrutura interna)
    pi_session = buildPiSession(
        messages=session.messages,
        model=model,
        system_prompt=build_system_prompt(...),
        tools=skills.to_tools(),
        auth_profile=auth_profile
    )

    # Inscreve-se em eventos pi e transmite para OpenClaw
    subscription = subscribeEmbeddedPiSession(pi_session)

    # Enforce timeout (padrão 600s)
    timeout_task = create_timeout_task(600)

    try:
        # Executa o modelo
        response = await pi_session.run()

        # Se modelo não emitiu lifecycle end, emite agora
        if not subscription.received_lifecycle_end:
            emit_lifecycle_event("end")

        return response

    except TimeoutError:
        abort_run(pi_session)
        emit_lifecycle_event("error", "timeout")
```

### 8. Streaming de Eventos

Os eventos são transmitidos em tempo real:

```typescript
// TypeScript: Bridge de eventos pi -> OpenClaw
function subscribeEmbeddedPiSession(piSession: PiSession): void {
    piSession.on("tool_call", (tool) => {
        // tool events => stream: "tool"
        emit({
            type: "event",
            event: "agent",
            payload: {
                stream: "tool",
                tool: tool.name,
                args: tool.args,
            }
        });
    });

    piSession.on("text_delta", (delta) => {
        // assistant deltas => stream: "assistant"
        emit({
            type: "event",
            event: "agent",
            payload: {
                stream: "assistant",
                delta: delta,
            }
        });
    });

    piSession.on("phase_change", (phase) => {
        // lifecycle events => stream: "lifecycle"
        emit({
            type: "event",
            event: "agent",
            payload: {
                stream: "lifecycle",
                phase: phase, // "start" | "end" | "error"
            }
        });
    });
}
```

### 9. Execução de Ferramentas

Quando o modelo chama uma ferramenta:

```python
# Pseudocódigo: Execução de ferramentas
async def execute_tool(tool_name, args):
    before_hook = dispatch_hook("before_tool_call", {
        "tool": tool_name,
        "args": args
    })

    # Hook pode bloquear com block: true
    if before_hook.block:
        emit_tool_event("blocked", tool_name)
        return {"error": "blocked"}

    try:
        # Executa a ferramenta
        result = await tools[tool_name](args)

        # Sanitiza tamanho e payloads de imagem
        result = sanitize_tool_result(result)

        # Hook pós-execução
        after_hook = dispatch_hook("after_tool_call", {
            "tool": tool_name,
            "result": result
        })

        # Transforma resultado antes de persistir
        persisted = dispatch_hook("tool_result_persist", result)

        emit_tool_event("end", tool_name, persisted)
        return persisted

    except ToolError as e:
        emit_tool_event("error", tool_name, str(e))
        return {"error": str(e)}
```

### 10. Compaction (Compressão de Histórico)

Se o histórico fica muito longo:

```go
// Go: Auto-compaction
func checkAndCompact(session *Session) error {
    // Verifica pressão de contexto
    tokenCount := countTokens(session.messages)

    if tokenCount > session.compactionThreshold {
        // Emite evento antes
        emit("compaction", map[string]interface{}{
            "phase": "before",
            "tokenCount": tokenCount,
        })

        // Compacta mensagens antigas
        compacted := compactMessages(session.messages)
        session.messages = compacted

        // Emite evento após
        emit("compaction", map[string]interface{}{
            "phase": "after",
            "newTokenCount": countTokens(compacted),
        })

        // Pode disparar retry automático
        if compactionTriggeredRetry {
            return retryAgentRun(session)
        }
    }

    return nil
}
```

### 11. Agent.wait - Esperando Resultado

O cliente pode aguardar o resultado da execução:

```typescript
// TypeScript: Esperando lifecycle end
function agent_wait(runId: string, timeoutMs: number = 30000): Promise<Result> {
    return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
            reject(new Error("agent.wait timeout"));
        }, timeoutMs);

        // Aguarda lifecycle end/error para runId
        const unsubscribe = subscribe("agent", (event) => {
            if (event.payload.runId === runId &&
                event.payload.stream === "lifecycle") {

                clearTimeout(timeout);
                unsubscribe();

                const phase = event.payload.phase;
                if (phase === "end") {
                    resolve({
                        status: "ok",
                        startedAt: event.startedAt,
                        endedAt: event.endedAt,
                    });
                } else if (phase === "error") {
                    resolve({
                        status: "error",
                        error: event.payload.error,
                    });
                }
            }
        });
    });
}
```

### 12. Formatação de Resposta Final

As respostas finais são montadas a partir de várias fontes:

```python
# Pseudocódigo: Formatação de respostas
def shape_final_reply(assistant_text, tool_summaries, reasoning, errors):
    payloads = []

    # Adiciona texto do assistente
    if assistant_text:
        payloads.append({
            "type": "text",
            "content": assistant_text
        })

    # Adiciona raciocínio se disponível
    if reasoning:
        payloads.append({
            "type": "reasoning",
            "content": reasoning
        })

    # Adiciona resumos de ferramentas (se verbose + permitido)
    if verbose and allow_inline_summaries:
        payloads.extend(tool_summaries)

    # Filtra NO_REPLY (token silencioso)
    payloads = [p for p in payloads if p.content != "NO_REPLY"]

    # Remove duplicatas de tool messaging
    payloads = remove_messaging_tool_duplicates(payloads)

    # Se nenhuma resposta renderable e ferramenta errou
    if not payloads and has_tool_error:
        payloads.append(create_fallback_error_reply())

    return payloads
```

### 13. Persistência no Histórico

Finalmente, tudo é persistido:

```go
// Go: Persistência final
func persistAgentRun(session *Session, run *AgentRun) error {
    // Adiciona resposta ao histórico
    session.messages = append(session.messages, Message{
        role: "assistant",
        content: run.finalReply,
        metadata: map[string]interface{}{
            "runId": run.runId,
            "model": run.model,
            "tokens": run.tokenUsage,
            "toolCalls": run.toolCalls,
        },
    })

    // Salva sessão
    if err := session.Save(); err != nil {
        return err
    }

    // Emite evento de persistência completa
    emit("agent", map[string]interface{}{
        "stream": "lifecycle",
        "phase": "persisted",
        "runId": run.runId,
    })

    return nil
}
```

## Pontos de Interception - Hooks

OpenClaw oferece vários pontos onde você pode intervir:

### Hooks de Gateway (internos)

- **`agent:bootstrap`**: Antes do system prompt ser finalizado
- **Command hooks**: `/new`, `/reset`, `/stop`, etc.

### Plugin Hooks (dentro do agent loop)

| Hook | Quando | O que fazer |
|------|--------|-----------|
| `before_model_resolve` | Antes de resolver modelo (sem mensagens) | Override provider/model |
| `before_prompt_build` | Após carregar sessão (com mensagens) | Injetar contexto/system prompt |
| `before_agent_start` | Legado - compatibilidade | Não recomendado |
| `agent_end` | Após conclusão | Inspecionar resultado final |
| `before_tool_call` | Antes de executar ferramenta | Bloquear com `block: true` |
| `after_tool_call` | Após executar ferramenta | Modificar resultado |
| `tool_result_persist` | Antes de persistir resultado | Transformar dados |
| `message_received` | Mensagem inbound | Filtrar/logar |
| `message_sending` | Mensagem outbound | Cancelar com `cancel: true` |
| `before_compaction` | Antes de compactar histórico | Observar/anotar |

## Modelos de Fila

Channels de mensagens podem escolher modos de fila que afetam o loop:

- **collect**: Aguarda múltiplas mensagens antes de iniciar
- **steer**: Decisões de roteamento antes de enfileirar
- **followup**: Mensagens de seguimento após resposta

## Timeouts e Early Exit

O loop pode terminar cedo por:

- **Timeout do agent**: 600s padrão (configurável)
- **AbortSignal**: Cliente cancela
- **Desconexão gateway**: Cliente desconecta
- **Timeout de wait**: `agent.wait` timeout (não para o agent, apenas a espera)

## Fluxo Completo em ASCII

```
Cliente                     Gateway                    Modelo (PI-Agent-Core)
   |                            |                                  |
   |----req:agent---------->     |                                  |
   |                    validate |                                  |
   |                            |                                  |
   |<----res:agent(runId)--------                                  |
   |                    [RETORNA IMEDIATAMENTE]                    |
   |                            |                                  |
   |                       build prompt                            |
   |                            |                                  |
   |                       enqueue run                             |
   |                            |                                  |
   |                    resolveWorkspace                           |
   |                            |                                  |
   |                    loadSkillsSnapshot                         |
   |                            |                                  |
   |                  runEmbeddedPiAgent                           |
   |                            |----modelo.run()----->            |
   |                            |                      think...    |
   |<--event:assistant(delta)--<-----stream delta-------           |
   |                            |                                  |
   |<--event:tool(call)--------<---------tool call--------         |
   |                    [executa tool]                             |
   |                            |                                  |
   |<--event:tool(result)------<---------return result---          |
   |                            |                                  |
   |<--event:assistant(delta)--<-----stream delta-------           |
   |                            |                                  |
   |<--event:lifecycle(end)----<---------lifecycle end---          |
   |                       persistToHistory                        |
   |                            |                                  |
   |-----req:agent.wait------->  |                                  |
   |<----res:agent.wait(status)--                                  |
```

## Resumo

O agent loop no OpenClaw é:

1. **Serializado por sessão** - evita race conditions
2. **Event-driven** - streams de lifecycle, assistant, tool em tempo real
3. **Interceptável** - hooks em múltiplos pontos
4. **Completo** - vai de intake até persistência
5. **Resiliente** - timeouts, retry, compaction automática

Cada loop é uma execução real e autorizada que transforma uma mensagem do usuário em ações de ferramentas e uma resposta final, mantendo o histórico consistente.

---

**Fonte**: Documentação oficial do OpenClaw
- `/concepts/agent-loop`
- `/concepts/architecture`
- `/concepts/system-prompt`
- `/concepts/context`
