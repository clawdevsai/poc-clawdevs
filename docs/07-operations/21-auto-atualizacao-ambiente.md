# Auto-atualização do ambiente (runtime e skills)

Os agentes do enxame podem **configurar e executar atualizações automáticas** do ambiente de execução (runtime do orquestrador, ex.: OpenClaw/Clawdbot) e de **todas as skills já instaladas**, com verificação periódica (ex.: diária), aplicação de atualizações e **resumo claro ao Diretor** do que foi alterado. Este documento define a habilidade, quem a executa, como configurar (cron, sessão isolada) e como reportar, alinhado à **postura Zero Trust** e à [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) (instalação de *novas* skills continua exigindo aprovação; aqui trata-se apenas de **atualizar** o que já está instalado).

**Segurança:** Atualizar o runtime e skills já aprovadas é permitido no escopo definido abaixo; **instalar** novas skills continua exigindo descoberta, checklist de segurança e aprovação do Diretor (ver [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) e [05-seguranca-e-etica.md](05-seguranca-e-etica.md)).

---

## O que esta habilidade faz

1. **Atualiza o runtime** do orquestrador (ex.: Clawdbot via `clawdbot update` / `npm update -g clawdbot@latest`, ou equivalente no seu ambiente).
2. **Atualiza todas as skills instaladas** (ex.: `clawdhub update --all` ou `npx skills update`), sem adicionar novas skills sem aprovação.
3. **Roda em horário configurado** (ex.: cron diário às 4h) em **sessão isolada**, para não consumir a atenção da sessão principal.
4. **Envia um resumo** ao Diretor (ou ao canal configurado): versão do runtime antes/depois, lista de skills atualizadas (nome, versão antiga → nova), skills já atualizadas, e eventuais erros.

Assim, o time mantém o ambiente atualizado sem intervenção manual constante, e o Diretor fica informado do que mudou.

---

## Quando usar

- O Diretor pede "configurar atualizações automáticas do ambiente e das skills".
- O time quer garantir que o runtime e as skills instaladas recebam patches e melhorias periodicamente.
- Manutenção proativa: incluir a verificação de atualizações no heartbeat ou em cron (ver [13-habilidades-proativas.md](13-habilidades-proativas.md)).

Não usar para **instalar** skills novas; para isso, usar o fluxo de [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md).

---

## Quem configura e quem executa

| Papel | Configurar cron / job | Executar atualizações | Receber resumo |
|-------|------------------------|------------------------|----------------|
| **DevOps/SRE** | Sim (cron, sessão isolada) | Sim | Sim (e encaminhar ao Diretor conforme config) |
| **Diretor** | Pode solicitar | Não precisa | Sim |
| **Outros agentes** | Não | Não | Podem ser citados no resumo se configurado |

A configuração do cron (ou equivalente) deve ser feita por quem tem permissão operacional (ex.: DevOps); a execução pode ser automatizada em sessão isolada para não bloquear a sessão principal.

---

## Como funciona (visão geral)

### 1. Detectar tipo de instalação do runtime

Antes de configurar, o agente deve identificar como o runtime está instalado para escolher o comando correto:

- **npm/pnpm/bun global:** `npm list -g clawdbot`, `pnpm list -g clawdbot`, ou equivalente.
- **Instalação a partir do código (git):** verificar se existe repositório do runtime (ex.: `~/.clawdbot/.git` ou caminho equivalente).
- **Skills:** no ecossistema Skills CLI, usar `npx skills check` / `npx skills update`; no ClawdHub, `clawdhub list` e `clawdhub update --all`.

### 2. Criar o job periódico (cron ou equivalente)

- **Horário:** por exemplo 4:00 (configurável; ex.: `0 4 * * *` em cron).
- **Timezone:** configurável (ex.: `America/Sao_Paulo`).
- **Sessão:** usar **sessão isolada** (ex.: `isolated agentTurn`), para que a tarefa rode em background e não dependa da sessão principal.
- **Entrega:** configurar para enviar o resumo ao Diretor (ex.: canal Telegram, ou arquivo no workspace lido na próxima sessão).

Exemplo de ideia de prompt para o cron (adaptar ao orquestrador real):

```text
Executar rotina diária de auto-atualização:
1. Verificar e atualizar o runtime (comando conforme tipo de instalação; depois rodar doctor/verificação se existir).
2. Atualizar todas as skills instaladas (clawdhub update --all ou npx skills update).
3. Reportar: versão do runtime antes/depois; skills atualizadas (nome, versão antiga → nova); skills já atuais; erros encontrados.
Formato do resumo: claro e escaneável (ver seção "Formato do resumo" neste doc).
```

### 3. Comandos típicos (referência)

**Runtime (ex.: Clawdbot):**

- Atualizar: `npm update -g clawdbot@latest` (ou pnpm/bun); ou `clawdbot update` em instalação a partir do código.
- Pós-atualização: `clawdbot doctor --yes` (quando existir).
- Versão: `clawdbot --version`.

**Skills (ClawdHub):**

- Listar: `clawdhub list`
- Atualizar todas: `clawdhub update --all`
- Simular (sem aplicar): `clawdhub update --all --dry-run`

**Skills (Skills CLI – npx skills):**

- Verificar atualizações: `npx skills check`
- Atualizar: `npx skills update`

### 4. Verificação após configuração

- Confirmar que o cron (ou job) foi criado: listar jobs (ex.: `clawdbot cron list` ou equivalente).
- Testar manualmente os comandos de atualização e a geração do resumo antes de confiar no cron.

---

## Formato do resumo para o Diretor

O resumo deve ser **curto, escaneável e informativo**. Exemplos de formato (adaptar ao contexto):

**Quando houve atualizações:**

```text
🔄 Auto-atualização concluída

**Runtime:** v2026.1.9 → v2026.1.10

**Skills atualizadas (3):**
- prd: 2.0.3 → 2.0.4
- browser: 1.2.0 → 1.2.1
- nano-banana-pro: 3.1.0 → 3.1.2

**Skills já atuais (5):** gemini, sag, things-mac, himalaya, peekaboo

✅ Concluído sem erros.
```

**Quando não há atualizações:**

```text
🔄 Verificação de auto-atualização

**Runtime:** v2026.1.10 (já na versão mais recente)
**Skills:** Todas as 8 skills instaladas estão atuais.

Nada a atualizar hoje.
```

**Quando há erros:**

```text
🔄 Auto-atualização concluída (com problemas)

**Runtime:** v2026.1.9 → v2026.1.10 ✅

**Skills atualizadas (1):** prd: 2.0.3 → 2.0.4 ✅

**Skills com falha (1):** ❌ nano-banana-pro — timeout ao baixar v3.1.2. Sugestão: rodar atualização manual depois.

**Skills já atuais (6):** gemini, sag, things-mac, himalaya, peekaboo, browser

⚠️ Concluído com 1 erro. Detalhes acima.
```

Diretrizes: usar emojis com moderação (ex.: 🔄 no título, ✅/❌ no status); agrupar por “atualizadas” vs “já atuais” vs “com falha”; sempre mostrar versões antes → depois; destacar erros.

---

## Customização

- **Horário:** alterar expressão cron (ex.: 6h → `0 6 * * *`).
- **Frequência:** semanal em vez de diária (ex.: domingo 4h → `0 4 * * 0`).
- **Timezone:** configurar `--tz` (ou equivalente) para o fuso do Diretor.
- **Canal de entrega:** enviar resumo para Telegram, e-mail ou arquivo no workspace, conforme capacidade do orquestrador.

---

## Tratamento de erros

- Registrar qualquer falha no resumo (runtime ou skill específica).
- Reportar sucesso parcial quando aplicável (ex.: runtime atualizado, uma skill falhou).
- Sugerir ação manual quando fizer sentido (ex.: “rodar `clawdhub update nome-da-skill` manualmente”).
- Erros comuns: permissão (EACCES) → sugerir ajuste de permissões ou execução por quem tem permissão; rede → retentar uma vez e depois reportar; conflitos em instalação a partir do código → sugerir comando de atualização forçada se existir.

---

## Desabilitar auto-atualização

- Remover o job: ex.: `clawdbot cron remove "Daily Auto-Update"` (ou equivalente no seu orquestrador).
- Ou desativar temporariamente na configuração (ex.: `cron.enabled: false`) sem apagar o job.

---

## Relação com a documentação

- [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) — Descoberta e **instalação** de novas skills (buscar, propor, instalar só após aprovação). Este doc trata de **atualizar** o que já está instalado.
- [13-habilidades-proativas.md](13-habilidades-proativas.md) — Crons e sessão isolada; heartbeat e manutenção proativa; incluir verificação de atualizações quando fizer sentido.
- [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) — Configuração de cron e canais de entrega no OpenClaw/orquestrador.
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Zero Trust; atualização de pacotes já aprovados está no escopo; instalação de novos pacotes/skills segue o fluxo de aprovação.
- [02-agentes.md](02-agentes.md) — DevOps/SRE como responsável por configurar e executar a rotina de auto-atualização; Diretor recebe o resumo.
