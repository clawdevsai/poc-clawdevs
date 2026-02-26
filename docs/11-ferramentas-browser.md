# Ferramentas de automação de browser (agent-browser)

CLI de automação de browser (Rust, com fallback Node.js) que permite aos agentes navegar, clicar, preencher formulários e obter snapshots de páginas via comandos estruturados. Relevante para **QA** (testes E2E), **Developer** (validação de frontend) e **UX** (análise de interface e fluxos).

Referência upstream: [agent-browser](https://github.com/vercel-labs/agent-browser) (Vercel Labs). Skill/Claw Hub: `agent-browser` (emoji 🌐; requer `node`, `npm`). Uso permitido: `Bash(agent-browser:*)`.

---

## Instalação

### npm (recomendado)

```bash
npm install -g agent-browser
agent-browser install
agent-browser install --with-deps
```

### A partir do código-fonte

```bash
git clone https://github.com/vercel-labs/agent-browser
cd agent-browser
pnpm install
pnpm build
agent-browser install
```

---

## Fluxo básico

1. **Navegar:** `agent-browser open <url>`
2. **Snapshot:** `agent-browser snapshot -i` (retorna elementos interativos com refs `@e1`, `@e2`, …)
3. **Interagir** usando as refs do snapshot
4. **Novo snapshot** após navegação ou mudanças relevantes no DOM

### Quick start

```bash
agent-browser open <url>        # Abre a página
agent-browser snapshot -i       # Lista elementos interativos com refs
agent-browser click @e1         # Clica no elemento por ref
agent-browser fill @e2 "texto"  # Preenche input por ref
agent-browser close             # Fecha o browser
```

---

## Comandos por categoria

### Navegação

| Comando | Descrição |
|---------|-----------|
| `agent-browser open <url>` | Navega para a URL |
| `agent-browser back` | Volta |
| `agent-browser forward` | Avança |
| `agent-browser reload` | Recarrega |
| `agent-browser close` | Fecha o browser |

### Snapshot (análise da página)

| Comando | Descrição |
|---------|-----------|
| `agent-browser snapshot` | Árvore de acessibilidade completa |
| `agent-browser snapshot -i` | Apenas elementos interativos (recomendado) |
| `agent-browser snapshot -c` | Saída compacta |
| `agent-browser snapshot -d 3` | Limita profundidade a 3 |
| `agent-browser snapshot -s "#main"` | Escopo por seletor CSS |

### Interações (usar @refs do snapshot)

| Comando | Descrição |
|---------|-----------|
| `agent-browser click @e1` | Clique |
| `agent-browser dblclick @e1` | Duplo clique |
| `agent-browser focus @e1` | Foco |
| `agent-browser fill @e2 "texto"` | Limpa e digita |
| `agent-browser type @e2 "texto"` | Digita sem limpar |
| `agent-browser press Enter` | Tecla |
| `agent-browser hover @e1` | Hover |
| `agent-browser check @e1` / `uncheck @e1` | Checkbox |
| `agent-browser select @e1 "value"` | Select |
| `agent-browser scroll down 500` | Scroll |
| `agent-browser scrollintoview @e1` | Scroll até elemento |
| `agent-browser drag @e1 @e2` | Arrastar e soltar |
| `agent-browser upload @e1 file.pdf` | Upload de arquivo |

### Obter informação

| Comando | Descrição |
|---------|-----------|
| `agent-browser get text @e1` | Texto do elemento |
| `agent-browser get html @e1` | innerHTML |
| `agent-browser get value @e1` | Valor de input |
| `agent-browser get attr @e1 href` | Atributo |
| `agent-browser get title` | Título da página |
| `agent-browser get url` | URL atual |
| `agent-browser get count ".item"` | Contagem de elementos |

### Estado e espera

| Comando | Descrição |
|---------|-----------|
| `agent-browser is visible @e1` | Está visível? |
| `agent-browser is enabled @e1` | Está habilitado? |
| `agent-browser wait @e1` | Espera elemento |
| `agent-browser wait 2000` | Espera em ms |
| `agent-browser wait --text "Success"` | Espera texto |
| `agent-browser wait --url "/dashboard"` | Espera padrão de URL |
| `agent-browser wait --load networkidle` | Espera rede ociosa |

### Screenshot, PDF e vídeo

| Comando | Descrição |
|---------|-----------|
| `agent-browser screenshot` | Screenshot para stdout |
| `agent-browser screenshot path.png` | Salva em arquivo |
| `agent-browser screenshot --full` | Página inteira |
| `agent-browser pdf output.pdf` | Salva como PDF |
| `agent-browser record start ./demo.webm` | Inicia gravação |
| `agent-browser record stop` | Para e salva |

### Localizadores semânticos (alternativa a @refs)

```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find first ".item" click
```

### Configuração do browser

```bash
agent-browser set viewport 1920 1080
agent-browser set device "iPhone 14"
agent-browser set offline on
agent-browser set credentials user pass
```

### Estado de sessão (reuso de login)

```bash
agent-browser state save auth.json    # Salva estado (cookies, storage)
agent-browser state load auth.json    # Carrega estado
```

### Sessões paralelas

```bash
agent-browser --session test1 open site-a.com
agent-browser --session test2 open site-b.com
agent-browser session list
```

### Saída JSON (parsing por agentes)

```bash
agent-browser snapshot -i --json
agent-browser get text @e1 --json
```

### Debug

```bash
agent-browser open example.com --headed   # Mostra janela do browser
agent-browser console                     # Mensagens do console
agent-browser errors                      # Erros da página
agent-browser highlight @e1               # Destaca elemento
agent-browser trace start
agent-browser trace stop trace.zip
```

### Opções gerais

| Opção | Descrição |
|-------|-----------|
| `--session <name>` | Sessão isolada |
| `--json` | Saída JSON |
| `--full` | Screenshot página inteira |
| `--headed` | Mostra janela do browser |
| `--timeout <ms>` | Timeout do comando |
| `--cdp <port>` | Conectar via Chrome DevTools Protocol |

---

## Exemplo: submissão de formulário

```bash
agent-browser open https://example.com/form
agent-browser snapshot -i
# Saída: textbox "Email" [ref=e1], textbox "Password" [ref=e2], button "Submit" [ref=e3]

agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "password123"
agent-browser click @e3
agent-browser wait --load networkidle
agent-browser snapshot -i   # Verificar resultado
```

---

## Exemplo: autenticação com estado salvo

```bash
# Login uma vez
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "username"
agent-browser fill @e2 "password"
agent-browser click @e3
agent-browser wait --url "/dashboard"
agent-browser state save auth.json

# Sessões seguintes: carregar estado
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

---

## Boas práticas para agentes

- **Refs** são estáveis por carregamento de página, mas mudam após navegação — fazer snapshot após cada navegação.
- Usar **fill** em vez de **type** em inputs para garantir que o texto existente seja limpo.
- Em falhas de elemento não encontrado: usar snapshot para obter a ref correta.
- Se a página não carregou: adicionar comando de wait após navegação.
- Em Linux ARM64, se o comando não for encontrado, usar o caminho completo do binário.

---

## Integração com o enxame

| Agente | Uso sugerido |
|--------|----------------|
| **QA** | Testes E2E, fluxos de UI, verificação de acessibilidade (snapshot). |
| **Developer** | Validação de frontend, preenchimento de formulários em demos, extração de dados. |
| **UX** | Análise de fluxos, gravação de vídeos de demo, captura de screenshots para documentação. |

Registrar gotchas e erros recorrentes em **TOOLS.md** do workspace (ver [10-self-improvement-agentes.md](10-self-improvement-agentes.md)) e, se aplicável, em `.learnings/ERRORS.md`.

---

## Reporte de problemas

- **Skill / documentação:** [TheSethRose/Agent-Browser-CLI](https://github.com/TheSethRose/Agent-Browser-CLI)
- **CLI agent-browser:** [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)

Antes de abrir issue: instalar `agent-browser@latest`, reproduzir o comando no terminal e anotar versão do Node, SO e saída de erro.
