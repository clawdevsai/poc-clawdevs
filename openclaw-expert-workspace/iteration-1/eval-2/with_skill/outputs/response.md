# Guia Completo: Construindo um Plugin OpenClaw do Zero

## Introdução

Este guia mostra como construir um plugin OpenClaw que integra com uma API externa. Usaremos como exemplo um plugin que conecta a um serviço de previsão do tempo externo.

---

## 1. Estrutura de Pastas do Plugin

```
my-weather-plugin/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                 # Ponto de entrada (plugin registration)
│   ├── types.ts                 # Tipos TypeScript
│   ├── provider/
│   │   ├── weather-api.ts       # Client da API externa
│   │   └── config.ts            # Configurações e validação
│   ├── tools/
│   │   ├── get-weather.ts       # Definição da ferramenta
│   │   └── forecast.ts          # Ferramenta adicional
│   ├── hooks/
│   │   ├── before-model-resolve.ts
│   │   └── after-tool-call.ts
│   └── utils/
│       ├── retry.ts             # Lógica de retry
│       └── formatting.ts        # Formatação de respostas
├── dist/                         # Saída compilada
├── tests/
│   └── weather-api.test.ts
└── README.md
```

---

## 2. Etapa 1: Setup do Projeto

### 2.1 package.json

```json
{
  "name": "@myorg/openclaw-weather-plugin",
  "version": "1.0.0",
  "description": "OpenClaw plugin para integração com API de previsão do tempo",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "test": "jest",
    "lint": "eslint src/**"
  },
  "peerDependencies": {
    "openclaw": "^2026.1.6"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.2.0"
  }
}
```

### 2.2 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020"],
    "declaration": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": ["src"],
  "exclude": ["node_modules", "tests"]
}
```

---

## 3. Etapa 2: Tipos e Interfaces

### 3.1 src/types.ts

```typescript
// Tipos de resposta da API externa
export interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  condition: string;
  windSpeed: number;
  lastUpdated: Date;
}

export interface ForecastData {
  location: string;
  forecast: ForecastDay[];
}

export interface ForecastDay {
  date: string;
  highTemp: number;
  lowTemp: number;
  condition: string;
  precipitation: number;
}

// Tipos de configuração do plugin
export interface WeatherPluginConfig {
  apiKey: string;
  apiUrl: string;
  cacheSeconds: number;
  maxRetries: number;
  retryDelayMs: number;
}

// Tipos de ferramenta (tool schema)
export interface GetWeatherParams {
  location: string;
  units?: "celsius" | "fahrenheit";
}

export interface ForecastParams {
  location: string;
  days: number;
  units?: "celsius" | "fahrenheit";
}
```

---

## 4. Etapa 3: Client da API Externa

### 4.1 src/provider/weather-api.ts

```typescript
import axios, { AxiosInstance } from "axios";
import { z } from "zod";
import { WeatherData, ForecastData, WeatherPluginConfig } from "../types";
import { retryWithBackoff } from "../utils/retry";

// Schema de validação para respostas da API
const WeatherResponseSchema = z.object({
  location: z.string(),
  temperature: z.number(),
  humidity: z.number(),
  condition: z.string(),
  windSpeed: z.number(),
  lastUpdated: z.string(),
});

export class WeatherAPIProvider {
  private client: AxiosInstance;
  private config: WeatherPluginConfig;
  private cache: Map<string, { data: WeatherData; timestamp: number }> = new Map();

  constructor(config: WeatherPluginConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.apiUrl,
      timeout: 10000,
      headers: {
        "X-API-Key": config.apiKey,
        "Content-Type": "application/json",
      },
    });
  }

  /**
   * Obtém dados meteorológicos atuais para uma localização
   * Implementa cache em memória e retry com backoff exponencial
   */
  async getWeather(location: string): Promise<WeatherData> {
    // Verifica cache
    const cached = this.cache.get(location);
    if (cached && Date.now() - cached.timestamp < this.config.cacheSeconds * 1000) {
      return cached.data;
    }

    // Faz request com retry
    const data = await retryWithBackoff(
      async () => {
        const response = await this.client.get("/current", {
          params: { location, format: "json" },
        });

        // Valida resposta com Zod
        const validated = WeatherResponseSchema.parse(response.data);

        return {
          location: validated.location,
          temperature: validated.temperature,
          humidity: validated.humidity,
          condition: validated.condition,
          windSpeed: validated.windSpeed,
          lastUpdated: new Date(validated.lastUpdated),
        };
      },
      this.config.maxRetries,
      this.config.retryDelayMs
    );

    // Armazena em cache
    this.cache.set(location, { data, timestamp: Date.now() });

    return data;
  }

  /**
   * Obtém previsão para múltiplos dias
   */
  async getForecast(location: string, days: number): Promise<ForecastData> {
    const cacheKey = `forecast:${location}:${days}`;
    const cached = this.cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this.config.cacheSeconds * 1000) {
      return cached.data as unknown as ForecastData;
    }

    const data = await retryWithBackoff(
      async () => {
        const response = await this.client.get("/forecast", {
          params: { location, days, format: "json" },
        });

        return {
          location: response.data.location,
          forecast: response.data.forecast.map((day: any) => ({
            date: day.date,
            highTemp: day.high,
            lowTemp: day.low,
            condition: day.condition,
            precipitation: day.precipitation || 0,
          })),
        };
      },
      this.config.maxRetries,
      this.config.retryDelayMs
    );

    this.cache.set(cacheKey, { data, timestamp: Date.now() });

    return data;
  }

  /**
   * Limpa cache expirado
   */
  clearExpiredCache(): void {
    const now = Date.now();
    const ttl = this.config.cacheSeconds * 1000;

    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > ttl) {
        this.cache.delete(key);
      }
    }
  }
}
```

### 4.2 src/provider/config.ts

```typescript
import { z } from "zod";
import { WeatherPluginConfig } from "../types";

// Schema de validação para configuração do plugin
const ConfigSchema = z.object({
  apiKey: z.string().min(1, "apiKey é obrigatório"),
  apiUrl: z.string().url("apiUrl deve ser uma URL válida").default("https://api.weather.example.com"),
  cacheSeconds: z.number().positive().default(300),
  maxRetries: z.number().nonnegative().default(3),
  retryDelayMs: z.number().positive().default(1000),
});

export function validateConfig(config: unknown): WeatherPluginConfig {
  return ConfigSchema.parse(config);
}

export function getConfigFromEnv(): WeatherPluginConfig {
  return validateConfig({
    apiKey: process.env.WEATHER_API_KEY,
    apiUrl: process.env.WEATHER_API_URL || "https://api.weather.example.com",
    cacheSeconds: Number(process.env.WEATHER_CACHE_SECONDS || 300),
    maxRetries: Number(process.env.WEATHER_MAX_RETRIES || 3),
    retryDelayMs: Number(process.env.WEATHER_RETRY_DELAY || 1000),
  });
}
```

---

## 5. Etapa 4: Definição de Ferramentas (Tools)

### 5.1 src/tools/get-weather.ts

```typescript
import { WeatherAPIProvider } from "../provider/weather-api";
import { GetWeatherParams, WeatherData } from "../types";
import { formatWeatherResponse } from "../utils/formatting";

/**
 * Esquema JSON Schema para a ferramenta get-weather
 * Este é o esquema que será injetado no system prompt do OpenClaw
 */
export const GetWeatherSchema = {
  name: "get_weather",
  description: "Obtém informações meteorológicas atuais para uma localização específica",
  input_schema: {
    type: "object",
    properties: {
      location: {
        type: "string",
        description: "Nome da cidade ou localização (ex: 'São Paulo, Brasil')",
      },
      units: {
        type: "string",
        enum: ["celsius", "fahrenheit"],
        description: "Unidade de temperatura (padrão: celsius)",
        default: "celsius",
      },
    },
    required: ["location"],
  },
};

/**
 * Implementação da ferramenta
 * Retorna dados formatados para o agente Claude
 */
export async function executeGetWeather(
  provider: WeatherAPIProvider,
  params: GetWeatherParams
): Promise<WeatherData> {
  try {
    const data = await provider.getWeather(params.location);

    // Converte unidade se necessário
    if (params.units === "fahrenheit") {
      data.temperature = (data.temperature * 9) / 5 + 32;
    }

    return data;
  } catch (error) {
    throw new Error(`Falha ao obter previsão para ${params.location}: ${error instanceof Error ? error.message : String(error)}`);
  }
}
```

### 5.2 src/tools/forecast.ts

```typescript
import { WeatherAPIProvider } from "../provider/weather-api";
import { ForecastParams, ForecastData } from "../types";

export const ForecastSchema = {
  name: "get_forecast",
  description: "Obtém previsão meteorológica para os próximos dias",
  input_schema: {
    type: "object",
    properties: {
      location: {
        type: "string",
        description: "Nome da cidade ou localização",
      },
      days: {
        type: "number",
        description: "Número de dias para a previsão (1-14)",
        minimum: 1,
        maximum: 14,
      },
      units: {
        type: "string",
        enum: ["celsius", "fahrenheit"],
        description: "Unidade de temperatura",
        default: "celsius",
      },
    },
    required: ["location", "days"],
  },
};

export async function executeGetForecast(
  provider: WeatherAPIProvider,
  params: ForecastParams
): Promise<ForecastData> {
  if (params.days < 1 || params.days > 14) {
    throw new Error("Dias deve estar entre 1 e 14");
  }

  try {
    const data = await provider.getForecast(params.location, params.days);

    // Converte unidades se necessário
    if (params.units === "fahrenheit") {
      data.forecast = data.forecast.map((day) => ({
        ...day,
        highTemp: (day.highTemp * 9) / 5 + 32,
        lowTemp: (day.lowTemp * 9) / 5 + 32,
      }));
    }

    return data;
  } catch (error) {
    throw new Error(`Falha ao obter previsão para ${params.location}: ${error instanceof Error ? error.message : String(error)}`);
  }
}
```

---

## 6. Etapa 5: Hooks do Plugin

### 6.1 src/hooks/before-model-resolve.ts

```typescript
/**
 * Hook executado ANTES da resolução do modelo
 * Útil para inicializar credenciais, validar configuração, etc.
 */
export async function beforeModelResolve(context: any) {
  console.log("[Weather Plugin] Validando configuração antes de resolver modelo...");

  // Exemplo: Verificar se chave de API está disponível
  if (!process.env.WEATHER_API_KEY) {
    throw new Error("WEATHER_API_KEY não configurada. Configure antes de usar o plugin.");
  }

  console.log("[Weather Plugin] Configuração validada com sucesso");
}
```

### 6.2 src/hooks/after-tool-call.ts

```typescript
/**
 * Hook executado APÓS uma chamada de ferramenta
 * Útil para logging, métricas, transformação de resposta, etc.
 */
export async function afterToolCall(context: any) {
  const { toolName, params, result, duration } = context;

  console.log(`[Weather Plugin] Ferramenta ${toolName} executada em ${duration}ms`);
  console.log(`  Parâmetros: ${JSON.stringify(params)}`);
  console.log(`  Resultado resumido: ${JSON.stringify(result).substring(0, 100)}...`);

  // Exemplo: Enviar métrica para observabilidade
  // metrics.recordToolExecution(toolName, duration);
}
```

---

## 7. Etapa 6: Utilitários

### 7.1 src/utils/retry.ts

```typescript
/**
 * Executa uma função com retry e backoff exponencial
 * Útil para chamadas de API que podem ser temporariamente instáveis
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number,
  initialDelayMs: number
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt < maxRetries) {
        // Calcula delay com backoff exponencial + jitter
        const delay = initialDelayMs * Math.pow(2, attempt) + Math.random() * 1000;
        console.log(`[Retry] Tentativa ${attempt + 1} falhou. Aguardando ${delay.toFixed(0)}ms antes de tentar novamente...`);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError || new Error("Falha na operação após múltiplas tentativas");
}
```

### 7.2 src/utils/formatting.ts

```typescript
import { WeatherData } from "../types";

/**
 * Formata dados de previsão em texto legível para o usuário
 */
export function formatWeatherResponse(data: WeatherData): string {
  return `
📍 Local: ${data.location}
🌡️ Temperatura: ${data.temperature.toFixed(1)}°C
💧 Umidade: ${data.humidity}%
💨 Vento: ${data.windSpeed} km/h
⛅ Condição: ${data.condition}
⏰ Atualizado em: ${data.lastUpdated.toLocaleString("pt-BR")}
  `.trim();
}

/**
 * Formata previsão de múltiplos dias
 */
export function formatForecastResponse(days: any[]): string {
  const formatted = days
    .map(
      (day) =>
        `${day.date}: ${day.condition} - Máx: ${day.highTemp}°C, Mín: ${day.lowTemp}°C (Precipitação: ${day.precipitation}mm)`
    )
    .join("\n");

  return `📅 Previsão:\n${formatted}`;
}
```

---

## 8. Etapa 7: Ponto de Entrada do Plugin

### 8.1 src/index.ts (ARQUIVO CRÍTICO)

```typescript
import { WeatherAPIProvider } from "./provider/weather-api";
import { getConfigFromEnv } from "./provider/config";
import { GetWeatherSchema, executeGetWeather } from "./tools/get-weather";
import { ForecastSchema, executeGetForecast } from "./tools/forecast";
import { beforeModelResolve } from "./hooks/before-model-resolve";
import { afterToolCall } from "./hooks/after-tool-call";

let weatherProvider: WeatherAPIProvider;

/**
 * Função de registro do plugin
 * Chamada por OpenClaw no startup
 *
 * OpenClaw espera uma função default que recebe um objeto `api` com:
 * - registerTool(schema, handler)
 * - registerHook(event, handler)
 * - getConfig()
 * - log(message)
 */
export default function registerWeatherPlugin(api: any) {
  console.log("[Weather Plugin] Iniciando registro do plugin...");

  // Inicializa provider da API
  const config = getConfigFromEnv();
  weatherProvider = new WeatherAPIProvider(config);

  // =========== REGISTRO DE FERRAMENTAS ===========
  // Cada ferramenta é registrada com seu schema e handler

  api.registerTool(GetWeatherSchema, async (params: any) => {
    try {
      const result = await executeGetWeather(weatherProvider, params);
      return {
        ok: true,
        data: result,
      };
    } catch (error) {
      return {
        ok: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  });

  api.registerTool(ForecastSchema, async (params: any) => {
    try {
      const result = await executeGetForecast(weatherProvider, params);
      return {
        ok: true,
        data: result,
      };
    } catch (error) {
      return {
        ok: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  });

  // =========== REGISTRO DE HOOKS ===========
  // Hooks executam em pontos específicos do ciclo de vida do agente

  api.registerHook("before:model-resolve", beforeModelResolve);
  api.registerHook("after:tool-call", afterToolCall);

  // =========== LIMPEZA PERIÓDICA ===========
  // Limpa cache expirado a cada 5 minutos
  setInterval(() => {
    weatherProvider.clearExpiredCache();
  }, 5 * 60 * 1000);

  console.log("[Weather Plugin] Plugin registrado com sucesso!");
  return {
    id: "weather-plugin",
    version: "1.0.0",
    tools: [GetWeatherSchema.name, ForecastSchema.name],
  };
}
```

---

## 9. Instalação e Configuração

### 9.1 Compilar o Plugin

```bash
npm install
npm run build
```

### 9.2 Instalar em OpenClaw

```bash
# Opção 1: Instalar do npm
openclaw plugins install @myorg/openclaw-weather-plugin

# Opção 2: Instalar localmente para desenvolvimento
openclaw plugins install -l ./my-weather-plugin
```

### 9.3 Configurar openclaw.json

```json
{
  "plugins": {
    "entries": {
      "weather-plugin": {
        "enabled": true,
        "config": {
          "apiKey": "${WEATHER_API_KEY}",
          "apiUrl": "https://api.weather.example.com",
          "cacheSeconds": 300,
          "maxRetries": 3,
          "retryDelayMs": 1000
        }
      }
    }
  }
}
```

### 9.4 Variáveis de Ambiente

```bash
export WEATHER_API_KEY="sua-chave-de-api"
export WEATHER_API_URL="https://api.weather.example.com"
export WEATHER_CACHE_SECONDS="300"
export WEATHER_MAX_RETRIES="3"
export WEATHER_RETRY_DELAY="1000"
```

---

## 10. Teste do Plugin

### 10.1 Teste Unitário

```typescript
// tests/weather-api.test.ts
import { WeatherAPIProvider } from "../src/provider/weather-api";

describe("WeatherAPIProvider", () => {
  let provider: WeatherAPIProvider;

  beforeEach(() => {
    provider = new WeatherAPIProvider({
      apiKey: "test-key",
      apiUrl: "https://api.test.com",
      cacheSeconds: 300,
      maxRetries: 3,
      retryDelayMs: 100,
    });
  });

  it("deve retornar dados de previsão para uma localização válida", async () => {
    const result = await provider.getWeather("São Paulo");
    expect(result.location).toBe("São Paulo");
    expect(result.temperature).toBeDefined();
  });

  it("deve usar cache para requisições repetidas", async () => {
    await provider.getWeather("Rio de Janeiro");
    const start = Date.now();
    await provider.getWeather("Rio de Janeiro");
    const duration = Date.now() - start;
    expect(duration).toBeLessThan(50);
  });
});
```

### 10.2 Teste no OpenClaw

```bash
# Inicia o agente
openclaw agent --agentId personal

# Testa a ferramenta
Qual é a previsão do tempo em São Paulo?

# Resultado esperado:
# Claude usa a ferramenta get_weather e retorna dados atualizados
```

---

## 11. Ciclo de Vida do Plugin

```
┌─────────────────────────────────────────┐
│  OpenClaw Gateway Startup               │
└────────────────┬────────────────────────┘
                 │
                 ▼
     ┌───────────────────────┐
     │ Carrega plugins       │
     │ openclaw.json         │
     └───────────┬───────────┘
                 │
                 ▼
     ┌───────────────────────────────┐
     │ Chama registerWeatherPlugin() │
     │ (função default do módulo)    │
     └───────────┬───────────────────┘
                 │
                 ▼
     ┌──────────────────────────────────┐
     │ 1. Inicializa WeatherAPIProvider │
     │ 2. Registra ferramentas (tools)  │
     │ 3. Registra hooks               │
     │ 4. Retorna metadata             │
     └───────────┬──────────────────────┘
                 │
                 ▼
     ┌─────────────────────────────────┐
     │ Plugin Pronto para Uso          │
     │ Ferramentas injetadas no prompt │
     └─────────────────────────────────┘
```

---

## 12. Fluxo Completo de Execução

### Quando o usuário envia uma mensagem:

```
1. Usuário em Telegram:
   "Qual é o tempo em São Paulo?"

2. OpenClaw Gateway:
   - Roteia mensagem para agente baseado em binding
   - Resolve sessão
   - Injeta ferramentas no system prompt

3. Claude recebe:
   - System prompt com get_weather e get_forecast tools
   - Histórico de conversa
   - Mensagem do usuário

4. Claude analisa e decide:
   "Preciso usar a ferramenta get_weather para São Paulo"

5. OpenClaw executa:
   - Valida parâmetros contra schema
   - Chama hook before:tool-call
   - Executa executeGetWeather()
     → Verifica cache
     → Faz request para API com retry
     → Valida resposta com Zod
     → Armazena em cache
   - Chama hook after:tool-call
   - Retorna resultado formatado

6. Claude processa resultado:
   - Formata resposta legível
   - Retorna para usuário

7. Usuário recebe:
   "📍 Local: São Paulo
    🌡️ Temperatura: 25.5°C
    💧 Umidade: 65%
    ..."
```

---

## 13. Boas Práticas

### 13.1 Tratamento de Erros

```typescript
// ✅ BOM: Erros específicos e informativos
throw new Error(`Falha ao conectar com API de previsão (${location}): timeout após 10s`);

// ❌ EVITAR: Erros genéricos
throw new Error("Erro");
```

### 13.2 Performance

```typescript
// ✅ BOM: Cache e retry
- Implementar cache em memória para dados imutáveis
- Usar backoff exponencial em retries
- Limpar cache expirado periodicamente

// ❌ EVITAR: Chamadas bloqueantes sem timeout
await fetch(url);  // sem timeout!
```

### 13.3 Segurança

```typescript
// ✅ BOM: Validação com Zod
const ConfigSchema = z.object({
  apiKey: z.string().min(1),
  apiUrl: z.string().url(),
});

// ❌ EVITAR: Aceitar qualquer entrada
const config = JSON.parse(userInput);
```

### 13.4 Logging

```typescript
// ✅ BOM: Logs estruturados com contexto
console.log(`[Weather Plugin] Ferramenta ${toolName} executada em ${duration}ms`);

// ❌ EVITAR: Logs sem contexto
console.log("Done");
```

---

## 14. Checklist de Implementação

- [ ] Estrutura de pastas criada
- [ ] `package.json` e `tsconfig.json` configurados
- [ ] Tipos TypeScript definidos em `types.ts`
- [ ] Client da API externa implementado com retry e cache
- [ ] Ferramentas definidas com JSON Schema válido
- [ ] Handlers de ferramentas implementados
- [ ] Hooks registrados (before-model-resolve, after-tool-call)
- [ ] Função de registro (index.ts) exportada como default
- [ ] Validação de configuração com Zod
- [ ] Tratamento de erros completo
- [ ] Testes unitários criados
- [ ] Plugin compilado com `npm run build`
- [ ] Plugin instalado em OpenClaw
- [ ] `openclaw.json` configurado com dados do plugin
- [ ] Variáveis de ambiente definidas
- [ ] Testado no OpenClaw com mensagens reais

---

## 15. Recursos Adicionais

### Documentação Oficial
- [OpenClaw Architecture](file://<path>/openclaw-expert-workspace/skills/openclaw-expert/SKILL.md)
- [Pi Agent SDK](https://github.com/anthropic-ai/pi-agent)

### Exemplos de Plugins Reais
- Context Engine Plugins (lossless-claw)
- Memory Search Plugins (Gemini, OpenAI embeddings)
- Channel integrations (Discord, Slack, WhatsApp)

---

## 16. Troubleshooting

| Problema | Solução |
|----------|---------|
| Plugin não carrega | Verifique `openclaw.json`, execute `openclaw doctor` |
| Ferramenta não aparece | Verifique schema JSON, procure logs com `[Weather Plugin]` |
| API lenta | Aumente `cacheSeconds`, reduza `maxRetries`, implemente pagination |
| Erros de validação | Use Zod strict mode, adicione testes |
| Memória alta | Implemente limite de tamanho de cache, limpe entradas antigas |

---

**Parabéns! Você agora tem um plugin OpenClaw completo e pronto para produção.**

Para mais detalhes, consulte a documentação da skill OpenClaw Expert ou o source code em `~/.openclaw/plugins/`.
