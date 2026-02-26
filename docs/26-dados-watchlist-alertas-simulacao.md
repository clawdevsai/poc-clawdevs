# Dados, watchlist, alertas e simulação

Os agentes podem dispor de **habilidades de consulta a dados externos, acompanhamento (watchlist), alertas e simulação local** — por exemplo via skills do ecossistema que sigam esse padrão. Este documento descreve as categorias de capacidade desejáveis para o time autônomo, de forma independente de qualquer skill específica.

**Contexto:** Padrões inspirados em skills de mercados de previsão e dados públicos (APIs read-only, sem autenticação quando o provedor for público), adaptados ao uso por agentes com **postura Zero Trust** ([05-seguranca-e-etica.md](05-seguranca-e-etica.md)) e **validação em runtime** ([14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md)).

---

## Visão geral das categorias

| Categoria | Objetivo | Exemplo de uso |
|-----------|----------|----------------|
| **Consulta a APIs de dados** | Ler dados de APIs públicas (odds, preços, eventos, volumes). | Trending, featured, busca, evento por slug, listagem por categoria. |
| **Watchlist** | Manter lista de itens acompanhados (ex.: mercados, ativos, eventos). | Adicionar/remover, listar com estado atual (preço, prazo). |
| **Alertas** | Notificar quando um threshold é atingido (preço, variação %, prazo). | Alert-at X%, alert-change ±Y%, checagem por cron (`--quiet`). |
| **Calendário / prazos** | Eventos que “resolvem” ou vencem em N dias. | “O que resolve nos próximos 7 dias”, filtro por dias e limite. |
| **Momentum / digests** | Maiores movimentos em um período; resumos por categoria. | Movers 24h/1w/1m; digest por categoria (política, crypto, etc.). |
| **Simulação local (paper)** | Simular posições e P&L sem dinheiro real; estado em arquivos locais. | “Comprar”/“vender” simulado, portfolio em `~/.xxx/` (JSON). |

Todas essas capacidades podem ser oferecidas por **skills** instaladas após descoberta e aprovação conforme [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md). Nenhuma delas substitui as diretrizes já documentadas nesta pasta (ex.: segurança, escrita humanizada, documentação).

---

## 1. Consulta a APIs de dados

- **Leitura apenas:** GET em APIs públicas; sem autenticação quando o provedor permitir.
- **Comandos típicos:** trending, featured, search, event (por slug), category.
- **Segurança:** Validar URL e método (apenas GET para leitura); não expor credenciais; seguir [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) (SSRF, URLs).
- **Quem usa:** CEO (pesquisa, tendências), PO (contexto de mercado quando autorizado), outros agentes quando a tarefa exigir dados externos e a skill estiver aprovada.

---

## 2. Watchlist

- **Persistência:** Lista de itens (IDs/slugs) com metadados opcionais (threshold de alerta, outcome específico).
- **Operações:** add, remove, list (com estado atual: preço, volume, tempo restante).
- **Armazenamento:** Arquivo local em diretório dedicado (ex.: `~/.skill-name/watchlist.json`), somente leitura/escrita pelo processo da skill.
- **Segurança:** Paths fixos ou derivados de `$HOME`; sem upload para terceiros.

---

## 3. Alertas

- **Tipos:** (a) alert-at X — notificar quando preço ≥ X%; (b) alert-change ±Y% — notificar quando variação em relação ao valor atual ultrapassar Y%.
- **Execução:** Comando de checagem (ex.: `alerts`) pode ser usado em **cron**; flag `--quiet` para só produzir saída quando houver disparo.
- **Integração com operações:** Conforme [13-habilidades-proativas.md](13-habilidades-proativas.md), crons que não precisam da sessão principal devem usar `isolated agentTurn` quando aplicável; o resultado pode ser resumido ao Diretor.

---

## 4. Calendário / prazos

- **Função:** Listar itens (eventos, mercados, entregas) que “resolvem” ou vencem nos próximos N dias.
- **Parâmetros:** `--days`, `--limit`.
- **Uso:** Morning brief, planejamento, priorização.

---

## 5. Momentum e digests

- **Momentum:** “Maiores movimentos” em um período (24h, 1w, 1m), com filtros opcionais (ex.: volume mínimo).
- **Digests:** Resumos por categoria (ex.: política, crypto, esportes); úteis para crons semanais.
- **Saída:** Dados estruturados ou texto legível (odds, variação, volume, bid/ask quando fizer sentido).

---

## 6. Simulação local (paper trading)

- **Objetivo:** Acompanhar “posições” e P&L sem dinheiro real, sem wallet, sem blockchain.
- **Persistência:** Diretório local (ex.: `~/.skill-name/`) com arquivos JSON (portfolio, histórico de trades).
- **Operações:** buy (valor simulado), sell, portfolio.
- **Segurança:** Nenhuma conexão com carteira ou conta financeira; nenhuma transação real; dados apenas no host. Revisar script da skill antes do primeiro uso ([05-seguranca-e-etica.md](05-seguranca-e-etica.md)).

---

## Quando usar estas habilidades

- **Descoberta de skills:** Ao buscar skills para “dados”, “mercados”, “alertas”, “watchlist”, “paper trading”, usar [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) e verificar se a skill se encaixa nestas categorias e se cumpre Zero Trust.
- **Proposta ao Diretor:** Apresentar o que a skill faz (consulta, watchlist, alertas, simulação), onde os dados são armazenados e que não há autenticação financeira nem envio de dados sensíveis, quando for o caso.
- **Crons e heartbeats:** Alertas e digests podem ser agendados; preferir sessão isolada para não ocupar a sessão principal ([13-habilidades-proativas.md](13-habilidades-proativas.md)).

---

## Quem pode usar

| Agente | Consulta dados | Watchlist / alertas | Simulação (paper) |
|--------|----------------|---------------------|-------------------|
| **CEO** | Sim (pesquisa, tendências) | Sim (se aprovado) | Sim (análise, sem real money) |
| **PO** | Conforme permissão de rede | Conforme aprovação | Conforme aprovação |
| **DevOps** | Sim (operar/instalar skill) | Sim | Sim |
| **Outros** | Conforme tarefa e aprovação | Conforme tarefa e aprovação | Conforme tarefa e aprovação |

Instalação de novas skills segue sempre o fluxo de [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) e checklist de [05-seguranca-e-etica.md](05-seguranca-e-etica.md).

---

## Relação com a documentação

- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — Descoberta e instalação de skills; categorias “dados, watchlist, alertas, simulação” podem ser buscadas e propostas aqui.
- [13-habilidades-proativas.md](13-habilidades-proativas.md) — Crons autônomo vs promptado; alertas e digests em sessão isolada; resourcefulness (usar skills antes de desistir).
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Zero Trust, checklist de skills de terceiros, revisão antes do primeiro uso.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validação de URLs, comandos e paths ao executar skills.
- [21-auto-atualizacao-ambiente.md](21-auto-atualizacao-ambiente.md) — Skills instaladas (incluindo as que oferecem essas habilidades) são atualizadas pela rotina de auto-atualização.
