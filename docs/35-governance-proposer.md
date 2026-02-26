# Governance Proposer (Propositor de Governança)

Agente que propõe ajustes a **rules**, **soul**, **skills**, **task** e outras **configurações dos agentes** em um **repositório Git dedicado** no GitHub. Validação humana obrigatória via Pull Request; após aprovação do Diretor e merge na main, o próprio agente aplica as modificações localmente (pull e sincronização com o workspace). Garante evolução segura da governança do enxame sem introduzir prompts maliciosos (gate humano no PR).

---

## Repositório separado (obrigatório)

- **Repo dedicado no GitHub:** Rules, soul, skills, task e demais configs dos agentes ficam em um **repositório Git separado** (ex.: `clawdevs-governance`, `skymed-agents-config`).
- **Vantagens:** Isolamento da governança; validação humana obrigatória no PR; aplicação local pelo agente só após merge aprovado pelo Diretor.

---

## Modelo e hardware

- **Inferência:** LLM **local** via **Ollama**, rodando em **CPU** (não disputa GPU Lock com Developer, Architect, QA etc.).
- **Modelo Ollama sugerido:** **Qwen 2.5:7B** (`qwen2.5:7b`). Boa relação qualidade/recursos para análise de texto, redação de propostas e geração de PRs em CPU.
- **Vantagem:** Custo zero de API; execução em sessão isolada (cron) sem competir por GPU. Ver [31-ollama-local.md](31-ollama-local.md).

---

## Cron: leitura periódica e busca na internet

- **Cron:** Periodicamente (ex.: diário ou semanal), o agente **lê** do repo dedicado no GitHub: rules, soul, skills, task e outras configurações de **todos** os agentes.
- **Busca na internet:** Pesquisa melhorias em sites como [ClawHub](https://clawhub.ai/) e outras referências (boas práticas, skills do ecossistema, padrões de prompts e governança). Usa o resultado para propor ajustes alinhados ao ecossistema.

---

## Fluxo em três fases

### Fase 1 — Leitura (cron) + busca internet

Ler o repo dedicado; buscar melhorias na internet (ClawHub e outros). Analisar e decidir quais propostas gerar.

### Fase 2 — Gerar PR e validação humana obrigatória

- Em **ambiente isolado** (clone efêmero do repo dedicado), o agente aplica as propostas de alteração, faz commit em branch, push e `gh pr create`.
- O PR que altera **rules, skills, soul, task ou outras configs** **deve** ser revisado e aprovado por um **humano (Diretor)** no GitHub. Nenhum merge automático; merge só após aprovação explícita do Diretor. Isso evita injeção de prompts maliciosos.

### Fase 3 — Pós-aprovação: o próprio agente aplica as modificações

- **Após** o PR ser aprovado pelo Diretor e **mergeado na main:** o **próprio agente** faz **pull** da main do repo dedicado e **sincroniza** com o workspace (ex.: OpenClaw SOUL.md, AGENTS.md, TOOLS.md ou volumes/configs dos agentes).
- Opcional: notificar o Diretor via Telegram que o PR foi mergeado e as alterações foram aplicadas localmente pelo agente.

---

## Permissões e restrições

- **Internet:** Leitura do repo dedicado, busca (ClawHub e outros), `gh` para push/PR e pull pós-merge.
- **Escrita local:** **Somente após** o Diretor aprovar e fazer merge na main. Antes do merge, edições só em clone efêmero do repo dedicado para abrir PR. O agente **nunca** faz merge de PR.
- **Validação humana:** Obrigatória para qualquer PR que altere rules, skills, soul, task ou configs no repo dedicado.
- **Sessão isolada:** Não consome filas Redis do dia a dia; roda em cron/janela dedicada.

---

## Segurança: sem prompts maliciosos

- **Validação humana obrigatória** do PR — nenhum merge automático nesse repo.
- **Aplicação local pelo agente só após aprovação:** O agente aplica no workspace **apenas** depois que o Diretor aprovou e fez merge na main. Todo conteúdo que entra no ambiente local passou pela revisão humana no PR.

---

## Relação com a documentação

- [02-agentes.md](02-agentes.md) — Definição do agente Governance Proposer (seção 10).
- [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) — Perfil (modelo qwen2.5:7b em CPU, skills, constraint).
- [10-self-improvement-agentes.md](10-self-improvement-agentes.md) — Curadoria workspace (Architect/CyberSec) vs Proposer (repo dedicado → PR → Diretor aprova e faz merge → agente aplica no workspace).
- [20-ferramenta-github-gh.md](20-ferramenta-github-gh.md) — Uso do `gh` para PRs e pull; nunca expor tokens.
- [31-ollama-local.md](31-ollama-local.md) — Ollama local, modelo em CPU (sem GPU Lock).
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Zero Trust, validação em runtime; escrita no workspace somente após merge aprovado pelo Diretor.
