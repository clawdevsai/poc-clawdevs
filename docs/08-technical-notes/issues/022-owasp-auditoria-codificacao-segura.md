# [team-devs-ai] Segurança de aplicação e OWASP (auditoria e codificação segura)

**Fase:** 2 — Segurança  
**Labels:** security, owasp, devsecops

## Descrição

Implementar processo de auditoria e codificação segura alinhado ao OWASP Top 10. CyberSec, Architect, Developer, DevOps e QA devem aplicar checklists e relatório de auditoria (Critical/High/Medium/Low).

## Critérios de aceite

- [ ] Processo de auditoria documentado: escopo, checklist OWASP (acesso, criptografia, injeção, XSS, configuração, headers, validação de entrada, auth, segredos, dependências, arquivos sensíveis).
- [ ] Formato de relatório de auditoria (severidade, item, recomendação).
- [ ] Headers de segurança, validação de entrada, autenticação/sessão, segredos e dependências cobertos nos checklists.
- [ ] **Análise estática em git hooks:** ferramenta (ex.: SonarQube) acoplada aos git hooks; falha em regras de segurança (segredos, padrões conhecidos) → **rejeição do commit** na hora. CyberSec (LLM) focado em **auditoria de fluxo lógico** (lógica de negócio, etapas), não substituindo a análise estática.
- [ ] Matriz por agente: CyberSec (auditoria de fluxo), Architect/Developer (codificação segura), DevOps (infra), QA (testes de segurança).
- [ ] Integração com pipeline (ex.: bloqueio de merge se Critical/High em aberto).

## Referências

- [15-seguranca-aplicacao-owasp.md](../15-seguranca-aplicacao-owasp.md)
