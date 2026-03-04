# Segurança de aplicação e OWASP: habilidades dos agentes

Os agentes do enxame (em especial **CyberSec**, **Developer** e **Architect**) devem possuir **habilidades de auditoria de segurança e codificação segura** alinhadas ao **OWASP Top 10** e às boas práticas de aplicação. Este documento integra a **prioridade de cibersegurança** do projeto ([05-seguranca-e-etica.md](05-seguranca-e-etica.md)): vulnerabilidades de aplicação (injeção, quebra de controle de acesso, falhas criptográficas, etc.) são tratadas como **prioridade não negociável**. Consolida o processo de auditoria, checklists e padrões que o time aplica em *code review*, implementação e merge. Complementa a postura **Zero Trust** e a validação em runtime em [05-seguranca-e-etica.md](05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md). Detecção de segredos e padrões de sintaxe é feita por **ferramentas determinísticas** (ex.: SonarQube em git hooks), não por LLM — alinhado a **baixíssimo custo** e alta performance.

**Origem:** Padrões inspirados em *Security Auditor* (buildwithclaude / Dave Poon, MIT), adaptados ao enxame e ao fluxo de PRs (Architect + CyberSec).

---

## Papel: engenheiro de segurança de aplicação

O time atua como **engenheiro de segurança de aplicação** especializado em:

- Práticas de codificação segura e detecção de vulnerabilidades
- Conformidade com OWASP Top 10
- Revisão de autenticação, autorização, criptografia e validação de entrada
- Relatórios de auditoria acionáveis (Critical / High / Medium / Low)

---

## Processo de auditoria de segurança

1. **Realizar auditoria** de código e arquitetura (endpoints, auth, dados sensíveis, dependências).
2. **Identificar vulnerabilidades** usando o framework OWASP Top 10.
3. **Projetar/validar** fluxos de autenticação e autorização.
4. **Garantir** validação de entrada e mecanismos de criptografia onde aplicável.
5. **Propor** testes de segurança e estratégias de monitoramento.

---

## Princípios de segurança de aplicação

- **Defesa em profundidade:** Múltiplas camadas de segurança (runtime + código + rede; ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md)).
- **Menor privilégio:** Controles de acesso restritos ao necessário.
- **Nunca confiar em entrada do usuário:** Validar e sanitizar rigorosamente.
- **Falhar de forma segura:** Sem vazamento de informação em erros.
- **Dependências:** Varredura e atualização regular (`npm audit`, Snyk/Trivy).
- **Correções práticas:** Priorizar riscos reais e mitigáveis.

---

## OWASP Top 10 — Checklist e exemplos

### A01:2021 — Controle de acesso quebrado

- [ ] Todo endpoint verifica autenticação.
- [ ] Todo acesso a dados verifica autorização (propriedade ou role).
- [ ] CORS configurado com origens específicas (não `*` em produção).
- [ ] Listagem de diretório desabilitada.
- [ ] Rate limiting em endpoints sensíveis.
- [ ] JWT validado em toda requisição.

**Exemplo (evitar):** Endpoint DELETE sem checagem de ownership ou role. **Correto:** Middleware de autenticação + verificação de que o recurso pertence ao usuário ou que o usuário tem role admin.

### A02:2021 — Falhas criptográficas

- [ ] Senhas com hash (bcrypt 12+ rounds ou argon2).
- [ ] Dados sensíveis criptografados em repouso (AES-256) quando aplicável.
- [ ] TLS/HTTPS em todas as conexões.
- [ ] Nenhum segredo em código-fonte ou logs.
- [ ] Chaves de API rotacionadas; campos sensíveis excluídos das respostas da API.

**Exemplo (evitar):** Armazenar senha em texto plano. **Correto:** `bcrypt.hash(senha, 12)` ou equivalente antes de persistir.

### A03:2021 — Injeção (SQL, comando, etc.)

- [ ] Todas as queries usam statements parametrizados ou ORM.
- [ ] Nenhuma concatenação de string em queries.
- [ ] Execução de comandos OS com array de argumentos, não string de shell.
- [ ] Entrada do usuário nunca em `eval()`, `Function()` ou template literais para código.

**Exemplo (evitar):** `query = "SELECT * FROM users WHERE email = '" + email + "'"`. **Correto:** ORM ou prepared statements (`$1`, `?`).

### A07:2021 — XSS (Cross-Site Scripting)

- [ ] Preferir escape automático (ex.: React); evitar `dangerouslySetInnerHTML` com entrada do usuário.
- [ ] Se precisar de HTML, sanitizar (ex.: DOMPurify).
- [ ] Headers CSP configurados; cookies de sessão HttpOnly.

### A05:2021 — Configuração insegura

- [ ] Credenciais padrão alteradas.
- [ ] Mensagens de erro em produção sem stack trace.
- [ ] Métodos HTTP desnecessários desabilitados.
- [ ] Headers de segurança configurados (ver seção abaixo).
- [ ] Debug desligado em produção; dependências atualizadas (`npm audit`).

---

## Headers de segurança (exemplo)

Configurar no servidor/Next.js (ou equivalente): HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, **Content-Security-Policy (CSP)**. Exemplo de CSP: `default-src 'self'`, `script-src`/`style-src` restritos, `connect-src` apenas origens conhecidas, `frame-ancestors 'none'`, `form-action 'self'`. Em produção, evitar `'unsafe-inline'`/`'unsafe-eval'` onde possível.

---

## Validação de entrada

- **APIs e Server Actions:** Usar schema (ex.: Zod) para validar corpo, query e parâmetros; rejeitar com erro estruturado quando inválido.
- **Upload de arquivos:** Validar tipo MIME, tamanho máximo e, quando possível, magic bytes (não confiar só na extensão).

---

## Autenticação e sessão

- **JWT:** Segredo mínimo 256 bits; tokens de curta duração (ex.: 15 min); validar `audience` e `issuer`; algoritmo explícito (ex.: HS256).
- **Cookies de sessão:** `httpOnly`, `secure`, `sameSite` (ex.: `lax`) para mitigar roubo e CSRF.
- **Rate limiting:** Aplicar em login e endpoints sensíveis (ex.: sliding window por IP).

---

## Ambiente e segredos

- Nunca commitar `.env`; usar `.env.example` com placeholders.
- Segredos distintos por ambiente; rotação periódica; em produção preferir gerenciador de segredos (Vault, AWS SSM, Doppler).
- Nunca logar ou incluir segredos em respostas de erro.

---

## Dependências

- Executar `npm audit` / `npm audit fix` e, quando disponível, ferramentas como Snyk/Trivy no pipeline (CyberSec/DevOps).
- Manter dependências atualizadas; o CyberSec bloqueia merge com CVE conhecida (ver [02-agentes.md](02-agentes.md)).

---

## Formato de relatório de auditoria

Ao conduzir revisão de segurança, registrar achados no formato:

```text
## Relatório de auditoria de segurança

### Crítico (corrigir antes do merge)
1. **[A03:Injeção]** SQL injection em `/api/search` — entrada concatenada na query
   - Arquivo: `app/api/search/route.ts:15`
   - Correção: Usar query parametrizada
   - Risco: Comprometimento do banco

### Alto (corrigir em seguida)
1. **[A01:Controle de acesso]** Falta checagem de auth no endpoint DELETE
   - Arquivo: `app/api/posts/[id]/route.ts:42`
   - Correção: Adicionar middleware de autenticação e verificação de ownership

### Médio (recomendado)
1. **[A05:Configuração]** Headers de segurança ausentes
   - Correção: Adicionar CSP, HSTS, X-Frame-Options

### Baixo (considerar)
1. **[A06:Componentes vulneráveis]** N pacotes com vulnerabilidades conhecidas
   - Ação: Executar `npm audit fix`
```

---

## Arquivos sensíveis (revisão cuidadosa)

Antes de modificar, o time deve revisar com cuidado:

- `.env*` — segredos de ambiente
- `auth.ts` / `auth.config.ts` — configuração de autenticação
- `middleware.ts` — proteção de rotas
- `**/api/auth/**` — endpoints de auth
- `prisma/schema.prisma` (ou equivalente) — permissões, RLS
- `next.config.*` — headers de segurança, redirects
- `package.json` / `package-lock.json` — mudanças de dependências

---

## Quem aplica o quê

| Agente     | Auditoria OWASP / codificação segura |
|-----------|--------------------------------------|
| **CyberSec**  | Revisão completa; relatório de auditoria; bloqueio de PR com vulnerabilidades; validação de dependências e segredos. |
| **Architect** | Revisão de padrões (acesso, validação, estrutura); Fitness Functions que checam licenças e segurança. |
| **Developer** | Implementar com validação de entrada, auth/autorização, sem injeção; não commitar segredos; seguir correções do CyberSec/Architect. |
| **DevOps**    | Headers de segurança em proxy/gateway; scan de dependências no CI; segredos em gerenciador. |
| **QA**        | Casos de teste para inputs malformados e bordas de autorização. |
| **DBA**       | Revisão da camada de dados (queries, schema, migrations); validação de queries/schema; prevenção de injeção SQL e desperdício de recursos; bloqueio de PR com risco de performance ou violação de normas de banco. |

---

## Integração com pipeline: git hooks e análise estática

**Análise estática na borda:** Acoplar uma ferramenta de análise estática (ex.: **SonarQube**) aos **git hooks**. Regras de segurança (ex.: segredos no código, padrões conhecidos de vulnerabilidade) são verificadas **antes** do commit; se falhar, o **git hook rejeita o commit** na hora. Não usar LLM/GPU para detecção de sintaxe ou segredos — a análise estática faz isso em milissegundos. O CyberSec (LLM) complementa com **auditoria de fluxo lógico** (lógica de negócio, ordem de etapas, riscos que exigem interpretação), não substituindo a análise estática. Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md) (seção 1.4).

**Script de referência (Fase 2 — 022):** [scripts/owasp-pre-commit.sh](../scripts/owasp-pre-commit.sh) — verifica staged files em busca de padrões de segredo (redis URL, AWS key, api_key/secret/password); opcionalmente executa **gitleaks** se instalado. Uso: `ln -sf ../../scripts/owasp-pre-commit.sh .git/hooks/pre-commit` ou via framework [pre-commit](https://pre-commit.com/).

**Bloqueio de merge:** Em pipeline de CI, **bloquear merge** (ou falhar o stage) quando o relatório de auditoria ou a análise estática indicar achados **Critical** ou **High** em aberto. Regra: nenhum PR com vulnerabilidade Critical/High não remediada pode ser merged; o CyberSec e o Architect aplicam os checklists antes do approve.

---

## Relação com outros documentos

- **[05-seguranca-e-etica.md](05-seguranca-e-etica.md):** Zero Trust, credenciais, URLs, skills de terceiros, egress filtering, rotação de tokens; sandbox air-gap e proxy para Developer; análise estática em git hooks.
- **[14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md):** Validação pré-execução (comandos, URLs, paths, conteúdo); proteção em runtime.
- **[02-agentes.md](02-agentes.md):** Definição do CyberSec, Developer, Architect e DBA; código de conduta e bloqueio de PRs inseguros.

Integrar este checklist aos system prompts e ao fluxo de *code review* (Architect + CyberSec + DBA quando houver alterações na camada de dados) garante que o time de desenvolvimento possua as habilidades de auditoria e codificação segura de forma consistente.
