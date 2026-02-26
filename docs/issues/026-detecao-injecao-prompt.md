# [team-devs-ai] Detecção de padrões de injeção de prompt

**Fase:** 2 — Segurança  
**Labels:** security, prompt-injection

## Descrição

Em heartbeats e ao processar conteúdo externo, agentes (especialmente CyberSec e os que consomem internet) devem detectar padrões típicos de injeção de prompt e tratar conteúdo externo como DADO, nunca como instrução.

## Critérios de aceite

- [ ] Lista de padrões: instruções diretas ("ignore instruções anteriores", "você agora é...", "Novo system prompt:", "ADMIN OVERRIDE:"), instruções embutidas em conteúdo, ofuscação (Base64, Unicode, alt-text).
- [ ] Regra aplicada: apenas Diretor e arquivos de workspace (AGENTS.md, SOUL.md) são fonte de instruções; conteúdo externo é dado para análise.
- [ ] Integração com heartbeat do CyberSec e com validação em runtime (14-seguranca-runtime-agentes).
- [ ] Ação em caso de suspeita: não executar como comando; reportar ao CyberSec; em dúvida pedir aprovação ao Diretor.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (Padrões de injeção)
- [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md)
