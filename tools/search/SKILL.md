# 🔍 search — Busca web headless e extração

**Objetivo:** Pesquisar na web e extrair conteúdo em Markdown de forma rápida, sem abrir browser completo (headless).  
**Quando usar:** Consultas rápidas a documentação, busca de notícias, verificação de dados públicos sem necessidade de interação complexa.  
**Referência:** `docs/24-busca-web-headless.md`

---

## ⚠️ Segurança Zero Trust (SSRF Protection)

- **Validação de URL:** O script de busca deve validar a URL de destino contra regras anti-SSRF (impedir acesso a `localhost`, `169.254.*`, IPs internos da rede K8s).
- **Egress Whitelist:** Somente domínios permitidos no `agents-config.yaml` podem ter o conteúdo extraído.
- **Max Content Size:** Limite de 2MB por página para evitar ataques de DoS e OOM.

---

## Ferramentas recomendadas

### 1. Brave Search (via MCP ou API)
Ideal para busca genérica e atualizada.

```bash
# Exemplo via CLI/Script
search-web "Versão estável do Kubernetes em Fevereiro 2026"
```

### 2. Jina Reader / Firecrawl
Ótimos para baixar uma página inteira já convertida para Markdown.

```bash
# Via cURL ou ferramenta customizada
curl https://r.jina.ai/https://docs.docker.com/compose/
# Retorna a página limpa em Markdown
```

---

## Passos para uso

### 1. Pesquisa inicial
Use o buscador para encontrar as URLs mais relevantes.

```bash
# Agente executa pesquisa
urls = search_tool.find("best practices for redis deployment on k8s")
```

### 2. Extração de conteúdo
Selecione as top 2-3 URLs e extraia o texto.

```bash
# Agente extrai conteúdo
content = search_tool.extract("https://redis.io/docs/deployment/")
```

### 3. Processamento
Passe o resultado pela skill de `summarize` se o texto for muito longo.

---

## Uso por agente

| Agente | Uso sugertido |
|--------|--------------|
| **DevOps** | Pesquisar bugs de infra, novas versões de charts Helm, documentação de cloud |
| **CyberSec** | Pesquisar vulnerabilidades em dependências npm/pip |
| **Architect** | Comparar frameworks e bibliotecas |
| **PO** | Buscar referências de funcionalidades em produtos concorrentes |
| **CEO** | Resumo de notícias do setor e novidades técnicas |

---

## Boas práticas

- **Preferir Headless ao Browser:** É mais barato (menos tokens/recursos) e mais rápido. Use o `agent-browser` apenas se precisar clicar em botões, fazer login ou interagir com JS pesado.
- **Cache Local:** Resultados de busca para a mesma query em < 12h devem ser buscados no `memory/warm/`.
- **Cabeçalho User-Agent:** Sempre usar identificação clara: `ClawDevs-Agent/1.0 (Autonomous-AI-Agent)`.
- **Respeito ao robots.txt:** A ferramenta deve honrar as diretivas de rastreamento.
