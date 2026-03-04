# [team-devs-ai] Balanceamento dinâmico GPU/CPU e TTL dinâmico

**Fase:** 11 — Avançado  
**Labels:** advanced, infra, k8s

## Descrição

Evolução **adicional** ao GPU Lock de fundação: o **TTL dinâmico** (por payload/linhas) e **node selectors** para DevOps/UX em CPU já são obrigatórios na Phase 0 (ver [006-gpu-lock-script.md](006-gpu-lock-script.md), [03-arquitetura.md](../03-arquitetura.md), [04-infraestrutura.md](../04-infraestrutura.md)). **Validação pré-GPU em CPU** (SLM para sintaxe/lint/SOLID) e **batching de PRs** (revisão em lote pelo Architect) reduzem carga na GPU e contenção no lock — ver [03-arquitetura.md](../03-arquitetura.md) e [06-operacoes.md](../06-operacoes.md). Esta issue cobre: balanceamento dinâmico de cargas entre GPU e CPU para tarefas leves adicionais; node selectors avançados quando o cluster tiver nós distintos; PriorityClasses para evict gracioso sem intervenção humana. **Alinhar** com o **protocolo unificado de fallbacks** (nuvem → GPU → CPU) e **recuperação de estado via LanceDB** quando a fila for pausada por saturação (ver [093-modelos-gratuitos-openrouter-freeride.md](093-modelos-gratuitos-openrouter-freeride.md)).

## Critérios de aceite

- [ ] Balanceamento dinâmico: tarefas menos intensivas (ex.: análise de logs) em modelos leves (Phi-3) em CPU; documentação ou POC.
- [ ] TTL dinâmico já implementado na Phase 0 (issue 006); esta issue cobre refinamentos adicionais se necessário.
- [ ] Node selectors ou taints avançados para rotear tarefas CPU vs GPU (quando cluster tiver nós distintos; baseline DevOps/UX em CPU já em 006/004).
- [ ] Referência ao **roteamento hierárquico unificado** (fallbacks nuvem → GPU → CPU) e à **persistência/recuperação de estado no LanceDB** quando pausar por saturação (issue 093).
- [ ] PriorityClasses (Kubernetes): evict gracioso de pods de inferência de baixa prioridade em pico térmico ou carga excessiva, sem manual de primeiros socorros.
- [ ] Documentação de como isso reduz dependência do manual 06-operacoes.

## Referências

- [03-arquitetura.md](../../01-core/03-arquitetura.md) (Evolução: balanceamento dinâmico GPU/CPU; roteamento hierárquico)
- [04-infraestrutura.md](../../02-infra/04-infraestrutura.md)
- [06-operacoes.md](../../07-operations/06-operacoes.md)
- [093-modelos-gratuitos-openrouter-freeride.md](093-modelos-gratuitos-openrouter-freeride.md) (fallbacks hierárquicos, estado no LanceDB)

## Verificação (Fase 11)

- Balanceamento dinâmico, PriorityClasses, roteamento hierárquico e LanceDB: [balanceamento-dinamico-gpu-cpu.md](../../02-infra/balanceamento-dinamico-gpu-cpu.md) — tarefas leves em CPU (Phi-3), node selectors/taints, PriorityClasses (evict gracioso), § Roteamento hierárquico e estado no LanceDB (ref 093), § Como isso reduz dependência do manual 06-operacoes.
