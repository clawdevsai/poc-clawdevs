# Ferramenta Markdown Converter (markitdown)

CLI para **converter documentos e arquivos para Markdown** usando `uvx markitdown`. Útil para agentes que precisam **extrair texto estruturado** de PDFs, Word, PowerPoint, Excel, HTML, imagens (EXIF/OCR), áudio (transcrição), ZIP, URLs do YouTube e EPubs, para processamento por LLM, análise de texto ou alimentação de RAG. Diferente da ferramenta **summarize** ([12-ferramenta-summarize.md](12-ferramenta-summarize.md)), que **resume** conteúdo com modelo de IA, o markitdown **converte** o formato preservando estrutura (títulos, tabelas, listas, links) sem sumarização.

**Uso:** Quando o agente precisar **ler ou processar** um documento não-Markdown (especificação em PDF, planilha, slide, anexo de e-mail convertido etc.), invocar `uvx markitdown` para obter Markdown e então seguir com análise, citação ou ingestão em RAG.

---

## Instalação

Não é necessária instalação local: o comando usa **uvx** (UV), que baixa e executa o pacote na primeira execução.

```bash
# Verificar se uv está disponível (Python/UV)
uvx markitdown --help
```

Na primeira execução as dependências são cacheadas; as seguintes são mais rápidas.

---

## Uso básico

```bash
# Saída no stdout
uvx markitdown input.pdf

# Salvar em arquivo
uvx markitdown input.pdf -o output.md
uvx markitdown input.docx > output.md

# Entrada via stdin (com hint de extensão)
cat input.pdf | uvx markitdown -x .pdf > output.md
```

---

## Formatos suportados

| Categoria   | Formatos |
|------------|----------|
| Documentos | PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx, .xls) |
| Web/Dados  | HTML, CSV, JSON, XML |
| Mídia      | Imagens (EXIF + OCR), Áudio (EXIF + transcrição) |
| Outros     | ZIP (itera conteúdo), URLs do YouTube, EPub |

---

## Opções principais

| Opção | Descrição |
|-------|-----------|
| `-o OUTPUT` | Arquivo de saída |
| `-x EXTENSION` | Hint de extensão (para stdin) |
| `-m MIME_TYPE` | Hint de MIME type |
| `-c CHARSET` | Hint de charset (ex.: UTF-8) |
| `-d` | Usar Azure Document Intelligence |
| `-e ENDPOINT` | Endpoint do Document Intelligence |
| `--use-plugins` | Habilitar plugins de terceiros |
| `--list-plugins` | Listar plugins instalados |

---

## Exemplos

```bash
# Word
uvx markitdown report.docx -o report.md

# Excel
uvx markitdown data.xlsx > data.md

# PowerPoint
uvx markitdown slides.pptx -o slides.md

# Hint de tipo para stdin
cat document | uvx markitdown -x .pdf > output.md

# PDF complexo com Azure Document Intelligence (melhor extração)
uvx markitdown scan.pdf -d -e "https://your-resource.cognitiveservices.azure.com/"
```

---

## Notas

- A saída preserva estrutura: headings, tabelas, listas, links.
- Para PDFs com extração ruim, usar `-d` com Azure Document Intelligence (requer recurso e endpoint configurados).
- **Segurança:** Validar paths e origem dos arquivos antes de invocar (Zero Trust; ver [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md)). Não processar arquivos de origem não confiável sem aprovação.

---

## Uso no ecossistema de agentes

- **CEO / PO:** Converter especificações, RFPs ou anexos (PDF, Word, planilhas) para Markdown antes de extrair requisitos, priorizar backlog ou alimentar RAG.
- **Pipeline de pré-processamento:** Antes de enviar contexto à nuvem ou ao summarize, converter documentos pesados para Markdown pode reduzir ruído e permitir sumarização ou truncamento mais eficiente (ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md)).
- **Developer / Architect:** Converter docs de design, ADRs em PDF ou exportações de ferramentas (Notion, Confluence em HTML) para análise e citação no código ou em PRs.
- **Architect — microADR:** Sempre que um **pull request for aprovado**, o Architect usa markitdown (ou saída formatada) para gerar um **microADR** (registro de decisão arquitetural) em **JSON estrito**. A saída é anexada **diretamente** à memória vetorial de longo prazo (Warm Store), **fora** do pipeline de sumarização — o microADR nunca é resumido. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (seção 2.3) e [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md).
- **Expertise em documentação:** Ao obter um doc em formato binário ou HTML, o agente pode usar markitdown para obter Markdown e então aplicar o fluxo identificar → buscar → ler → citar (ver [18-expertise-documentacao.md](18-expertise-documentacao.md)).
