---
name: openclaw-expert
description: Expert assistant for OpenClaw (AI agent framework for messaging channels). Use this skill whenever the user mentions OpenClaw, asks about agents, plugins, automation, hooks, webhooks, context management, sessions, memory, multi-agent systems, or wants to build/debug OpenClaw implementations. This skill explains concepts deeply, provides implementation guidance with pseudocode examples in Python/TypeScript/Go, recommends architecture patterns, troubleshoots issues, and generates project structures. Use it proactively for any OpenClaw-related work - from learning fundamentals to advanced multi-agent patterns.
compatibility: web-fetch (for searching OpenClaw docs when needed)
---

## O que é OpenClaw

OpenClaw é um framework para construir agentes de IA com suporte a múltiplos canais de mensageria (WhatsApp, Telegram, Discord, etc.). É construído em torno de um sistema robusto de **context management**, **sessions**, **memory compaction**, e **orquestração de múltiplos agentes**.

O OpenClaw roda em um **Gateway** que coordena todas as operações e fornece APIs tanto via RPC quanto via CLI.

---

## Principais Conceitos

### 1. Agent Loop (O Núcleo)

O **agent loop** é a execução completa de um agente em OpenClaw. Fluxo cíclico:

1. **Intake**: Receber mensagem do usuário via canal (WhatsApp, Telegram, etc)
2. **Session Resolution**: Resolver qual sessão do usuário está se comunicando
3. **Context Loading**: Carregar contexto (history, memory, metadados) via **context engine**
4. **System Prompt Building**: Montar system prompt com base no agente, skills, e configurações
5. **LLM Inference**: Chamar o modelo (Claude, GPT, etc) com o prompt completo
6. **Tool Execution**: Se o modelo chamou ferramentas (plugins), executá-las
7. **Response Streaming**: Enviar resposta de volta ao usuário (streaming real-time possível)
8. **Persistence**: Armazenar na sessão para histórico futuro
9. **Hooks & Events**: Disparar eventos que plugins podem escutar

Cada etapa é um ponto de interception onde hooks podem rodar.

### 2. Context & Context Engine (Crítico para Performance)

**O que é Context?**
- Tudo que o modelo precisa para responder bem: histórico de mensagens, informações sobre o usuário, dados persistentes em memory, workspace files, etc
- Context é **limitado em tokens** — não pode crescer infinitamente
- **Context Engine** é o sistema que gerencia o que incluir/excluir para manter eficiência

**Como o Context Engine Funciona:**

```
┌─────────────────────────────────────────────┐
│         SESSION (armazenada em disco)        │
│  ┌─────────────────────────────────────────┐ │
│  │ Histórico completo (pode ser gigante)   │ │
│  │ Memory entries (usuário, agent state)   │ │
│  │ Workspace files (dados persistidos)     │ │
│  └─────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────┘
               │ Context Engine seleciona o que usar
               ↓
    ┌──────────────────────┐
    │  CONTEXT WINDOW      │
    │  (para este run)     │
    │  Max ~100k tokens    │
    ├──────────────────────┤
    │ - Últimas N msgs     │
    │ - Top K memories     │
    │ - Workspace essencial│
    │ - System prompt      │
    └──────────────────────┘
               │
               ↓
    ┌──────────────────────┐
    │  LLM INFERENCE       │
    │  (Claude, GPT, etc)  │
    └──────────────────────┘
```

**Estratégias do Context Engine:**

1. **Recency Bias**: Manter mensagens recentes (últimos 10-20 messages)
2. **Relevance Scoring**: Scoreá mensagens antigas por relevância ao tópico atual
3. **Memory Compression**: Resumir conversas longas em "memory entries"
4. **Dynamic Selection**: Pegar os itens mais relevantes para este específico run

**Configurar Context Engine:**

```json
{
  "context": {
    "maxTokens": 100000,
    "recencyWindow": 20,
    "memoryTopK": 5,
    "prioritizeMemory": true
  }
}
```

### 3. Session & Session Pruning

**Session**: Identifica uma conversa de um usuário
- Formato: `user:<user-id>` ou `hook:<webhook-id>`
- Contém histórico completo + memory + metadados
- Pode crescer muito (anos de conversa)

**Session Pruning**: Remover dados antigos periodicamente

```json
{
  "session": {
    "pruning": {
      "enabled": true,
      "olderThan": "30d",
      "keepLastMessages": 100
    }
  }
}
```

### 4. Memory & Compaction

**Memory**: Informações persistentes sobre usuários/agentes que transcendem sessões

Exemplo:
```json
{
  "user:12345": {
    "name": "João",
    "preferences": "gosta de Python",
    "vip": true,
    "history_summary": "Trabalhou em 5 projetos de ML"
  }
}
```

**Compaction**: Sumarizar memória antiga para manter eficiência

```
Semana 1-4: Memory completa
    ↓ (após 4 semanas)
Semana 1-3: Compactada em resumo
Semana 4: Mantém detalhe
    ↓ (após 8 semanas)
Semana 1-7: Um único resumo
Semana 8: Detalhe
```

### 5. Plugins & Skills

**Plugins**: Pacotes que adicionam ferramentas/integrações ao OpenClaw
- Exemplo: `weather-plugin` expõe tool `get_weather`
- Hooks: `before_model_resolve`, `after_tool_call`, etc
- Manifesto: Define metadados, dependências, permissões

**Skills**: Comandos específicos (`/comando`) que usuários invocam
- Exemplo: `/summarize` resume a conversa
- Registradas no agent config
- Podem usar plugins por baixo

### 6. Automação

**Hooks**: Executar lógica quando eventos ocorrem
```json
{
  "hooks": [
    {
      "event": "message.received",
      "action": "log_to_database"
    }
  ]
}
```

**Standing Orders**: Instruções permanentes para agentes
- "Sempre valide entrada do usuário"
- "Se score < 0.5, peça confirmação"

**Cron Jobs**: Tarefas agendadas
- "A cada hora, verifique pendências"

**Webhooks**: Integração com sistemas externos
- Gateway chama seu server quando eventos ocorrem
- Seu server responde com ações

### 7. Arquitetura Multi-Agent

**Delegate Architecture**: Um agente supervisor delega trabalho para sub-agentes
- Supervisor: orquestra, valida, consolida
- Sub-agentes: especializados (dev, research, testing)
- Cada um roda isolado em sua própria sessão

**Presence**: Rastreamento de agentes online
- Saber quais agentes estão disponíveis
- Routing automático se um cair

**Message Flow**: Como mensagens fluem entre agentes
- via `sessions_spawn` (cria nova sessão para sub-agente)
- via `agent_send` (envia mensagem para agente específico)

---

## Padrões e Melhores Práticas

### 1. Design de Agent

**System Prompt**: Claro, conciso, com role definido
```
"Você é um especialista em Python que ajuda com code review.
Foque em legibilidade, performance, e segurança.
Sempre explique suas recomendações."
```

**Tool Selection**: Escolher plugins certos
- Não carregue plugins desnecessários (aumenta token usage)
- Mantenha skills simples e focadas

**Error Handling**: Tratar falhas gracefully
- Timeouts: agent demora demais
- Tool failures: plugin retorna erro
- Model quota exceeded: fallback para modelo menor

### 2. Gerenciamento de Context

**Keep It Small**:
- Manter context janela entre 20-100k tokens
- Usar memory para dados que ficam fora da janela
- Fazer compaction regularmente

**Smart Selection**:
- Não incluir tudo sempre
- Scoreá por relevância
- Priorize recente + relevante

**Monitor**:
```bash
/status              # Ver tokens atuais
/context detail      # Ver o que está no contexto
/memory list         # Ver memórias persistidas
```

### 3. Orquestração Multi-Agent

**Delegação Robusta**:
- Supervisor valida input antes de delegar
- Sub-agentes rodam isolados
- Timeout proteção: se sub-agente demora demais, fallback

**Consolidação**:
- Aggregar resultados de múltiplos agentes
- Validar qualidade antes de retornar
- Log de qual agente processou

### 4. Integração com Canais

**Testes em Múltiplos Canais**: WhatsApp, Telegram, Discord têm diferenças
- Media handling diferente
- Rate limits variam
- Formatting (bold, italic) pode não funcionar igual

**Fallbacks**: Se funcionalidade não existe no canal, ofereça alternativa

**Rate Limiting**: Respeitar limites do canal
- WhatsApp: ~30 mensagens/min
- Telegram: menos restritivo
- Implementar circuit breaker

---

## Como Usar Esta Skill

**Você pode pedir:**

1. **Explicar conceitos**: "Como funciona o context engine?"
2. **Guia de implementação**: "Como construir um plugin?"
3. **Exemplos de código**: Darei pseudocódigo em Python/TypeScript/Go
4. **Estrutura de projeto**: Vou sugerir pastas e organização
5. **Troubleshooting**: "Por que meu webhook não dispara?"
6. **Padrões arquiteturais**: "Como estruturar um sistema multi-agent?"
7. **Boas práticas**: "Como otimizar memory/context?"
8. **Web search**: Vou buscar nos docs oficiais quando necessário

---

## Quando Usar Outras Skills

Para tarefas mais especializadas, existem skills dedicadas:

- **openclaw-plugin-builder**: Criar um plugin do zero passo a passo (estrutura, manifest, hooks, testing)
- **openclaw-agent-patterns**: Padrões avançados (multi-agent, supervisor patterns, cross-domain delegation)
- **openclaw-automation-setup**: Configurar hooks, webhooks, standing orders, cron jobs
- **openclaw-troubleshooting**: Debugar problemas específicos com comandos OpenClaw e logs

---

## Exemplo Rápido: Agent Simples

```
PSEUDOCÓDIGO (Python/TypeScript/Go):

class MyAgent:
    def __init__(self):
        self.system_prompt = "Você é um assistente útil"
        self.plugins = [plugin_search, plugin_database]
        self.memory = {}

    async def process_message(context, user_message):
        # 1. Load context via Context Engine
        ctx = context_engine.load(
            session_key=user_id,
            max_tokens=80000,
            include_memory=true
        )

        # 2. Build prompt: system + histórico + user message
        prompt = build_prompt(
            system=self.system_prompt,
            history=ctx.recent_messages,
            memory=ctx.top_memories,
            user_input=user_message
        )

        # 3. Call LLM with tools
        response = await llm.chat(
            prompt=prompt,
            tools=self.plugins,
            model="claude-opus-4"
        )

        # 4. Execute tools if model called them
        while response.uses_tool:
            tool_result = await self.plugins[response.tool].execute(response.args)
            response = await llm.refine(
                prompt=prompt,
                previous_response=response,
                tool_result=tool_result
            )

        # 5. Store in session
        session.add_message(user_message, response.text)

        # 6. Update memory if should persist
        if should_remember(response):
            memory[user_id].update(extracted_insights)

        # 7. Emit event (plugins can listen)
        emit_event("agent.response_generated", {
            "agent": "my_agent",
            "tokens": response.usage.tokens,
            "tools_used": response.tools_called
        })

        return response.text
```

---

## Recursos e Referências

Tenho acesso à documentação completa do OpenClaw. Posso:
- Buscar docs quando apropriado (web search)
- Citar conceitos específicos com exemplos
- Fornecer exemplos baseados em casos reais
- Ajudar a escolher entre padrões diferentes

**Próximo passo**: O que você quer fazer com OpenClaw? Deixe-me guiar! 🚀
