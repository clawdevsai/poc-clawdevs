# [team-devs-ai] Modelos gratuitos OpenRouter (FreeRide)

**Fase:** 8 — Skills e ambiente  
**Labels:** config, cost, openrouter

## Descrição

Configurar OpenClaw para usar modelos gratuitos do OpenRouter (FreeRide): ranking, fallbacks, rate limit. Comandos freeride; uso por DevOps após aprovação do Diretor; alinhado a custo e descoberta de skills. **Roteamento hierárquico** e **recuperação de estado** para evitar deadlock quando nuvem e GPU estiverem saturadas.

## Critérios de aceite

- [ ] Documentação de como configurar OpenClaw para modelos FreeRide (OpenRouter): ranking, fallbacks, rate limit.
- [ ] **Fallbacks hierárquicos:** config `agents.defaults.model.fallbacks` inclui último fallback estrutural para modelo local leve em **CPU** (ex.: Phi-3 Mini), unificando nuvem → GPU → CPU; documentar risco de memória/qualidade quando usar CPU.
- [ ] **Hook de recuperação:** script/daemon FreeRide (ex.: script-free-ride-auto, freeride-watcher) implementa hook que, quando nuvem e GPU local estiverem saturadas, instrui OpenClaw a **pausar a fila do Sessions-Spawn** (evitar deadlock e loop infinito).
- [ ] **Estado de pausa no LanceDB:** ao pausar sub-agente por saturação, OpenClaw serializa árvore de raciocínio e persiste no LanceDB (warm store); ao receber do Redis evento de liberação do GPU Lock, recupera estado do LanceDB e agente continua do ponto exato.
- [ ] Comandos ou passos "freeride" documentados (ex.: listar modelos gratuitos, aplicar config).
- [ ] Regra: DevOps executa após aprovação do Diretor; não alterar em produção sem aprovação.
- [ ] Aviso sobre limites e expectativas (prototipagem, test drive) documentado.

## Referências

- [22-modelos-gratuitos-openrouter-freeride.md](../../07-operations/22-modelos-gratuitos-openrouter-freeride.md)

## Verificação (Fase 8)

- Roteamento hierárquico (nuvem → GPU → CPU), hook de recuperação e estado no LanceDB: documentados em [22-modelos-gratuitos-openrouter-freeride.md](../../07-operations/22-modelos-gratuitos-openrouter-freeride.md).
- FreeRide e descoberta de skills no fluxo do PO: seção "FreeRide e descoberta de skills no fluxo do PO" no doc 22.
