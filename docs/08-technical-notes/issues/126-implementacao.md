# Token bucket e degradação por eficiência (126) — Implementação

**Script:** [scripts/gateway_token_bucket.py](../../scripts/gateway_token_bucket.py) — `check_bucket` (limite por hora), `record_strategy_event`, `should_degrade_ceo_to_local` (razão PO/CEO + preditivo).

**Gateway:** [gateway_redis_adapter.py](../../scripts/gateway_redis_adapter.py) chama `check_token_bucket` antes de publicar em `cmd:strategy`; se limite excedido retorna 429 com `error: token_bucket_limit`. Variável `PHASE2_TOKEN_BUCKET_ENABLED` (env).

**Documentação:** [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.1 (Token bucket, Degradação por eficiência); [03-arquitetura.md](../03-arquitetura.md) (estágio de borda). Variáveis: `TOKEN_BUCKET_MAX_PER_HOUR`, `EFFICIENCY_RATIO_MIN`, `KEY_STRATEGY_COUNT`, `KEY_CEO_IDEAS`, `KEY_PO_APPROVED`.

**$5/dia:** Permanece freio de emergência; token bucket e degradação são controle primário (doc 07 §2.1).

Ref: [126-token-bucket-degradacao-eficiencia.md](126-token-bucket-degradacao-eficiencia.md).
