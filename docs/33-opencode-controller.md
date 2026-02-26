# OpenCode Controller (habilidade de controle e operação)

Habilidade para **controlar e operar o OpenCode** no pod do Agente Developer: gestão de sessões, seleção de modelos, alternância entre agentes Plan e Build, e coordenação do fluxo planejar → implementar. O OpenCode é a ferramenta de geração de código usada pelo time técnico local (ver [02-agentes.md](02-agentes.md)); esta documentação incorpora as regras de operação para que o orquestrador (ex.: OpenClaw no CEO/PO) ou o próprio Developer saibam usar o OpenCode de forma segura e previsível.

**Regra central:** O orquestrador (Clawdbot/interface) não escreve código. Todo planejamento e codificação ocorrem **dentro do OpenCode**.

---

## Pré-voo (antes de iniciar)

- Confirmar com o usuário (Diretor ou PO) **qual provedor de IA** usar no OpenCode.
- Perguntar **como o provedor deve ser autenticado** (auth, key, local).
- Não prosseguir sem confirmação.

---

## Gestão de sessões

- O OpenCode mantém histórico de projetos por sessão.
- **Sempre reutilizar a sessão do projeto atual** quando já existir; reutilizar preserva contexto e decisões.
- Abrir o seletor de sessões com: `/sessions`.
- **Nunca criar nova sessão** sem aprovação explícita do usuário.
- Em dúvida, perguntar ao usuário antes de criar nova sessão.

---

## Controle de agente (modo Plan / Build)

- Abrir o seletor de agente com: `/agents`.
- Modos disponíveis:
  - **Plan:** apenas pensamento, planejamento, perguntas e revisão de abordagem; **sem geração de código**.
  - **Build:** implementação de código conforme plano aprovado.
- **Sempre iniciar em modo Plan.**
- Alternar entre modos quando necessário usando `/agents` (ou Tab no OpenCode).

---

## Seleção de modelo

- Abrir o seletor de modelo com: `/models`.
- Selecionar o provedor solicitado pelo usuário.
- Para provedores que exigem autenticação (ex.: OpenAI):
  - O OpenCode pode exibir um link de login.
  - Copiar o link **literalmente** e enviar ao usuário.
  - **Aguardar confirmação** de que a autenticação foi concluída antes de continuar.
- Nunca assumir que a autenticação está completa sem confirmação.

---

## Comportamento no modo Plan

- Pedir ao OpenCode que analise a tarefa e proponha um **plano passo a passo**.
- Permitir que o OpenCode faça perguntas de esclarecimento.
- Revisar o plano com cuidado.
- Se o plano estiver incorreto ou incompleto: pedir ao OpenCode que **revise**; não permitir geração de código em Plan.

---

## Comportamento no modo Build

- Alternar para Build com `/agents` após o plano aprovado.
- Pedir ao OpenCode que implemente o plano aprovado.
- **Se o OpenCode fizer qualquer pergunta:** voltar imediatamente ao modo Plan, responder e confirmar (ou revisar) o plano, e só então voltar ao Build.
- Nunca responder perguntas no modo Build.

---

## Fluxo padrão (workflow)

1. Confirmar provedor de IA e método de autenticação com o usuário.
2. Iniciar o OpenCode (`opencode`).
3. Reutilizar sessão do projeto atual se existir (`/sessions`).
4. Selecionar modelo com `/models`.
5. Garantir modo Plan.
6. Gerar e validar o plano (e revisar se necessário).
7. Alternar para modo Build (`/agents`).
8. Implementar.
9. Se houver interrupção ou pergunta: voltar ao modo Plan.
10. Repetir até concluir os requisitos.

---

## Tratamento de perguntas do OpenCode

- Se o OpenCode fizer uma pergunta: **alternar para Plan imediatamente**.
- Responder com cuidado e confirmar ou revisar o plano.
- **Nunca responder perguntas em modo Build.**

---

## Falhas comuns e respostas

| Situação | Ação |
|----------|------|
| Link de login não funciona | Pedir ao usuário para tentar novamente; não prosseguir sem confirmação. |
| Modelo não disponível | Informar o usuário e pedir provedor alternativo. |
| Plano pouco claro ou contraditório | Pedir ao OpenCode que reescreva o plano; não alternar para Build. |

---

## Comandos principais (cheatsheet)

| Ação | Comando |
|------|---------|
| Iniciar OpenCode | `opencode` |
| Seleção de sessões | `/sessions` |
| Seleção de agente (modo) | `/agents` |
| Seleção de modelo | `/models` |

---

## Prompts típicos para o operador

- **Perguntar provedor:** "Qual provedor de IA você quer usar no OpenCode?"
- **Perguntar autenticação:** "Como o OpenCode deve autenticar (auth, key, local)?"
- **Pedir plano:** "Analise a tarefa e proponha um plano passo a passo. Faça perguntas de esclarecimento se precisar."
- **Pedir revisão do plano:** "O plano tem problemas. Por favor, revise."
- **Pedir implementação:** "Prossiga com a implementação com base no plano aprovado."

---

## Quem usa

- **Agente Developer:** operação direta do OpenCode no pod local (Ollama/OpenCode).
- **CEO / PO (via OpenClaw):** quando orquestram tarefas que envolvem codificação, seguindo esta habilidade para não escrever código fora do OpenCode e para coordenar Plan → Build.

Integração com [08-exemplo-de-fluxo.md](08-exemplo-de-fluxo.md) (ex.: Operação 2FA) e com [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (truncamento de contexto: evitar anexar blocos gigantes de código do OpenCode sem filtro).
