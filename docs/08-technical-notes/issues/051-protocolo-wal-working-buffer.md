# [team-devs-ai] Protocolo WAL e Working Buffer (persistência de contexto)

**Fase:** 5 — Self-improvement e memória  
**Labels:** memory, proactive

## Descrição

Implementar o protocolo WAL (Write-Ahead Log): em toda mensagem, detectar correções, nomes, preferências, decisões, rascunhos e valores concretos; parar, escrever em SESSION-STATE.md, depois responder. Working Buffer (memory/working-buffer.md) para a zona entre 60% de contexto e compactação; recuperação pós-compactação.

## Critérios de aceite

- [x] Gatilhos WAL documentados e aplicados (correções, nomes, preferências, decisões, valores). **Ref:** [docs/agents-devs/protocolo-wal-working-buffer.md](../agents-devs/protocolo-wal-working-buffer.md) §1 (tabela de gatilhos); [13-habilidades-proativas.md](../13-habilidades-proativas.md).
- [x] Fluxo: Parar → Escrever SESSION-STATE.md → Responder. **Ref:** [protocolo-wal-working-buffer.md](../agents-devs/protocolo-wal-working-buffer.md) §2.
- [x] Working Buffer atualizado a cada troca após 60% de contexto; conteúdo usado para recuperação pós-compactação. **Ref:** [protocolo-wal-working-buffer.md](../agents-devs/protocolo-wal-working-buffer.md) §3 e §4; template em k8s/management-team/openclaw/workspace-ceo-configmap.yaml (working-buffer.md).
- [x] Regra de ouro comunicada aos agentes: "O histórico de chat é buffer, não armazenamento; escrever agora." **Ref:** [protocolo-wal-working-buffer.md](../agents-devs/protocolo-wal-working-buffer.md) (regra de ouro) e [13-habilidades-proativas.md](../13-habilidades-proativas.md); incluir em SOUL/AGENTS quando injetar workspace.
- [x] Integração com **gancho de validação de contexto (operado localmente, antes da sumarização na nuvem):** [scripts/context_validation_hook.py](../../scripts/context_validation_hook.py) varre o buffer buscando intenções/regras sem tag e propõe extração para SESSION-STATE. **Ref:** [protocolo-wal-working-buffer.md](../agents-devs/protocolo-wal-working-buffer.md) §5, [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md), [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md).

## Referências

- [13-habilidades-proativas.md](../13-habilidades-proativas.md)
- [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Gancho de validação de contexto)
