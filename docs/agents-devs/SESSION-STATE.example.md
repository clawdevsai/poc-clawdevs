# SESSION-STATE — Estado da sessão (exemplo)

Arquivo principal de estado da sessão. Regras absolutas do Diretor devem usar a **tag de invariante** para que o script de limpeza do DevOps **nunca** as apague (truncamento-finops).

Ref: docs/07-configuracao-e-prompts.md (2.3 Invariantes de negócio), docs/issues/041-truncamento-contexto-finops.md.

---

## Invariantes de negócio (nunca sumarizar nem apagar)

<!-- INVARIANTE_NEGOCIO -->
- Token de login expira em 5 minutos.
- Senha mínima 12 caracteres, pelo menos um número e um símbolo.
- API pública rate limit: 100 req/min por IP.
<!-- /INVARIANTE_NEGOCIO -->

---

## Contexto da sessão (podem ser compactados com regex que preserva blocos acima)

- Tarefa atual: issue #42
- Última decisão: PO aprovou escopo em 2025-03-02.
