# 🦅 exa-search — Busca neural (web, código e empresas)

**Objetivo:** Realizar buscas neurais de alta precisão filtradas por domínio (código, notícias, empresas) via MCP Exa (mcporter).  
**Quando usar:** Pesquisa de documentação técnica (GitHub/Stack Overflow), busca de tendências, prospecção de empresas ou verificação de fatos.  
**Referência:** `docs/30-exa-web-search.md`

---

## Diferencial Neural

Diferente da busca baseada em palavras-chave (Google/Brave), o **Exa** entende o significado semântico (embeddings) e retorna links de alta relevância técnica.

---

## Configuração (DevOps)

O Exa é geralmente acessado via **MCP (Model Context Protocol)** no OpenClaw.

```json
// ~/.openclaw/mcp_config.json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "@exa-labs/mcp-server"],
      "env": {
        "EXA_API_KEY": "sua_chave_aqui"
      }
    }
  }
}
```

> **Nota:** Alguns tiers permitem busca limitada sem API Key, mas recomenda-se configurar via Secret K8s.

---

## Ferramentas principais

### 1. `search` (Busca Neural Genérica)
Busca links similares ao significado do prompt.

```bash
# Exemplo de comando via ferramenta MCP
exa-search "Como implementar autenticação JWT rotativa em FastAPI"
```

### 2. `find_similar` (Busca por similaridade)
Encontra páginas similares a uma URL conhecida.

```bash
exa-find_similar "https://docs.pydantic.dev/latest/"
```

### 3. `get_contents` (Extração limpa)
Obtém o conteúdo da página já convertido em Markdown/Texto limpo prontos para LLM.

```bash
exa-get_contents ["https://github.com/fastapi/fastapi"]
```

---

## Filtros avançados

O Exa permite filtrar por categoria para evitar ruído:

| Categoria | Descrição |
|-----------|-----------|
| `company` | Busca focada em sites de empresas e LinkedIn |
| `research paper` | Busca em repositórios acadêmicos (ArXiv, etc.) |
| `github` | Busca focada em código e repositórios |
| `tweet` | Busca em threads e posts do X/Twitter |
| `blog` | Busca em artigos técnicos e blogs |

Exemplo de query filtrada:
`exa-search "JWT best practices" --category "github"`

---

## Uso por agente

| Agente | Aplicação |
|--------|-----------|
| **CEO** | Pesquisa de mercado, tendências de IA, busca de concorrentes |
| **Architect** | Busca de padrões de projeto, RFCs, bibliotecas similares |
| **Developer** | Pesquisa de erros de compilação, exemplos de uso de biblioteca (Stack Overflow/GitHub) |
| **CyberSec** | Busca de CVEs recentes, exploits conhecidos para uma biblioteca |
| **UX** | Pesquisa de design systems, cases de UX para nichos específicos |

---

## Boas práticas

- Use o **`get_contents`** em vez de baixar o HTML bruto; o Exa já limpa cabeçalhos/rodapés.
- Se o resultado for muito genérico, adicione o filtro `--category`.
- Combine com a skill de `summarize` se o conteúdo extraído for muito longo (> 4000 tokens).
- Respeite a **Egress Whitelist**: o MCP Gateway deve validar o domínio `api.exa.ai`.
