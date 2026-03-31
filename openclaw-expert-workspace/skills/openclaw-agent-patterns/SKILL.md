---
name: openclaw-agent-patterns
description: Advanced architectural patterns for OpenClaw agents. Use this skill when discussing multi-agent systems, supervisor patterns, delegating architectures, cross-domain specialization, agent communication, load balancing, or complex agent topologies. Provides pattern diagrams, pseudocode implementations in Python/TypeScript/Go, configuration examples, robustness strategies (timeout, retry, circuit breaker), and when to use each pattern.
---

## Padrões Avançados de Agents

Este guia cobre arquiteturas robustas para sistemas complexos.

---

## Padrão 1: Supervisor + Specialists (Recomendado)

Um supervisor orquestra múltiplos agentes especializados.

**Quando usar:**
- Tarefas multi-domínio (análise + desenvolvimento + validação)
- Necessita especialização profunda
- Quer isolamento entre concerns

**Arquitetura:**

```
User Message
     ↓
┌────────────────────────┐
│   Supervisor Agent     │
│  - Analisa requisição  │
│  - Delega para spec's  │
│  - Consolida resultado │
└────────────────────────┘
    ↓         ↓         ↓
┌──────┐ ┌──────┐ ┌──────┐
│ Dev  │ │ Data │ │ QA   │
│Agent │ │Agent │ │Agent │
└──────┘ └──────┘ └──────┘
(isolados, cada um em sua sessão)
```

**Implementação:**

```python
# supervisor.py
class SupervisorAgent:
    def __init__(self):
        self.specialists = {
            "dev": AgentSpawner("dev-agent"),
            "data": AgentSpawner("data-agent"),
            "qa": AgentSpawner("qa-agent"),
        }

    async def process(self, user_request):
        # 1. Analisar requisição
        analysis = await self.analyze_request(user_request)

        # 2. Determinar quais specialists são necessários
        required = self.determine_specialists(analysis)

        # 3. Delegar em paralelo (sessions_spawn)
        results = await asyncio.gather(
            *[
                self.specialists[spec].spawn(
                    task=analysis["subtasks"][spec],
                    session_id=f"subagent_{spec}_{uuid4()}",
                    timeout=300,
                )
                for spec in required
            ]
        )

        # 4. Validar resultados
        validated = await self.validate_results(results)

        # 5. Consolidar resposta
        return self.consolidate(validated)

    async def validate_results(self, results):
        """Verificar qualidade antes de retornar"""
        for result in results:
            if result.score < 0.7:
                # Retry com modelo diferente
                result = await self.retry_with_fallback(result)
        return results

    def consolidate(self, results):
        """Mesclar outputs de múltiplos agentes"""
        return {
            "dev_output": results["dev"],
            "data_insights": results["data"],
            "qa_validation": results["qa"],
            "combined_recommendation": self.merge_recommendations(results),
        }
```

**Configuração openclaw.json:**

```json
{
  "agents": {
    "supervisor": {
      "model": "claude-opus-4",
      "systemPrompt": "You orchestrate multiple specialist agents...",
      "tools": ["sessions_spawn"],
      "config": {
        "spawnTimeout": 300,
        "retryPolicy": {
          "attempts": 2,
          "backoffMs": 5000
        }
      }
    },
    "dev-agent": {
      "model": "claude-opus-4",
      "systemPrompt": "You are an expert developer...",
      "plugins": ["code-analyzer", "github-integration"]
    },
    "data-agent": {
      "model": "claude-opus-4",
      "systemPrompt": "You are a data scientist...",
      "plugins": ["pandas-tools", "sql-integration"]
    },
    "qa-agent": {
      "model": "claude-haiku-4-5",
      "systemPrompt": "You validate code quality..."
    }
  }
}
```

---

## Padrão 2: Pipeline Sequential

Agentes processam em cadeia, passando resultados adiante.

**Quando usar:**
- Processos com ordem definida (extract → transform → load)
- Cada etapa depende da anterior
- Simplicidade > paralelismo

**Arquitetura:**

```
Input
  ↓
┌─────────────────┐
│ Extract Agent   │ (parseia input)
└─────────────────┘
  ↓
┌─────────────────┐
│ Transform Agent │ (processa)
└─────────────────┘
  ↓
┌─────────────────┐
│ Load Agent      │ (persiste)
└─────────────────┘
  ↓
Output
```

**Pseudocódigo:**

```typescript
async function pipelineETL(input: string) {
  // Estágio 1: Extract
  const extracted = await extractor.run({
    input,
    tools: ["json-parser", "csv-reader"],
  });

  if (!extracted.success) {
    throw new Error(`Extract failed: ${extracted.error}`);
  }

  // Estágio 2: Transform
  const transformed = await transformer.run({
    input: extracted.data,
    tools: ["data-cleaner", "ml-model"],
  });

  // Estágio 3: Load
  const loaded = await loader.run({
    input: transformed.data,
    tools: ["database-writer", "cache-updater"],
  });

  return {
    stages: ["extract", "transform", "load"],
    result: loaded.data,
    metrics: {
      extractTime: extracted.duration,
      transformTime: transformed.duration,
      loadTime: loaded.duration,
    },
  };
}
```

---

## Padrão 3: Router Agent

Um agente rota requisições para diferentes handlers baseado em tipo.

**Quando usar:**
- Múltiplos tipos de requisições diferentes
- Quer escolher melhor agent para o job
- Simplificar lógica no supervisor

**Pseudocódigo:**

```go
type RouterAgent struct {
    handlers map[string]Agent
}

func (r *RouterAgent) Route(req Request) (Response, error) {
    // Classificar requisição
    category := r.classify(req)

    // Escolher handler apropriado
    handler, ok := r.handlers[category]
    if !ok {
        return nil, fmt.Errorf("unknown category: %s", category)
    }

    // Delegar
    return handler.Process(req)
}

func (r *RouterAgent) classify(req Request) string {
    switch {
    case strings.Contains(req.Text, "database"):
        return "data-agent"
    case strings.Contains(req.Text, "code"):
        return "dev-agent"
    case strings.Contains(req.Text, "test"):
        return "qa-agent"
    default:
        return "general-agent"
    }
}
```

---

## Padrão 4: Critic + Generator

Um agent gera, outro valida/critica. Loop até passar.

**Quando usar:**
- Qualidade é crítica
- Quer múltiplas iterações
- Feedback loop importante

**Pseudocódigo:**

```python
async def generate_and_critique_loop(
    prompt: str,
    max_iterations: int = 3
) -> str:
    current_output = None

    for iteration in range(max_iterations):
        # Geração
        if current_output is None:
            current_output = await generator.run(prompt)
        else:
            current_output = await generator.run(
                f"{prompt}\n\nFeedback anterior: {feedback}"
            )

        # Crítica
        critique = await critic.run(
            f"Avalie isso:\n{current_output}"
        )

        # Checar se passou
        if critique.score >= 0.85:
            return current_output

        # Feedback para próxima iteração
        feedback = critique.suggestions

    # Retornar melhor versão
    return current_output
```

---

## Padrão 5: Cache + Fallback

Tentar responder rápido com cache, fallback para computação pesada.

**Quando usar:**
- Query pode ser respondida de cache
- Quer latência baixa
- Custo importa (cache = mais barato)

**Pseudocódigo:**

```typescript
async function cachedAgent(query: string) {
  // 1. Tentar cache
  const cached = await cache.get(query);
  if (cached && cached.age < 3600) {
    return {
      result: cached.value,
      source: "cache",
      latency: "low",
    };
  }

  // 2. Fallback para agente rápido (Haiku)
  const fastResponse = await agent.run({
    query,
    model: "claude-haiku-4-5",
    timeout: 10,
  });

  // 3. Se rápido falha, usar modelo pesado
  if (!fastResponse.success) {
    const fullResponse = await agent.run({
      query,
      model: "claude-opus-4",
      timeout: 60,
    });

    // Cache o resultado
    await cache.set(query, fullResponse.result, ttl: 3600);
    return fullResponse;
  }

  // Cache resposta rápida também
  await cache.set(query, fastResponse.result, ttl: 7200);
  return fastResponse;
}
```

---

## Robustez: Error Handling & Retry

**Timeout Protection:**

```python
from async_timeout import timeout as async_timeout

async def agent_with_timeout(agent, task, timeout_sec=30):
    try:
        async with async_timeout(timeout_sec):
            return await agent.run(task)
    except TimeoutError:
        # Fallback: modelo mais rápido
        return await agent.run(
            task,
            model="claude-haiku-4-5"
        )
```

**Circuit Breaker (evitar cascata de falhas):**

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout_sec=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "closed"  # closed, open, half-open
        self.timeout_sec = timeout_sec

    async def call(self, agent, task):
        if self.state == "open":
            raise Exception("Circuit breaker is open")

        try:
            result = await agent.run(task)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                # Agendarrecheck após timeout
                asyncio.create_task(self.half_open_after(self.timeout_sec))
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = "closed"

    def on_failure(self):
        self.failure_count += 1

    async def half_open_after(self, delay_sec):
        await asyncio.sleep(delay_sec)
        self.state = "half-open"
        self.failure_count = 0
```

**Retry com Backoff Exponencial:**

```python
async def retry_with_backoff(
    agent, task,
    attempts=3,
    base_delay=1.0,
    max_delay=30.0
):
    for attempt in range(attempts):
        try:
            return await agent.run(task)
        except Exception as e:
            if attempt == attempts - 1:
                raise

            # Backoff exponencial com jitter
            delay = min(
                base_delay * (2 ** attempt) + random.uniform(0, 1),
                max_delay
            )
            await asyncio.sleep(delay)
```

---

## Comparação de Padrões

| Padrão | Paralelismo | Complexidade | Latência | Uso |
|--------|-------------|-------------|----------|-----|
| Supervisor | Alto | Alta | Média | Multi-domain |
| Pipeline | Baixo | Baixa | Alta | Sequential |
| Router | Médio | Média | Baixa | Type-based |
| Critic Loop | Baixo | Média | Alta | Quality critical |
| Cache+Fallback | Alto | Média | Muito Baixa | Cost sensitive |

---

## Checklist de Robustez

- [ ] Timeout proteção em cada spawned agent
- [ ] Retry policy com backoff exponencial
- [ ] Circuit breaker para falhas cascata
- [ ] Validação de outputs antes de usar
- [ ] Fallback para modelo mais rápido/barato
- [ ] Logging detalhado de cada etapa
- [ ] Monitoramento de latência por etapa
- [ ] SLA verificação (tempo máximo)
- [ ] Metrics coleta (tokens, duração, retries)
- [ ] Testes de failure injection

Qualquer dúvida sobre padrões, pergunte!
