# [team-devs-ai] OpenCode Controller (sessões, modelo, Plan/Build)

**Fase:** 7 — Ferramentas  
**Labels:** tooling, opencode, developer

## Descrição

Habilidade para controlar e operar o OpenCode no pod do Developer: gestão de sessões (/sessions), seleção de modelo (/models), modos Plan e Build (/agents), fluxo planejar→implementar, tratamento de perguntas e falhas. Regra: orquestrador não escreve código; todo código dentro do OpenCode.

## Critérios de aceite

- [ ] Pré-voo: confirmar provedor de IA e autenticação com usuário antes de iniciar.
- [ ] Gestão de sessões: reutilizar sessão do projeto atual; /sessions; nunca criar nova sessão sem aprovação.
- [ ] Controle de agente: /agents; sempre iniciar em modo Plan; alternar para Build quando plano aprovado.
- [ ] Seleção de modelo: /models; se auth necessária, enviar link ao usuário e aguardar confirmação.
- [ ] Comportamento em Plan: analisar tarefa, propor plano, permitir perguntas, revisar; não gerar código em Plan.
- [ ] Comportamento em Build: implementar conforme plano; tratar perguntas e falhas (documentado).
- [ ] Documentação para CEO/PO e Developer sobre quando e como usar o OpenCode.

## Referências

- [33-opencode-controller.md](../33-opencode-controller.md)
