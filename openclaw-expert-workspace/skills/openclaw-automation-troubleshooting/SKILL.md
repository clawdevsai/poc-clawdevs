---
name: openclaw-automation-troubleshooting
description: Configure OpenClaw automation (hooks, webhooks, standing orders, cron jobs) and troubleshoot issues. Use when setting up event-driven systems, integrating webhooks, scheduling tasks, debugging why automations don't trigger, or monitoring automation health. Includes configuration examples, debugging checklists, command reference, log interpretation, and common pitfalls.
---

## Automação & Troubleshooting em OpenClaw

OpenClaw oferece múltiplos mecanismos para automatizar tarefas.

---

## Part 1: Tipos de Automação

### 1. Hooks (Event-Driven)

Executam lógica quando eventos ocorrem **dentro** do OpenClaw.

**Eventos Disponíveis:**
- `message.received` - Nova mensagem chegou
- `agent.run.start` - Agent iniciando
- `agent.run.end` - Agent terminou
- `agent.run.error` - Agent falhou
- `session.created` - Nova sessão aberta
- `session.ended` - Sessão fechada
- `tool.called` - Tool foi invocada
- `tool.failed` - Tool falhou

**Configuração:**

```json
{
  "hooks": [
    {
      "event": "message.received",
      "handler": "log_to_database",
      "async": true,
      "timeout": 5000
    },
    {
      "event": "agent.run.error",
      "handler": "notify_slack",
      "retry": 3
    }
  ]
}
```

**Implementação de Hook:**

```python
# hooks/log_to_database.py
async def handle(context):
    """Chamado quando mensagem é recebida"""
    return {
        "logged": True,
        "timestamp": now(),
        "user": context.user_id,
        "message": context.message.text[:100]
    }

# hooks/notify_slack.py
async def handle(context):
    """Chamado quando agent falha"""
    error = context.error
    await slack_client.post_message(
        channel="#errors",
        text=f"Agent failed: {error.message}"
    )
    return {"notified": True}
```

### 2. Standing Orders (Instruções Permanentes)

Diretrizes que o agent segue **sempre**, não apenas em eventos.

**Exemplos:**
- "Sempre valide entrada do usuário antes de processar"
- "Se score de confiança < 0.7, peça confirmação"
- "Nunca execute comandos desconhecidos"

**Configuração:**

```json
{
  "standing_orders": [
    {
      "rule": "Sempre validar entrada",
      "condition": "every_message",
      "action": "validate_input"
    },
    {
      "rule": "Pedir confirmação se baixa confiança",
      "condition": "confidence < 0.7",
      "action": "ask_confirmation"
    }
  ]
}
```

### 3. Webhooks (Integração Externa)

OpenClaw **chama seu servidor** quando eventos ocorrem.

**Fluxo:**

```
OpenClaw Event
     ↓
┌──────────────────┐
│  Webhook Trigger │
└──────────────────┘
     ↓
 HTTP POST para seu URL
     ↓
┌──────────────────┐
│  Seu Servidor    │
│  Processa evento │
└──────────────────┘
     ↓
Retorna resposta (opcional action)
```

**Configuração:**

```json
{
  "webhooks": [
    {
      "id": "slack-notifier",
      "url": "https://seu-servidor.com/webhooks/slack",
      "events": ["agent.run.end", "agent.run.error"],
      "headers": {
        "Authorization": "Bearer seu-token"
      },
      "retry": {
        "attempts": 3,
        "delayMs": 5000
      }
    }
  ]
}
```

**Receber Webhook:**

```python
# seu-servidor.com/webhooks/slack

from fastapi import FastAPI, Request
from cryptography import hmac, hashlib

app = FastAPI()

WEBHOOK_SECRET = "seu-secret"

@app.post("/webhooks/slack")
async def handle_webhook(request: Request):
    # 1. Validar assinatura
    signature = request.headers.get("X-Openclaw-Signature")
    body = await request.body()

    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if signature != expected_sig:
        return {"error": "Invalid signature"}, 401

    # 2. Processar evento
    event = await request.json()

    if event["type"] == "agent.run.end":
        await notify_slack(
            f"Agent completou: {event['agent_id']}"
        )
    elif event["type"] == "agent.run.error":
        await notify_slack(
            f"Agent FALHOU: {event['error']}"
        )

    return {"ok": True}
```

### 4. Cron Jobs (Agendado)

Executar tarefas em horários específicos.

**Formato Cron:**

```
┌───────────── minuto (0-59)
│ ┌───────────── hora (0-23)
│ │ ┌───────────── dia do mês (1-31)
│ │ │ ┌───────────── mês (1-12)
│ │ │ │ ┌───────────── dia da semana (0-6, 0=domingo)
│ │ │ │ │
* * * * * comando

# Exemplos:
"0 9 * * *"    → 9:00 AM todo dia
"*/5 * * * *"  → A cada 5 minutos
"0 0 * * 0"    → Meia-noite de domingo
"0 12 1 * *"   → 12:00 PM no dia 1 de cada mês
```

**Configuração:**

```json
{
  "cron_jobs": [
    {
      "id": "daily-cleanup",
      "schedule": "0 2 * * *",
      "agent": "maintenance-agent",
      "task": "cleanup_old_sessions",
      "timeout": 300
    },
    {
      "id": "hourly-health-check",
      "schedule": "0 * * * *",
      "agent": "monitor-agent",
      "task": "health_check",
      "timeout": 30
    }
  ]
}
```

---

## Part 2: Troubleshooting

### Problema: Hook Não Dispara

**Checklist:**

```
1. Hook está registrado?
   openclaw hooks list

2. Evento correto está configurado?
   openclaw hooks show <hook-id>
   → Verificar campo "events"

3. Agente está recebendo mensagens?
   openclaw sessions history user:<user-id>
   → Deve ver "message.received" events

4. Handler está correto?
   openclaw hooks test <hook-id>
   → Simular evento manualmente

5. Logs mostram erro?
   openclaw logs --module hooks --level error
   → Procurar por "hook execution failed"
```

**Debug:**

```bash
# Ativar verbose logging para hooks
openclaw config set logging.modules.hooks debug

# Ver eventos em tempo real
openclaw events watch --filter "hook*"

# Testar hook manualmente
openclaw gateway call hooks.test --id <hook-id> --event "message.received"
```

### Problema: Webhook Não Recebe Events

**Checklist:**

```
1. URL é válida e acessível?
   curl -X POST https://seu-servidor.com/webhooks
   → Deve retornar 2xx ou validar assinatura

2. Webhook está ativo?
   openclaw webhooks list
   → Verificar status="active"

3. Eventos estão configurados corretamente?
   openclaw webhooks show <webhook-id>
   → Verificar array "events"

4. Firewall permite saída do Gateway?
   (Execute do host do Gateway)
   curl -v https://seu-servidor.com/webhooks
   → Sem timeout/refused

5. Assinatura está sendo validada corretamente?
   → Verificar WEBHOOK_SECRET corresponde
   → Log da requisição recebida (headers inclusos)
```

**Debug:**

```bash
# Usar webhook.site para capturar requisições
# 1. Ir a https://webhook.site
# 2. Copiar URL gerada
# 3. Registrar no OpenClaw como webhook
# 4. Acionar evento
# 5. Ver requisição capturada (headers, body, etc)

# Ou usar ngrok localmente
ngrok http 8000
# Usar URL do ngrok como webhook URL

# Logs do Gateway
tail -f ~/.openclaw/logs/gateway.log | grep webhook
```

### Problema: Cron Job Não Executa

**Checklist:**

```
1. Cron job está registrado?
   openclaw cron list

2. Schedule está correto (syntaxe)?
   openclaw cron validate "0 9 * * *"

3. Agent existe e está disponível?
   openclaw agents list
   → Verificar que agent do cron existe

4. Timeout suficiente?
   openclaw cron show <job-id>
   → Se timeout muito curto, job falha silenciosamente

5. Logs mostram que rodou?
   openclaw logs --job <job-id> --since 24h
```

**Debug:**

```bash
# Testar cron job manualmente
openclaw cron run <job-id>

# Ver último resultado
openclaw cron last-run <job-id>

# Agendar teste em 2 minutos
openclaw cron test "*/2 * * * *" "test-agent" "test_task"
```

### Problema: Agent Toma Muito Tempo

**Checklist:**

```
1. Qual etapa demora?
   openclaw sessions show <session-id>
   → Ver timings por etapa (context load, inference, etc)

2. Context está grande?
   /context detail
   → Contar tokens do contexto atual
   → Se > 80k, problema é lá

3. Modelo é lento?
   openclaw config get models.default
   → Trocar para Haiku se é questão de latência

4. Tool está lenta?
   openclaw logs --module tools --level debug
   → Procurar por qual tool demora

5. Network latência?
   openclaw logs --search "network timeout"
```

**Soluções:**

```python
# Reduzir context
{
  "context": {
    "maxTokens": 50000,  # Reduzir
    "recencyWindow": 10  # Menos histórico
  }
}

# Usar modelo mais rápido para certos casos
if task_type == "simple_query":
    model = "claude-haiku-4-5"  # Mais rápido
else:
    model = "claude-opus-4"

# Implementar timeout
from async_timeout import timeout

async with timeout(10):  # Max 10 segundos
    result = await agent.run(task)
```

---

## Part 3: Monitoring & Observability

### Métricas Importantes

```bash
# Ver saúde do Gateway
openclaw health

# Ver fila de mensagens
openclaw queue status

# Ver sessões ativas
openclaw sessions list --active

# Ver uso de tokens (últimas 24h)
openclaw metrics tokens --since 24h

# Ver taxa de erro de agents
openclaw metrics errors-by-agent --since 24h
```

### Alertas

```json
{
  "alerts": [
    {
      "name": "high_error_rate",
      "condition": "error_rate > 0.05",
      "action": "post_to_slack",
      "message": "Error rate crítica: {{error_rate}}"
    },
    {
      "name": "queue_backup",
      "condition": "queue_size > 1000",
      "action": "email_admin",
      "message": "Fila com {{queue_size}} mensagens"
    },
    {
      "name": "webhook_failure",
      "condition": "webhook_fail_count > 5",
      "action": "disable_webhook",
      "webhook_id": "{{webhook_id}}"
    }
  ]
}
```

### Logging Estruturado

```python
import logging
import json

logger = logging.getLogger("openclaw")

logger.info("Hook executed", extra={
    "hook_id": "slack-notifier",
    "event": "message.received",
    "duration_ms": 125,
    "status": "success"
})

# Resultado nos logs:
# {
#   "timestamp": "2026-03-31T10:30:00Z",
#   "level": "INFO",
#   "message": "Hook executed",
#   "hook_id": "slack-notifier",
#   "event": "message.received",
#   "duration_ms": 125,
#   "status": "success"
# }
```

---

## Part 4: Boas Práticas

**1. Idempotência**
Hooks/webhooks podem rodar múltiplas vezes. Garanta que é seguro executar 2x:

```python
# ❌ BAD: Não idempotente
def increment_counter():
    current = get_counter()
    set_counter(current + 1)  # Se roda 2x, incrementa 2

# ✅ GOOD: Idempotente
def mark_processed(event_id):
    if already_processed(event_id):
        return
    process(event_id)
    mark_as_processed(event_id)
```

**2. Circuit Breaker para Webhooks**
Se webhook falha muito, desabilitar temporariamente:

```json
{
  "webhooks": [{
    "id": "slack-notifier",
    "url": "https://seu-servidor.com/webhooks/slack",
    "circuit_breaker": {
      "failure_threshold": 5,
      "timeout_sec": 300
    }
  }]
}
```

**3. Retry com Jitter**
Evitar thundering herd:

```python
delay = base_delay * (2 ** attempt) + random.uniform(0, jitter)
# Não: todos tentam simultaneamente
# Sim: aleatoriamente espaçados
```

**4. Timeout em Tudo**
Nunca confiar que algo completa:

```python
# Hook timeout
timeout_ms: 5000

# Agent timeout
timeout: 300

# Webhook timeout
request_timeout: 10
```

---

## Referência Rápida de Comandos

```bash
# Hooks
openclaw hooks list
openclaw hooks show <hook-id>
openclaw hooks test <hook-id>
openclaw hooks enable <hook-id>
openclaw hooks disable <hook-id>

# Webhooks
openclaw webhooks list
openclaw webhooks show <webhook-id>
openclaw webhooks test <webhook-id>
openclaw webhooks logs <webhook-id>

# Cron
openclaw cron list
openclaw cron run <job-id>
openclaw cron disable <job-id>
openclaw cron validate "0 9 * * *"

# Logs
openclaw logs --module hooks --level debug
openclaw logs --module webhooks --level error
openclaw logs --since 1h

# Métricas
openclaw metrics --summary
openclaw metrics tokens --since 24h
openclaw metrics errors-by-agent
```

---

**Precisa de ajuda específica?** Pergunte sobre qual automação ou problema!
