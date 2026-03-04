# Exemplo: critérios de aceite com tag de proteção (truncamento-finops)

Os critérios de aceite **não** podem estar no mesmo buffer que é sumarizado — senão o PO perde a referência para validação reversa. Use a **tag de proteção** para que o script de limpeza/compacted do DevOps **nunca** apague nem envie ao sumarizador este bloco.

Ref: docs/07-configuracao-e-prompts.md (2.2 Segregação dos critérios de aceite), docs/issues/041-truncamento-contexto-finops.md.

---

## Issue #42 — Autenticação 2FA

Descrição da tarefa...

<!-- CRITERIOS_ACEITE -->
1. Usuário pode habilitar 2FA pelo perfil.
2. Código TOTP válido por 30 segundos; máximo 3 tentativas por minuto.
3. Tokens de backup: 10 códigos de uso único, exibidos uma vez.
4. Sem 2FA: login normal; com 2FA: segundo fator obrigatório após senha.
<!-- /CRITERIOS_ACEITE -->

---

O PO compara o **resumo** gerado (após sumarização) com os critérios acima **intactos**. Se o resumo omitir um critério fundamental, o PO **rejeita o truncamento** e o sistema reestrutura o bloco.
