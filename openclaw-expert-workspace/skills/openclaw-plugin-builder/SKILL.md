---
name: openclaw-plugin-builder
description: Step-by-step guide to building OpenClaw plugins. Use this skill whenever the user wants to create a plugin, integrate a new tool/API into OpenClaw, implement custom hooks, or extend OpenClaw functionality. Provides project structure, manifest examples, hook implementations, tool definitions with JSON Schema, and testing strategies. Use proactively when user mentions building integrations, custom tools, external API connections, or extending OpenClaw capabilities.
compatibility: web-fetch (optional for searching plugin examples)
---

## Criar um Plugin OpenClaw do Zero

Um **plugin** estende OpenClaw com novas ferramentas/integrações. Exemplos:
- **weather-plugin**: Expõe tool `get_weather(city)`
- **database-plugin**: Expõe `query_db`, `save_record`
- **slack-plugin**: Integração com Slack

Vou guiar você passo a passo.

---

## Step 1: Estrutura de Pastas

```
meu-plugin/
├── SKILL.md                      # Metadados do plugin (obrigatório)
├── manifest.json                 # Configuração do plugin
├── src/
│   ├── index.ts                  # Ponto de entrada principal
│   ├── hooks/
│   │   ├── before_model_resolve.ts
│   │   ├── before_tool_call.ts
│   │   └── after_tool_call.ts
│   ├── tools/
│   │   ├── weather.ts            # Definiçãodas ferramentas
│   │   ├── database.ts
│   │   └── schemas.ts            # JSON Schemas
│   └── utils/
│       ├── api_client.ts         # Cliente HTTP com retry
│       ├── logger.ts
│       └── config.ts
├── tests/
│   ├── unit/
│   │   └── tools.test.ts
│   └── integration/
│       └── hooks.test.ts
├── package.json
├── tsconfig.json
└── README.md
```

---

## Step 2: SKILL.md do Plugin

Arquivo obrigatório que descreve o plugin:

```yaml
---
name: meu-plugin
version: 1.0.0
description: "Plugin que integra com API externa de weather"
author: "Seu Nome"
keywords: ["weather", "integration", "api"]
license: MIT
dependencies:
  - openclaw >= 2.0.0
  - typescript >= 5.0
permissions:
  - network_access
  - environment_variables
  - file_write
---

## O Que Este Plugin Faz

Fornece ferramentas para obter dados de clima em tempo real.

## Instalação

```bash
openclaw plugin install ./meu-plugin
```

## Uso

Adicione ao seu `openclaw.json`:

```json
{
  "plugins": ["meu-plugin"]
}
```

## Configuração

Variáveis de ambiente:
- `WEATHER_API_KEY`: Sua chave da API OpenWeatherMap

## Tools Disponíveis

- `get_weather(city: string)` - Obter previsão atual
- `get_forecast(city: string, days: int)` - Previsão para N dias
```

---

## Step 3: manifest.json

Define como o plugin carrega e qual é sua interface:

```json
{
  "id": "meu-plugin",
  "name": "My Weather Plugin",
  "version": "1.0.0",
  "description": "Integração com OpenWeatherMap",
  "entry": "./src/index.ts",
  "hooks": [
    {
      "event": "before_model_resolve",
      "handler": "beforeModelResolve"
    },
    {
      "event": "after_tool_call",
      "handler": "afterToolCall"
    }
  ],
  "tools": [
    {
      "name": "get_weather",
      "description": "Obter previsão de clima para uma cidade",
      "schema": {
        "type": "object",
        "properties": {
          "city": {
            "type": "string",
            "description": "Nome da cidade"
          },
          "units": {
            "type": "string",
            "enum": ["metric", "imperial"],
            "default": "metric"
          }
        },
        "required": ["city"]
      }
    }
  ],
  "config": {
    "apiKey": {
      "type": "string",
      "description": "Chave da API OpenWeatherMap",
      "required": true,
      "sensitive": true
    },
    "cacheEnabled": {
      "type": "boolean",
      "default": true
    },
    "cacheTTL": {
      "type": "number",
      "default": 3600,
      "description": "TTL do cache em segundos"
    }
  }
}
```

---

## Step 4: Definir Ferramentas (Tools)

As ferramentas são o que o agente pode chamar. Implemente cada tool:

```typescript
// src/tools/weather.ts

import Zod from "zod";
import { APIClient } from "../utils/api_client";

// Validação com Zod
const GetWeatherInput = Zod.object({
  city: Zod.string().min(1),
  units: Zod.enum(["metric", "imperial"]).default("metric"),
});

type GetWeatherInput = Zod.infer<typeof GetWeatherInput>;

export class WeatherTool {
  private client: APIClient;

  constructor(apiKey: string) {
    this.client = new APIClient({
      baseURL: "https://api.openweathermap.org/data/2.5",
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
      retryPolicy: {
        attempts: 3,
        backoffMs: 1000,
      },
    });
  }

  async execute(input: unknown): Promise<{
    city: string;
    temperature: number;
    condition: string;
  }> {
    // Validar input
    const validated = GetWeatherInput.parse(input);

    // Chamar API com retry automático
    const response = await this.client.get("/weather", {
      params: {
        q: validated.city,
        units: validated.units,
      },
    });

    return {
      city: validated.city,
      temperature: response.data.main.temp,
      condition: response.data.weather[0].main,
    };
  }
}
```

---

## Step 5: Implementar Hooks

Hooks permitem interceptar eventos no agent loop:

```typescript
// src/hooks/before_model_resolve.ts

export async function beforeModelResolve(context: {
  sessionKey: string;
  config: any;
  model: string;
}): Promise<{
  model?: string;
  prependContext?: string;
}> {
  // Exemplo: usar modelo diferente para tarefas de weather
  if (context.config.forceWeatherModel) {
    return {
      model: "claude-haiku-4-5", // Mais rápido para weather
    };
  }

  return {};
}

// src/hooks/after_tool_call.ts

export async function afterToolCall(context: {
  toolName: string;
  input: any;
  output: any;
  duration: number;
}): Promise<void> {
  // Log de ferramentas chamadas
  console.log(`Tool ${context.toolName} executed in ${context.duration}ms`);

  // Exemplo: cache o resultado
  if (context.toolName === "get_weather") {
    await cacheWeatherResult(context.input, context.output);
  }
}
```

---

## Step 6: Utilitários Importantes

**API Client com Retry:**

```typescript
// src/utils/api_client.ts

export class APIClient {
  async get(url: string, options: any) {
    return this.requestWithRetry(() =>
      fetch(`${this.baseURL}${url}`, {
        method: "GET",
        headers: this.headers,
        ...options,
      })
    );
  }

  private async requestWithRetry(
    fn: () => Promise<Response>,
    attempt = 1
  ): Promise<any> {
    try {
      const response = await fn();

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return {
        status: response.status,
        data: await response.json(),
      };
    } catch (error) {
      if (attempt < this.retryPolicy.attempts) {
        const delayMs =
          this.retryPolicy.backoffMs * Math.pow(2, attempt - 1);
        await new Promise((r) => setTimeout(r, delayMs));
        return this.requestWithRetry(fn, attempt + 1);
      }
      throw error;
    }
  }
}
```

---

## Step 7: Ponto de Entrada (index.ts)

O arquivo principal que OpenClaw carrega:

```typescript
// src/index.ts

import { WeatherTool } from "./tools/weather";
import * as hooks from "./hooks";

export interface PluginConfig {
  apiKey: string;
  cacheEnabled: boolean;
  cacheTTL: number;
}

export async function initialize(config: PluginConfig) {
  const weatherTool = new WeatherTool(config.apiKey);

  return {
    // Registrar ferramentas
    tools: {
      get_weather: (input) => weatherTool.execute(input),
    },

    // Registrar hooks
    hooks: {
      before_model_resolve: hooks.beforeModelResolve,
      after_tool_call: hooks.afterToolCall,
    },

    // Metadados
    metadata: {
      name: "meu-plugin",
      version: "1.0.0",
    },
  };
}
```

---

## Step 8: Testes

**Testes Unitários:**

```typescript
// tests/unit/tools.test.ts

import { WeatherTool } from "../../src/tools/weather";

describe("WeatherTool", () => {
  let tool: WeatherTool;

  beforeEach(() => {
    tool = new WeatherTool("test-api-key");
  });

  test("should fetch weather for valid city", async () => {
    const result = await tool.execute({
      city: "São Paulo",
      units: "metric",
    });

    expect(result).toHaveProperty("temperature");
    expect(result).toHaveProperty("condition");
    expect(result.city).toBe("São Paulo");
  });

  test("should retry on API failure", async () => {
    // Mock API para simular falha
    const retries = await tool.getRetryCount();
    expect(retries).toBeGreaterThan(0);
  });

  test("should throw on invalid input", async () => {
    await expect(
      tool.execute({ city: "" }) // City vazio
    ).rejects.toThrow();
  });
});
```

**Testes de Integração:**

```typescript
// tests/integration/hooks.test.ts

import { initialize } from "../../src/index";

describe("Plugin Integration", () => {
  test("should load plugin successfully", async () => {
    const plugin = await initialize({
      apiKey: "test-key",
      cacheEnabled: true,
      cacheTTL: 3600,
    });

    expect(plugin.tools).toHaveProperty("get_weather");
    expect(plugin.hooks).toHaveProperty("before_model_resolve");
  });

  test("should call before_model_resolve hook", async () => {
    const plugin = await initialize({
      apiKey: "test-key",
      cacheEnabled: true,
      cacheTTL: 3600,
    });

    const result = await plugin.hooks.before_model_resolve({
      sessionKey: "user:123",
      config: {},
      model: "claude-opus-4",
    });

    expect(result).toHaveProperty("model");
  });
});
```

---

## Step 9: Instalação & Uso

**Instalar o plugin:**

```bash
openclaw plugin install ./meu-plugin
```

**Usar no agent:**

```json
{
  "name": "meu-agente",
  "plugins": ["meu-plugin"],
  "config": {
    "meu-plugin": {
      "apiKey": "${WEATHER_API_KEY}",
      "cacheEnabled": true
    }
  }
}
```

**Agora o agent pode chamar:**

```
User: "Como está o clima em São Paulo?"
Agent: [calls get_weather tool]
Agent: "Em São Paulo está 25°C com céu nublado"
```

---

## Checklist de Implementação

- [ ] Estrutura de pastas criada
- [ ] SKILL.md preenchido com metadados
- [ ] manifest.json com tools e hooks
- [ ] Tools implementadas com validação
- [ ] Hooks implementados (before_model_resolve, after_tool_call)
- [ ] API client com retry policy
- [ ] Testes unitários escritos
- [ ] Testes de integração escritos
- [ ] package.json e tsconfig.json configurados
- [ ] Documentação no README.md
- [ ] Plugin testado localmente
- [ ] Plugin pronto para publicar

---

## Próximos Passos

1. **Publicar no ClawhHub**: Repositório oficial de plugins
2. **Adicionar mais tools**: Expandir funcionalidades
3. **Implementar mais hooks**: `before_tool_call`, `after_model_resolve`, etc
4. **Adicionar cache**: Melhorar performance
5. **Rate limiting**: Proteger API externa

Pronto! Seu plugin estará pronto para uso em produção.
