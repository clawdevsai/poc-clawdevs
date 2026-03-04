# [team-devs-ai] Five strikes com fallback contextual e arbitragem na nuvem

**Fase:** 3 — Operações  
**Labels:** ops, autonomy, escalation  
**Depende de:** [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md)

## Descrição

Implementar o fluxo **five strikes** com fallback contextual: 2º strike aciona o Architect para gerar código que aprovaria o PR; 5º strike empacota contexto e roteia para **arbitragem na nuvem** (modelo superior reescreve). Abandono da tarefa **apenas** se a escalação falhar; caso contrário a issue **volta ao backlog do PO** e o PO, com o Architect, devolve a tarefa ao desenvolvimento. Objetivo: não perder tarefas críticas por impasse Developer–Architect.

## Critérios de aceite

- [ ] **Contagem de strikes por tarefa/PR:** orquestrador mantém contador (ex.: chave Redis `project:v1:issue:{id}:strikes`) incrementado em cada rejeição do Architect (ou QA/CyberSec conforme matriz). Documentar em [06-operacoes.md](../06-operacoes.md).
- [ ] **2º strike — Fallback Architect:** ao atingir 2 strikes, orquestrador injeta **prompt de compromisso** no Architect: gerar o código exato que tornaria o PR aprovável (patch ou instruções determinísticas). Developer recebe o output e reaplica; se aprovado, contador de strikes da tarefa é zerado. Documentar em 06 e em soul/Architect.
- [ ] **5º strike — Escalação para arbitragem na nuvem:** ao atingir 5 strikes, orquestrador **empacota contexto** (diff, critérios de aceite, histórico de prompts e rejeições) e publica evento para **arbitragem na nuvem** (modelo superior, ex.: via OpenRouter/Gemini). Se a arbitragem retornar solução aplicável, aplicar no repositório e marcar tarefa como concluída; se **escalação falhar** (timeout, erro de API, resposta inválida), issue **volta ao backlog do PO** (Developer pega próxima tarefa).
- [ ] **PO + Architect retorno ao desenvolvimento:** quando a issue volta ao backlog por 5º strike com falha de escalação, **PO** analisa **todo o histórico** com o **Architect** e define solução (critérios ajustados, escopo reduzido ou abordagem alternativa); tarefa **retorna ao desenvolvimento** (não se perde). Registrar em MEMORY.md ou artefato equivalente. Documentar em [06-operacoes.md](../06-operacoes.md) e [01-visao-e-proposta.md](../01-visao-e-proposta.md).
- [ ] Integração com orquestrador existente ([scripts/orchestrator_autonomy.py](../../scripts/orchestrator_autonomy.py)) e com chaves/eventos de degradação (relatório ao pausar).

## Referências

- [017-autonomia-nivel-4-matriz-escalonamento.md](017-autonomia-nivel-4-matriz-escalonamento.md) (especificação completa)
- [06-operacoes.md](../06-operacoes.md) (Five strikes, workflow de recuperação)
