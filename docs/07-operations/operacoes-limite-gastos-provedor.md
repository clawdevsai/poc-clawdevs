# Limite de gastos no painel do provedor (truncamento-finops)

Para evitar surpresas na fatura, configure um **limite rígido de gastos** (freio de emergência) no painel do provedor de LLM em nuvem que você usar. O pipeline de truncamento e sumarização (doc 07) reduz o consumo na causa raiz; o limite no painel é a proteção final.

---

## OpenRouter

1. Acesse [openrouter.ai](https://openrouter.ai) e faça login.
2. Vá em **Settings** → **Usage & Billing** (ou **Keys**).
3. Defina **Spend limit** (ex.: $5/dia ou $50/mês) conforme seu freio de emergência.
4. Opcional: crie uma API key com limite próprio para o ClawDevs.

---

## OpenAI

1. Acesse [platform.openai.com](https://platform.openai.com) → **Settings** → **Billing**.
2. Em **Limits**, configure **Hard limit** (ex.: $5/dia) ou **Monthly budget**.
3. Ative alertas por e-mail ao atingir um percentual do limite.

---

## Google Cloud (Vertex AI / Gemini)

1. Acesse [console.cloud.google.com](https://console.cloud.google.com) → **Billing** → **Budgets & alerts**.
2. Crie um **Budget** para o projeto que usa a API (ex.: limite mensal em USD).
3. Configure alertas (ex.: 50%, 90%, 100%) e opcionalmente **cap** para bloquear uso acima do orçamento.

---

## Ollama Cloud

1. No painel da conta Ollama Cloud, verifique a seção de **Usage** ou **Billing**.
2. Configure limite de créditos ou gasto conforme a documentação atual do provedor.

---

**Referência:** [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (Limite de gastos), [issues/041-truncamento-contexto-finops.md](issues/041-truncamento-contexto-finops.md).
