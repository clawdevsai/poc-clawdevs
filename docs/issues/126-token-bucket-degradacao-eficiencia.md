# [team-devs-ai] Token bucket para eventos de estratégia e degradação por eficiência

**Fase:** 2 — Segurança / 4 — Configuração  
**Labels:** governance, finops, gateway, ceo

## Descrição

Implementar no Gateway (ou orquestrador) controles de taxa **determinísticos** para a governança do agente executivo (CEO), evitando paralisia por exaustão financeira antes de a cota $5/dia ser atingida. Dois mecanismos: (1) **token bucket** para eventos de estratégia; (2) **degradação por eficiência** com rebaixamento para modelo local em CPU quando a razão ideias CEO vs tarefas aprovadas pelo PO cair abaixo do limiar.

## Critérios de aceite

- [ ] **Token bucket:** contador no orquestrador (ex.: Redis) para eventos com **tag de estratégia** (ex.: canal `cmd:strategy` ou metadado equivalente). Limite por janela configurável (ex.: **máximo 5 eventos por hora**). Se o CEO tentar emitir além do limite, o Gateway **intercepta**: enfileirar para a próxima janela ou descartar e devolver erro ao agente para aguardar. Documentar em [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) e [03-arquitetura.md](../03-arquitetura.md).
- [ ] **Degradação por eficiência:** orquestrador mede a **razão** entre ideias/diretrizes geradas pelo CEO e épicos ou tarefas **aprovadas pelo PO**. Se a taxa cair **abaixo de limiar configurável**, bloquear temporariamente requisições ao modelo em nuvem para o CEO e **forçar roteamento para modelo local em CPU** (ex.: Phi-3). Objetivo: refinar ideias na fila em vez de gerar volume novo; esteira segue sem consumir cota de API. Documentar em [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) e [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).
- [ ] **$5/dia** permanece **freio de emergência** (última linha de defesa); token bucket e degradação por eficiência são o **controle primário** sustentável.

## Implementação (início Fase 2)

- **Script de referência** [scripts/gateway_token_bucket.py](../../scripts/gateway_token_bucket.py): token bucket (Redis, janela 1 h) e verificação de degradação por eficiência (razão PO aprovadas / CEO ideias). Uso: Gateway chama `check_bucket` antes de publicar em cmd:strategy; `record` após publicar; `check_degrade` para decidir rotear CEO para modelo local.
- **Documentação:** [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) § 2.1 (Token bucket e Degradação por eficiência). Variáveis: `TOKEN_BUCKET_MAX_PER_HOUR`, `EFFICIENCY_RATIO_MIN`, `REDIS_HOST`, `REDIS_PORT`.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (System Prompt CEO, alerta imediato)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Controle de FinOps no Gateway, perfis CEO)
- [03-arquitetura.md](../03-arquitetura.md) (Estágio de borda)
- [soul/CEO.md](../soul/CEO.md)
