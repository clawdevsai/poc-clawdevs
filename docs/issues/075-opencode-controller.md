# [team-devs-ai] OpenCode Controller (sessões, modelo, Plan/Build)

**Fase:** 7 — Ferramentas  
**Labels:** tooling, opencode, developer

## Descrição

Habilidade para controlar e operar o OpenCode no pod do Developer: gestão de sessões (/sessions), seleção de modelo (/models), modos Plan e Build (/agents), fluxo planejar→implementar, tratamento de perguntas e falhas. Regra: orquestrador não escreve código; todo código dentro do OpenCode.

## Critérios de aceite

- [x] Pré-voo: confirmar provedor de IA e autenticação com usuário antes de iniciar. **Ref:** [33-opencode-controller.md](../33-opencode-controller.md) § Pré-voo.
- [x] Gestão de sessões: reutilizar sessão do projeto atual; /sessions; nunca criar nova sessão sem aprovação. **Ref:** Doc 33 § Gestão de sessões.
- [x] Controle de agente: /agents; sempre iniciar em modo Plan; alternar para Build quando plano aprovado. **Ref:** Doc 33 § Controle de agente (modo Plan/Build).
- [x] Seleção de modelo: /models; se auth necessária, enviar link ao usuário e aguardar confirmação. **Ref:** Doc 33 § Seleção de modelo.
- [x] Comportamento em Plan: analisar tarefa, propor plano, permitir perguntas, revisar; não gerar código em Plan. **Ref:** Doc 33 § Comportamento no modo Plan.
- [x] Comportamento em Build: implementar conforme plano; tratar perguntas e falhas (documentado). **Ref:** Doc 33 § Comportamento no modo Build, § Tratamento de perguntas do OpenCode, § Falhas comuns e respostas.
- [x] Documentação para CEO/PO e Developer sobre quando e como usar o OpenCode. **Ref:** Doc 33 § Quem usa, § Fluxo padrão (workflow), § Comandos principais, § Prompts típicos; [02-agentes.md](../02-agentes.md) (Developer opera OpenCode no pod).

## Referências

- [33-opencode-controller.md](../33-opencode-controller.md)
