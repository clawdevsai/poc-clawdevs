# Sistema Multi-Agent no OpenClaw: Padrão Delegate Architecture

## Pergunta
Preciso de um sistema multi-agent no OpenClaw onde um agente supervisor delega tarefas para 3 agentes especializados. Qual padrão você recomenda? E como estruturar para que seja robusto?

## Resposta

### Padrão Recomendado: Delegate Architecture com Sub-Agent Spawning

O OpenClaw oferece suporte nativo para este padrão através da ferramenta **`sessions_spawn`**, que permite que um agente supervisor lance runs isoladas de sub-agentes. Esta é a arquitetura mais robusta para sistemas multi-agent.

### Arquitetura de Alto Nível

```
┌─────────────────────────────────┐
│   Agente Supervisor (Main)      │
│  - Recebe requisição do usuário │
│  - Analisa e roteia para        │
│  - Monitora progresso           │
│  - Consolida resultados         │
└────────┬────────────────────────┘
         │
    ┌────┼────┐
    │    │    │
    ▼    ▼    ▼
 ┌──┐ ┌──┐ ┌──┐
 │S1│ │S2│ │S3│  Sub-agents (Isolated Sessions)
 └──┘ └──┘ └──┘
 Spec Code Data
 AnalyEng  Sci
 ist      ineer
```

### 1. Configuração de Agents (openclaw.json)

```json5
{
  "agents": {
    "list": [
      {
        "id": "supervisor",
        "workspace": "/path/to/workspace/supervisor",
        "tools": {
          "allow": ["sessions_spawn", "sessions_history", "sessions_send"],
          "deny": []
        },
        "sandbox": { "mode": "off" }
      },
      {
        "id": "data-engineer",
        "workspace": "/path/to/workspace/data-engineer",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read", "exec", "write"],
          "deny": ["sessions_spawn"]
        }
      },
      {
        "id": "code-specialist",
        "workspace": "/path/to/workspace/code-specialist",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read", "exec", "write"],
          "deny": ["sessions_spawn"]
        }
      },
      {
        "id": "science-engineer",
        "workspace": "/path/to/workspace/science-engineer",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read", "exec", "write"],
          "deny": ["sessions_spawn"]
        }
      }
    ]
  }
}
```

### 2. Workspace do Supervisor (AGENTS.md)

```markdown
# Supervisor Agent - Multi-Agent Delegation System

## Responsabilidades
- Receber requisições do usuário
- Analisar e classificar tarefas
- Delegar para agentes especializados
- Monitorar progresso
- Consolidar e validar resultados

## Agentes Especializados Disponíveis

### data-engineer
- Especialista em processamento de dados
- Manipulação de estruturas de dados
- Análise e transformação
- ETL pipelines

### code-specialist
- Desenvolvimento de software
- Refatoração e otimização
- Code review e debugging
- Padrões de design

### science-engineer
- Análise científica e matemática
- Modelagem quantitativa
- Validação de hipóteses
- Computação científica

## Protocolo de Delegação

1. Analise a requisição do usuário
2. Classifique em domínios: DATA, CODE, SCIENCE
3. Para cada domínio identificado:
   - Use `sessions_spawn` para criar tarefa isolada
   - Forneça instruções claras
   - Aguarde resultado
4. Após todas as tarefas:
   - Consolide resultados
   - Valide coerência
   - Retorne resposta unificada

## Instruções para Sub-Agentes

Cada sub-agente recebe um prompt estruturado com:
- TAREFA: descrição clara
- CONTEXTO: background necessário
- SAÍDAS: formato esperado
- RESTRIÇÕES: limites e regras
```

### 3. Pseudocódigo da Lógica Delegate (Supervisor)

```typescript
// ============================================
// DELEGATE ARCHITECTURE - PSEUDOCÓDIGO
// ============================================

class SupervisorAgent {
  // Etapa 1: Análise de Requisição
  async analyzeRequest(userMessage: string): Promise<DelegateTask[]> {
    // Determina quais agentes são necessários
    const analysis = await this.model.prompt(`
      Analise esta requisição e determine quais agentes são necessários:
      - data-engineer (processamento, transformação, análise de dados)
      - code-specialist (código, arquitetura, otimização)
      - science-engineer (matemática, ciência, modelagem)

      Requisição: "${userMessage}"

      Retorne JSON com:
      {
        "tasks": [
          {
            "agent": "agent-id",
            "priority": "high|medium|low",
            "dependencies": ["task-ids"],
            "prompt": "instruções específicas"
          }
        ],
        "parallelizable": true/false
      }
    `);

    return analysis.tasks;
  }

  // Etapa 2: Delegação Paralela
  async delegateToSubAgents(tasks: DelegateTask[]): Promise<TaskResult[]> {
    // Se tarefas são parallelizáveis, execute em paralelo
    if (tasks.parallelizable) {
      return Promise.all(
        tasks.map(task => this.spawnSubAgent(task))
      );
    }

    // Caso contrário, respeite dependências
    const results = [];
    for (const task of tasks) {
      // Aguarde dependências
      const dependencies = await Promise.all(
        task.dependencies.map(depId =>
          results.find(r => r.taskId === depId)
        )
      );

      // Contexto inclui resultados de dependências
      const contextFromDeps = dependencies
        .map(r => `## Resultado de ${r.taskId}\n${r.output}`)
        .join('\n\n');

      const result = await this.spawnSubAgent(task, contextFromDeps);
      results.push(result);
    }

    return results;
  }

  // Etapa 3: Spawn Sub-Agent (Tool Call)
  async spawnSubAgent(
    task: DelegateTask,
    additionalContext?: string
  ): Promise<TaskResult> {
    // Constrói prompt estruturado
    const subAgentPrompt = `
## TAREFA DELEGADA: ${task.agent}

### OBJETIVO
${task.prompt}

### CONTEXTO DO SUPERVISOR
${additionalContext ? `
${additionalContext}
` : ''}

### INSTRUÇÕES CRÍTICAS
1. Você é um sub-agente especializado em seu domínio
2. Forneça resposta completa e auto-contida
3. Inclua raciocínio e passos
4. Valide resultados antes de retornar
5. Se encontrar ambiguidade, faça suposições razoáveis e documente

### FORMATO DE SAÍDA
Estruture sua resposta com:
- ANÁLISE: seu entendimento do problema
- SOLUÇÃO: implementação/resposta
- VALIDAÇÃO: como você validou
- CONSIDERAÇÕES: edge cases ou limitações
    `;

    // Chama sessions_spawn (ferramenta nativa do OpenClaw)
    const result = await this.tools.sessions_spawn({
      task: subAgentPrompt,
      model: this.selectModelForAgent(task.agent),
      sandbox: { visibility: "self" },
      runTimeoutSeconds: 300,
      attachments: [] // passar arquivos se necessário
    });

    return {
      taskId: task.agent,
      agentId: task.agent,
      output: result.text,
      tokens: result.usage,
      status: result.ok ? "success" : "failed"
    };
  }

  // Etapa 4: Consolidação de Resultados
  async consolidateResults(results: TaskResult[]): Promise<FinalResponse> {
    // Agrupa resultados por agente
    const byAgent = {};
    results.forEach(r => {
      byAgent[r.agentId] = r.output;
    });

    // Realiza consolidação inteligente
    const consolidatedPrompt = `
Você é o Supervisor. Os sub-agentes completaram suas tarefas:

${Object.entries(byAgent)
  .map(([agent, output]) => `
### Resultado de ${agent}
${output}
`)
  .join('\n\n')}

## TAREFA DE CONSOLIDAÇÃO

1. INTEGRAÇÃO: combine os resultados de forma coerente
2. VALIDAÇÃO: procure inconsistências ou conflitos
3. COMPLETUDE: verifique se todos os aspectos foram cobertos
4. REFINAMENTO: melhore a resposta final unificando insights
5. RESPOSTA FINAL: articule conclusão clara e acionável

Forneça:
- RESPOSTA CONSOLIDADA: síntese dos resultados
- CONFLITOS RESOLVIDOS: qualquer divergência encontrada
- PRÓXIMOS PASSOS: recomendações
    `;

    const consolidated = await this.model.prompt(consolidatedPrompt);

    return {
      finalResponse: consolidated,
      sourceResults: results,
      consolidationNotes: "Resultados consolidados de 3 sub-agentes"
    };
  }

  // Etapa 5: Seleção de Modelo por Domínio
  selectModelForAgent(agentId: string): string {
    const modelMap = {
      "data-engineer": "claude-opus",      // Modelo mais capaz
      "code-specialist": "claude-sonnet",  // Balanceado
      "science-engineer": "claude-opus"    // Requer raciocínio avançado
    };

    return modelMap[agentId] || "claude-sonnet";
  }

  // ORQUESTRAÇÃO PRINCIPAL
  async handleUserRequest(userMessage: string): Promise<string> {
    console.log("FASE 1: Analisando requisição...");
    const tasks = await this.analyzeRequest(userMessage);

    console.log(`FASE 2: Delegando ${tasks.length} tarefas...`);
    const results = await this.delegateToSubAgents(tasks);

    console.log("FASE 3: Consolidando resultados...");
    const final = await this.consolidateResults(results);

    console.log("FASE 4: Retornando resposta...");
    return final.finalResponse;
  }
}

// ============================================
// TIPOS E INTERFACES
// ============================================

interface DelegateTask {
  agent: string;           // agent-id
  priority: "high" | "medium" | "low";
  dependencies: string[];  // task-ids de dependências
  prompt: string;          // instruções para sub-agente
}

interface TaskResult {
  taskId: string;
  agentId: string;
  output: string;
  tokens: { input: number; output: number };
  status: "success" | "failed";
}

interface FinalResponse {
  finalResponse: string;
  sourceResults: TaskResult[];
  consolidationNotes: string;
}
```

### 4. Robustez: Padrões de Tratamento de Erros

```typescript
// RETRY COM BACKOFF
async function spawnWithRetry(
  task: DelegateTask,
  maxAttempts: number = 3
): Promise<TaskResult> {
  let lastError;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await spawnSubAgent(task);
    } catch (error) {
      lastError = error;

      if (attempt < maxAttempts) {
        const delayMs = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s
        console.log(`Tentativa ${attempt} falhou. Aguardando ${delayMs}ms...`);
        await sleep(delayMs);
      }
    }
  }

  throw new Error(
    `Sub-agente falhou após ${maxAttempts} tentativas: ${lastError.message}`
  );
}

// TIMEOUT PROTEÇÃO
async function executeWithTimeout(
  promise: Promise<any>,
  timeoutMs: number
): Promise<any> {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(
        () => reject(new Error(`Timeout após ${timeoutMs}ms`)),
        timeoutMs
      )
    )
  ]);
}

// VALIDAÇÃO DE SAÍDA
function validateSubAgentOutput(output: string, expectedFormat: string): boolean {
  // Verifica se output segue formato esperado
  // - Contém seções ANÁLISE, SOLUÇÃO, VALIDAÇÃO
  // - Não contém tokens suspeitos
  // - Tamanho razoável

  const sections = ['ANÁLISE', 'SOLUÇÃO', 'VALIDAÇÃO'];
  return sections.every(s => output.includes(s));
}

// FALLBACK: Se sub-agente falhar, tente agente alternativo
async function delegateWithFallback(
  task: DelegateTask,
  fallbackAgents: string[]
): Promise<TaskResult> {
  const agents = [task.agent, ...fallbackAgents];

  for (const agent of agents) {
    try {
      return await spawnSubAgent({ ...task, agent });
    } catch (error) {
      console.log(`${agent} falhou, tentando próximo...`);
    }
  }

  throw new Error("Todos os agentes falharam para esta tarefa");
}
```

### 5. Configuração de Sessão para Multi-Agent

```json5
{
  "session": {
    // Cada supervisor e sub-agent tem sua própria sessão
    "dmScope": "per-channel-peer",

    // Isolamento de sandbox protege state
    "resetByType": {
      "direct": {
        "resetAt": "04:00",
        "idleMinutes": 1440
      }
    },

    // Subagentes herdados clampeiam visibilidade
    "sandboxes": {
      "spawn": {
        "visibility": "self"  // Sub-agents veem só sua própria sessão
      }
    }
  }
}
```

### 6. Exemplo Real: Requisição Multi-Domain

```markdown
## Cenário: "Otimize um pipeline de ML com 3 focos"

USUÁRIO: "Temos um pipeline de machine learning lento.
Preciso de: (1) análise dos dados atuais, (2) refatoração
do código Python, (3) modelo matemático alternativo"

### Fase 1: Análise do Supervisor
✓ data-engineer: análise dos dados
✓ code-specialist: refatoração Python
✓ science-engineer: alternativa matemática
✓ Parallelizáveis? SIM

### Fase 2-3: Delegação Paralela
┌─ Task 1: data-engineer ──────────────┐
│ "Analise distribuição dos dados,     │
│  valores faltantes, outliers,        │
│  e recomende limpeza"                │
└──────────────────────────────────────┘

┌─ Task 2: code-specialist ────────────┐
│ "Revise pipeline.py, identifique     │
│  gargalos, refatore com async/multiprocessing" │
└──────────────────────────────────────┘

┌─ Task 3: science-engineer ───────────┐
│ "Contexto: pipeline atual usa regressão. │
│  Explore 2 alternativas: (a) ensemble,   │
│  (b) modelo não-paramétrico. Benchmark."│
└──────────────────────────────────────┘

### Fase 4: Consolidação
✓ data-engineer identificou 15% outliers → remover
✓ code-specialist sugeriu asyncio → 3x speedup
✓ science-engineer recomenda ensemble → 12% acurácia

RESPOSTA FINAL: "3 otimizações complementares..."
```

### 7. Checklist de Robustez

- [x] **Isolamento**: Sub-agentes em sessões separadas (sandbox)
- [x] **Timeouts**: Cada spawn tem `runTimeoutSeconds: 300`
- [x] **Retry Logic**: Falhas em sub-agente com backoff exponencial
- [x] **Validação**: Output de cada sub-agente validado antes consolidação
- [x] **Monitoramento**: Logs detalhados de cada fase
- [x] **Fallback**: Agentes alternativos se principal falhar
- [x] **Coerência**: Prompt estruturado para evitar alucinações
- [x] **Consolidação**: Supervisor resolve conflitos entre sub-agentes
- [x] **Tool Access**: Ferramenta `sessions_spawn` com visibilidade clampeada

## Conclusão

A **Delegate Architecture com `sessions_spawn`** é o padrão nativo e mais robusto do OpenClaw para multi-agent orchestration. Oferece:

1. **Isolamento completo** entre agentes
2. **Execução paralela** quando possível
3. **Tratamento de falhas** com retry automático
4. **Contexto estruturado** para evitar erros
5. **Consolidação inteligente** de resultados
6. **Auditoria e rastreamento** total
