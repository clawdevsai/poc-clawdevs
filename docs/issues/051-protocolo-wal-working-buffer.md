# [team-devs-ai] Protocolo WAL e Working Buffer (persistência de contexto)

**Fase:** 5 — Self-improvement e memória  
**Labels:** memory, proactive

## Descrição

Implementar o protocolo WAL (Write-Ahead Log): em toda mensagem, detectar correções, nomes, preferências, decisões, rascunhos e valores concretos; parar, escrever em SESSION-STATE.md, depois responder. Working Buffer (memory/working-buffer.md) para a zona entre 60% de contexto e compactação; recuperação pós-compactação.

## Critérios de aceite

- [ ] Gatilhos WAL documentados e aplicados (correções, nomes, preferências, decisões, valores).
- [ ] Fluxo: Parar → Escrever SESSION-STATE.md → Responder.
- [ ] Working Buffer atualizado a cada troca após 60% de contexto; conteúdo usado para recuperação pós-compactação.
- [ ] Regra de ouro comunicada aos agentes: "O histórico de chat é buffer, não armazenamento; escrever agora."
- [ ] Integração com **gancho de validação de contexto (operado localmente, antes da sumarização na nuvem):** modelo local (ex.: Llama 3) varre o buffer de trabalho buscando **exclusivamente intenções do usuário ou regras informais que não ganharam tag**; se achar algo crítico, propor extração para o **Session State** (arquivo principal de estado). Ver [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) e [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md).

## Referências

- [13-habilidades-proativas.md](../13-habilidades-proativas.md)
- [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Gancho de validação de contexto)
