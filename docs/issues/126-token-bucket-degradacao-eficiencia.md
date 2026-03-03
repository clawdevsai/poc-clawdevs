# [team-devs-ai] Token bucket para eventos de estratégia e degradação por eficiência

**Fase:** 2 — Segurança / 4 — Configuração  
**Labels:** governance, finops, gateway, ceo

## Descrição

Implementar no Gateway (ou orquestrador) controles de taxa **determinísticos** para a governança do agente executivo (CEO), evitando paralisia por exaustão financeira antes de a cota $5/dia ser atingida. Dois mecanismos: (1) **token bucket** para eventos de estratégia; (2) **degradação por eficiência** com rebaixamento para modelo local em CPU quando a razão ideias CEO vs tarefas aprovadas pelo PO cair abaixo do limiar.

## Critérios de aceite

- [x] **Token bucket:** contador no orquestrador (Redis) para eventos em `cmd:strategy`. Limite por janela configurável (ex.: 5 eventos/hora). Gateway intercepta e devolve erro quando excedido. **Ref:** [gateway_token_bucket.py](../../scripts/gateway_token_bucket.py), [gateway_redis_adapter.py](../../scripts/gateway_redis_adapter.py) (check_token_bucket antes de publicar); [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.1, [03-arquitetura.md](../03-arquitetura.md); [126-implementacao.md](126-implementacao.md).
- [x] **Degradação por eficiência:** orquestrador mede razão PO aprovadas / CEO ideias; abaixo do limiar → rotear CEO para modelo local. **Ref:** `gateway_token_bucket.py` (`should_degrade_ceo_to_local`); doc 07 §2.1, [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).
- [x] **$5/dia** permanece **freio de emergência**; token bucket e degradação são o **controle primário** sustentável. **Ref:** Doc 07 §2.1, constraint CEO.

## Implementação (início Fase 2)

- **Script de referência** [scripts/gateway_token_bucket.py](../../scripts/gateway_token_bucket.py): token bucket (Redis, janela 1 h) e verificação de degradação por eficiência (razão PO aprovadas / CEO ideias). Uso: Gateway chama `check_bucket` antes de publicar em cmd:strategy; `record` após publicar; `check_degrade` para decidir rotear CEO para modelo local.
- **Documentação:** [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) § 2.1 (Token bucket e Degradação por eficiência). Variáveis: `TOKEN_BUCKET_MAX_PER_HOUR`, `EFFICIENCY_RATIO_MIN`, `REDIS_HOST`, `REDIS_PORT`.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (System Prompt CEO, alerta imediato)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Controle de FinOps no Gateway, perfis CEO)
- [03-arquitetura.md](../03-arquitetura.md) (Estágio de borda)
- [soul/CEO.md](../soul/CEO.md)
