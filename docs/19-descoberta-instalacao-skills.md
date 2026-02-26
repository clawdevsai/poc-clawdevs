# Descoberta e instalação de skills

Os agentes do enxame podem **descobrir e propor a instalação de skills** do ecossistema aberto de agent skills quando isso ampliar capacidades de forma segura. Este documento define quando usar, como buscar, como apresentar opções ao Diretor e como alinhar instalação à **postura Zero Trust** e ao checklist de skills de terceiros em [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

**Segurança:** Buscar e listar skills é permitido no escopo do agente; **instalar** qualquer skill exige verificação de origem, revisão do SKILL.md e aprovação explícita do Diretor (e, quando aplicável, do CyberSec). Skills de terceiros são vetor de risco — ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md) (seção *Skills de terceiros*). **Verificação criptográfica na borda:** todo pacote de skill deve ter manifesto de hash **SHA-256** obrigatório (`skillstracelock.json`); o roteador OpenClaw (ou componente de borda) **derruba automaticamente** qualquer requisição de download cujo hash não bata 100%, de forma silenciosa, sem notificar o CyberSec — isso elimina dependência de LLM para barrar artefatos adulterados. **Zero binários:** todas as skills devem ser obrigatoriamente **script em texto claro** (ex.: Python, Bash); pacotes pré-compilados ou binários são proibidos; o Architect pode analisar estaticamente e rejeitar qualquer arquivo que chegue já compilado.

**Score de confiança e quarentena:** Se uma skill tem **manifesto validado na borda** (ex.: x255 ou equivalente) e o sistema comprova que **não contém binários ocultos**, ela pode ser executada em **sandbox de execução (quarentena)** em vez de bloquear a sprint aguardando OK manual do Diretor para cada instalação. Casos de dúvida ou baixa confiança continuam exigindo aprovação explícita; ver matriz de escalonamento probabilística em [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

---

## Quando usar esta habilidade

Usar quando o Diretor ou o time:

- Pergunta "como fazer X" e X pode ser coberto por uma skill existente.
- Pede "encontrar uma skill para X" ou "existe skill que faça X?".
- Quer estender capacidades do agente em um domínio específico (testes, deploy, documentação, design, etc.).
- Menciona necessidade de templates, fluxos de trabalho ou ferramentas que possam existir como skill instalável.

Não usar para substituir capacidades já documentadas nesta pasta (ex.: expertise em documentação, escrita humanizada, segurança OWASP, **frontend design** — ver [23-frontend-design.md](23-frontend-design.md), ou **memória de longo prazo** — modelo de seis camadas, WAL, higiene e **configuração prática de memória** — memorySearch, MEMORY.md, diários, recall — já consolidados em [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md)); usar para **complementar** com skills externas quando fizer sentido (ex.: plugins LanceDB, Mem0 ou Git-Notes que implementem camadas opcionais do doc 28). As habilidades de frontend design (design thinking, estética distinta, anti-genérico e **workflow e padrões SuperDesign** — layout, tema, animação, implementação com Tailwind/Flowbite/Lucide, responsivo, acessibilidade) estão **incorporadas** no doc 23; skills externas de "design" ou "UI" podem complementar, não substituir, essas diretrizes. Para o ecossistema **OpenClaw/ClawHub** (ex.: skill **FreeRide** — modelos gratuitos OpenRouter com ranking e fallbacks), a descoberta e instalação seguem o mesmo fluxo de aprovação; o uso e comandos estão em [22-modelos-gratuitos-openrouter-freeride.md](22-modelos-gratuitos-openrouter-freeride.md). Outro exemplo: skill **api-gateway** (Maton) — integração com 100+ APIs (Google, Slack, Notion, HubSpot, etc.) com OAuth gerenciado; instalação após checklist e uso conforme [25-api-gateway-integracao-apis.md](25-api-gateway-integracao-apis.md). O skill **ollama-local** (gestão e uso de modelos Ollama locais: list/pull/rm, chat, embeddings, tool-use, sub-agentes OpenClaw) está documentado em [31-ollama-local.md](31-ollama-local.md); instalação pelo mesmo fluxo de aprovação.

---

## O que é o Skills CLI

O **Skills CLI** (`npx skills`) funciona como gerenciador de pacotes do ecossistema aberto de agent skills. Skills são pacotes modulares que estendem capacidades do agente com conhecimento, fluxos e ferramentas especializados.

**Comandos principais:**

| Comando | Uso |
|--------|-----|
| `npx skills find [query]` | Buscar skills (interativo ou por palavra-chave). |
| `npx skills add <pacote>` | Instalar skill (GitHub ou outra origem). |
| `npx skills check` | Verificar atualizações disponíveis. |
| `npx skills update` | Atualizar skills instaladas. |

**Catálogo:** https://skills.sh/

---

## Fluxo: descobrir → apresentar → (opcional) instalar

### 1. Entender a necessidade

Identificar:

1. **Domínio** (ex.: React, testes, DevOps, documentação, design).
2. **Tarefa concreta** (ex.: escrever testes, criar changelog, revisar PRs).
3. Se a tarefa é comum o suficiente para provavelmente existir skill.

### 2. Buscar skills

Executar a busca com termos relevantes:

```bash
npx skills find [query]
```

Exemplos:

- "Como deixar o app React mais rápido?" → `npx skills find react performance`
- "Ajuda com revisão de PRs?" → `npx skills find pr review`
- "Preciso criar changelog" → `npx skills find changelog`

A saída pode trazer algo como:

```
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 3. Apresentar opções ao Diretor

Ao encontrar skills relevantes:

1. Nome da skill e o que ela faz.
2. Comando de instalação sugerido.
3. Link para mais informações (skills.sh).

Exemplo de resposta ao Diretor:

```
Encontrei uma skill que pode ajudar: "vercel-react-best-practices" traz
diretrizes de otimização de React e Next.js da Vercel Engineering.

Para instalar:
npx skills add vercel-labs/agent-skills@vercel-react-best-practices

Mais informações: https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

**Não instalar** sem aprovação. A instalação segue o checklist de [05-seguranca-e-etica.md](05-seguranca-e-etica.md) (origem, revisão do SKILL.md, aprovação em dúvida).

**Manter atualizadas:** Depois de instaladas, as skills podem ser atualizadas automaticamente pela rotina de **auto-atualização do ambiente** ([21-auto-atualizacao-ambiente.md](21-auto-atualizacao-ambiente.md)): cron em sessão isolada, sem necessidade de nova aprovação por skill já aprovada.

### 4. Manifesto de hash e domínios (skillstracelock.json) — obrigatório na borda

Antes de qualquer instalação, o pipeline de borda (ex.: roteador OpenClaw ou CI cedido ao DevOps) deve validar o **manifesto de hash SHA-256** (`skillstracelock.json`). Se o hash do pacote não coincidir 100% com o manifesto, a requisição de download é **rejeitada automaticamente**, sem notificar o CyberSec. Nenhuma decisão de LLM substitui essa verificação criptográfica determinística na borda.

**Domínios e egress:** A rede **não** é liberada apenas pela autodeclaração da skill no manifesto. A infraestrutura mantém **whitelist global estática** no Gateway (ex.: NPM, GitHub, API OpenAI). Domínios **fora** dessa lista são **bloqueados por padrão** (alerta crítico no Telegram); para domínios na whitelist ou em processo de ampliação, exige-se **validação determinística de reputação** (ex.: API VirusTotal) antes de liberar tráfego. Cada skill pode declarar `allowed_domains` no manifesto para documentação, mas a liberação efetiva depende da whitelist global e da verificação de reputação — skills não podem abrir o firewall por si só. Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [issues/024-skills-terceiros-checklist-egress.md](issues/024-skills-terceiros-checklist-egress.md).

### 5. Regra zero binários

Todas as skills instaláveis devem ser **código em texto claro** (ex.: Python, Bash, JavaScript legível). **Pacotes pré-compilados ou binários são proibidos.** O Architect (e o pipeline de revisão estática) deve rejeitar qualquer skill que contenha artefatos compilados ou ofuscados. Essa regra reduz a superfície de ataque e permite análise estática sem depender do CyberSec para detectar lógica maliciosa em binários.

### 6. Instalação (após aprovação)

Só após o Diretor aprovar e após verificação de segurança:

1. **Verificar origem** (autor/registry confiável).
2. **Revisar o SKILL.md** da skill em busca de comandos suspeitos (shell, curl/wget, exfiltração).
3. Confirmar que a skill é apenas texto claro (sem binários); verificar hash em `skillstracelock.json`.
4. Se estiver em dúvida, pedir aprovação explícita ao Diretor.

Comando de instalação (quando aprovado):

```bash
npx skills add <owner/repo@skill> -g -y
```

`-g` instala no nível do usuário; `-y` evita prompts de confirmação em modo não interativo.

---

## Categorias comuns de skills

| Categoria | Exemplos de busca |
|-----------|-------------------|
| Desenvolvimento web | react, nextjs, typescript, css, tailwind |
| Testes | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| Documentação | docs, readme, changelog, api-docs |
| Qualidade de código | review, lint, refactor, best-practices |
| Design | ui, ux, design-system, acessibilidade |
| Produtividade | workflow, automação, git |
| Busca web / pesquisa | brave-search, web search, search api, content extraction, Exa (MCP mcporter: web + código + empresas) |
| Dados, watchlist, alertas, simulação | prediction markets, watchlist, alerts, paper trading, digest, momentum |

Para habilidades de **dados, watchlist, alertas e simulação** (consulta a APIs de dados, acompanhamento, alertas por threshold/cron, calendário/prazos, momentum/digests, simulação local), ver [26-dados-watchlist-alertas-simulacao.md](26-dados-watchlist-alertas-simulacao.md).

---

## Quando não houver skills encontradas

1. Informar que não foi encontrada skill relevante para o termo buscado.
2. Oferecer ajudar na tarefa com as capacidades atuais do agente.
3. Sugerir, se for algo recorrente, criar uma skill própria: registrar a ideia em `.learnings/FEATURE_REQUESTS.md` conforme [10-self-improvement-agentes.md](10-self-improvement-agentes.md) e seguir o processo de **criação de skills** em [29-criacao-de-skills.md](29-criacao-de-skills.md) (princípios, anatomia, 6 passos; usar `npx skills init <nome-skill>` quando disponível no ecossistema).

---

## Dicas para buscas eficazes

- Usar **termos específicos**: "react testing" tende a dar melhores resultados que só "testing".
- Tentar **sinônimos**: se "deploy" não retornar nada, tentar "deployment" ou "ci-cd".
- Considerar **fontes conhecidas**: muitas skills vêm de `vercel-labs/agent-skills` ou repositórios curados.

---

## Quem pode usar

| Agente | Buscar skills | Propor instalação | Instalar (após aprovação) |
|--------|----------------|-------------------|---------------------------|
| **CEO** | Sim (pesquisa, tendências) | Sim | Não — escalar ao Diretor/DevOps. |
| **PO** | Sim (se tiver acesso à rede permitida) | Sim | Não. |
| **Architect** | Sim | Sim | Não — aprovar uso técnico; instalação pelo DevOps ou Diretor. |
| **Developer** | Sim | Sim | Não — depende de Architect/CyberSec e Diretor ([02-agentes.md](02-agentes.md): não instalar bibliotecas/pacotes sem autorização). |
| **DevOps/SRE** | Sim | Sim | Sim, **somente** após checklist de segurança e aprovação do Diretor. |
| **QA** | Sim | Sim | Não. |
| **CyberSec** | Sim (avaliar riscos) | Sim (com parecer de segurança) | Não — validar e bloquear se houver risco; instalação operada por DevOps/Diretor. |
| **UX** | Sim | Sim | Não. |

A **instalação efetiva** (executar `npx skills add`) deve ser feita por quem tem permissão operacional (ex.: DevOps) e apenas após o fluxo Zero Trust e o checklist de skills de terceiros.

---

## Relação com a documentação

- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Postura Zero Trust, checklist de skills de terceiros, regras de instalação, varredura na borda.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validação pré-execução de comandos (incluindo `npx`).
- [02-agentes.md](02-agentes.md) — Regras por agente (ex.: Developer não instala sem autorização).
- [10-self-improvement-agentes.md](10-self-improvement-agentes.md) — FEATURE_REQUESTS quando não houver skill e for relevante criar uma.
- [29-criacao-de-skills.md](29-criacao-de-skills.md) — Criação de skills: quando não houver skill no ecossistema e a necessidade for recorrente, os agentes seguem o processo (princípios, anatomia, 6 passos) para criar uma skill própria.
- [13-habilidades-proativas.md](13-habilidades-proativas.md) — Resourcefulness: usar descoberta de skills como mais uma ferramenta antes de desistir.
- [20-ferramenta-github-gh.md](20-ferramenta-github-gh.md) — Ferramenta GitHub (gh CLI) integrada ao time: Issues, PRs, CI, API; skills do ecossistema (ex.: "github") podem estar documentadas como capacidade padrão neste doc.
- [21-auto-atualizacao-ambiente.md](21-auto-atualizacao-ambiente.md) — Auto-atualização do ambiente: atualizar o runtime e **todas as skills já instaladas** em rotina automática (cron, resumo ao Diretor); instalação de **novas** skills continua por este fluxo (descoberta → propor → aprovar).
- [22-modelos-gratuitos-openrouter-freeride.md](22-modelos-gratuitos-openrouter-freeride.md) — Modelos gratuitos OpenRouter (FreeRide): skill do ecossistema OpenClaw/ClawHub; quando o Diretor quiser IA gratuita ou redução de custos com OpenRouter, propor/instalar conforme este fluxo e usar os comandos e regras do doc 22.
- [26-dados-watchlist-alertas-simulacao.md](26-dados-watchlist-alertas-simulacao.md) — Dados, watchlist, alertas e simulação: categorias de habilidades (consulta a APIs, watchlist, alertas, calendário, momentum/digests, paper trading local); skills que se encaixem nessas categorias são buscadas e propostas por este fluxo.
- [24-busca-web-headless.md](24-busca-web-headless.md) — Busca web headless (genérica); implementações via skill ou MCP.
- [30-exa-web-search.md](30-exa-web-search.md) — Exa Web Search: implementação via MCP (mcporter) para busca web, código (GitHub/Stack Overflow) e pesquisa de empresas; habilitar conforme este fluxo (propor → aprovar).
