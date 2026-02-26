# Ferramenta summarize (CLI)

CLI para sumarizar URLs, arquivos locais (PDF, imagens, áudio) e links do YouTube. Útil para agentes que precisam **reduzir contexto** antes de enviar à nuvem (ver pipeline de truncamento em [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md)), para CEO/PO consumirem resumos de páginas ou documentos, e para alimentar RAG com conteúdo pré-processado.

**Pre-flight obrigatório no OpenClaw:** O Summarize (ou equivalente) é configurado como **pre-flight obrigatório** no fluxo de eventos do OpenClaw: para issues ou conversas com **mais de três interações** destinadas à nuvem, o orquestrador intercepta o payload, um **modelo local** (ex.: Ollama) gera resumo executivo denso, o histórico bruto é substituído no payload e **só então** o Gateway envia ao provedor. Assim evita-se corte no meio de JSON e a carga pesada sai da nuvem paga para o hardware local. Detalhes em [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (seções 2.1 e 2.2).

**Regra de ouro — exceções à sumarização:** Conteúdo **tagado como invariante de negócio**, **microADR** (registro de decisão arquitetural) ou **critérios de aceite** (tag de proteção, ex.: `<!-- CRITERIOS_ACEITE -->`) **não** deve ser passado ao summarize. O microADR **nunca é resumido**; ele é anexado diretamente à memória vetorial de longo prazo. Os **critérios de aceite** das issues devem ser preservados intactos para que o PO faça a validação reversa (comparar resumo com critérios originais); se estiverem no mesmo buffer que é sumarizado, o PO perde a referência e não consegue rejeitar truncamento falho. O script de limpeza/compacted do DevOps usa **regex** para ignorar blocos dentro da tag de critérios de aceite; alternativa é armazenar critérios em arquivo separado e enviar payload duplo (resumo + critérios) à nuvem. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (seções 2.2 e 2.3) e [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md).

Referência: [summarize.sh](https://summarize.sh). Skill/Claw Hub: `summarize` (emoji 🧾; requer binário `summarize`).

---

## Instalação

### Homebrew (macOS/Linux)

```bash
brew install steipete/tap/summarize
```

---

## Quick start

```bash
# Exemplo com modelo local (Ollama) ou provedor OpenClaw (ex.: OpenRouter)
summarize "https://example.com" --model ollama/llama3:8b
summarize "/path/to/file.pdf" --model openrouter/openai/gpt-4o-mini
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

---

## Modelo e chaves de API

No **ClawDevs** usamos apenas **provedores integrados OpenClaw** para inferência. Definir a variável de ambiente do provedor escolhido (conforme [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md#provedores-apenas-integrados-openclaw)):

- **Ollama (local):** sem chave; `host` no config.
- **OpenRouter:** `OPENROUTER_API_KEY`
- **OpenAI:** `OPENAI_API_KEY`
- **Ollama cloud / Qwen / Moonshot AI / Hugging Face:** consultar [documentação OpenClaw](https://docs.openclaw.ai) para o nome exato da variável por provedor.

Para uso do CLI summarize fora do gateway (ex.: pre-flight local), usar modelo compatível (ex.: `ollama/llama3:8b` para local ou o modelo do provedor nuvem configurado).

---

## Flags úteis

| Flag | Descrição |
|------|-----------|
| `--length short\|medium\|long\|xl\|xxl\|<chars>` | Tamanho do resumo |
| `--max-output-tokens <count>` | Limite de tokens na saída |
| `--extract-only` | Apenas extração (apenas URLs) |
| `--json` | Saída em JSON (machine readable) |
| `--firecrawl auto\|off\|always` | Fallback de extração (requer `FIRECRAWL_API_KEY`) |
| `--youtube auto` | Fallback Apify para YouTube (requer `APIFY_API_TOKEN`) |

---

## Configuração opcional

Arquivo: `~/.summarize/config.json`

```json
{ "model": "openai/gpt-5.2" }
```

Serviços opcionais:

- **FIRECRAWL_API_KEY** — sites bloqueados ou com JS pesado
- **APIFY_API_TOKEN** — fallback para YouTube

---

## Uso no ecossistema de agentes

- **Pre-flight obrigatório (conversas com >3 interações):** O orquestrador invoca Summarize (modelo local) antes de enviar o payload à nuvem; substitui histórico bruto por resumo denso — ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md). Não depender de agente para "limpar" contexto; a gestão é determinística no pipeline.
- **Pipeline de truncamento:** Skill de pré-processamento ou estágio de borda invoca `summarize` em URLs ou arquivos antes de anexar ao contexto enviado ao CEO/nuvem, reduzindo tokens e custo.
- **CEO / PO:** Resumir artigos, documentação externa ou PDFs de requisitos para decisão sem carregar o conteúdo bruto.
- **Integração com .learnings:** Resumos de páginas de erro ou de documentação podem ser registrados em `.learnings/` (ver [10-self-improvement-agentes.md](10-self-improvement-agentes.md)) para consulta posterior.
