# Habilidades CISO (Chief Information Security Officer)

Este documento consolida as **habilidades de nível CISO** que os agentes do enxame devem aplicar quando atuam em segurança da informação, conformidade, resposta a incidentes e avaliação de fornecedores. Integra a **prioridade de cibersegurança** do projeto ([05-seguranca-e-etica.md](05-seguranca-e-etica.md)): resistência a ataques e governança de risco são não negociáveis, em alinhamento com custo baixíssimo e alta performance. O **Agente CyberSec** é o principal detentor dessas capacidades; **DevOps/SRE** e **Architect** utilizam checklists de infraestrutura e aplicação conforme seu escopo; **CEO** e **PO** podem referenciar critérios de conformidade e fornecedores para decisões estratégicas.

**Referência de origem:** Skill CISO 1.0.0 (auditoria de infraestrutura, triagem de vulnerabilidades, conformidade SOC 2/GDPR/ISO/HIPAA, avaliação de fornecedores, resposta a incidentes, monitoramento de ameaças, gestão de segredos), integrado à documentação do time de agentes ([02-agentes.md](02-agentes.md), [05-seguranca-e-etica.md](05-seguranca-e-etica.md), [15-seguranca-aplicacao-owasp.md](15-seguranca-aplicacao-owasp.md)).

---

## Quando usar

O agente atua como **CISO virtual** quando o contexto exige: orientação em segurança da informação, operações de segurança, gestão de risco, conformidade regulatória ou resposta a incidentes. As decisões que exigem **humano no loop** (escolha de fornecedor de segurança, priorização de framework de conformidade, divulgação de incidente, exceções de política) devem ser escaladas ao Diretor.

---

## Referência rápida

| Domínio | Conteúdo neste documento |
|--------|---------------------------|
| Auditoria de infraestrutura | Checklists cloud (AWS/GCP), Docker/K8s, aplicação; **varredura local OpenClaw** (config, rede, credenciais, hardening SO, guardrails); modelo de relatório |
| Conformidade | SOC 2, GDPR, ISO 27001, HIPAA — evidências e checklists |
| Resposta a incidentes | Classificação, fases, playbooks (vazamento de credenciais, ransomware, phishing, vazamento de dados), templates |
| Avaliação de fornecedores | Tiers de risco, questionário, revisão de SOC 2, DPA, registro de risco, checklist de desligamento |

---

## Capacidades centrais

1. **Auditar infraestrutura** — Revisar configs de nuvem (AWS/GCP/Hetzner), Docker/K8s, regras de firewall, SSL/TLS.
2. **Triar vulnerabilidades** — Filtrar ruído de CVE, cruzar com ativos reais, priorizar por impacto real.
3. **Acompanhar conformidade** — Coleta de evidências SOC 2, mapeamento de dados GDPR, cronograma de revisão de políticas.
4. **Avaliar fornecedores** — Analisar questionários de segurança, revisar relatórios SOC 2 de terceiros, sinalizar riscos.
5. **Responder a incidentes** — Executar runbooks, coordenar contenção, redigir pós-mortem.
6. **Monitorar ameaças** — Menções em dark web, vazamentos de credenciais, expiração de certificados, sequestro de DNS.
7. **Gerenciar segredos** — Cronograma de rotação, configuração de vault, resposta a credenciais vazadas.

---

## Checklist de decisão (antes de recomendar postura de segurança)

- [ ] Estágio da empresa? (startup, crescimento, enterprise)
- [ ] Stack tecnológico? (provedor de nuvem, linguagens, frameworks)
- [ ] Requisitos de conformidade? (SOC 2, HIPAA, PCI-DSS, GDPR/LGPD)
- [ ] Tamanho do time? (impacta complexidade de gestão de acesso)
- [ ] Maturidade de segurança atual? (nenhuma, básica, madura)

---

## Regras críticas

- **Priorizar com rigor** — Startups não podem fazer tudo; regra 80/20.
- **Saída acionável** — "Altere a linha 47 de X para Y" vale mais que "SQL injection detectada".
- **Rastrear dívida de segurança** — Documentar o que foi deixado para depois.
- **Nada de teatro de segurança** — Checkboxes sem proteção real desperdiçam tempo.
- **Assumir brecha** — Logging, backups e planos de resposta são inegociáveis.
- **Segredos nunca no chat** — O agente nunca deve expor credenciais, mesmo ao ajudar a rotacioná-las.

---

## Foco por estágio da empresa

| Estágio | Foco CISO |
|--------|-----------|
| **Pre-seed/Seed** | MFA em todo lugar, gestão de segredos, controle de acesso básico, sem buckets públicos |
| **Series A** | Plano de resposta a incidentes, preparação SOC 2, processo de avaliação de fornecedores, treinamento de segurança |
| **Series B+** | Contratação dedicada de segurança, testes de penetração, bug bounty, automação de conformidade |

---

## Humano no loop

Estas decisões exigem julgamento humano (Diretor):

- Escolha de fornecedor de segurança principal
- Priorização de framework de conformidade
- Decisões de divulgação de incidente
- Alocação de orçamento de segurança
- Exceções de política de acesso
- Aceitação de risco de terceiros

---

## 1. Auditoria de infraestrutura

### 1.1 Cloud — AWS

**IAM**
- [ ] Conta root com MFA habilitado
- [ ] Conta root sem access keys
- [ ] Usuários IAM com MFA
- [ ] Sem políticas inline (usar managed policies)
- [ ] Política de senha com complexidade
- [ ] Credenciais não usadas removidas (90+ dias)
- [ ] Acesso cross-account revisado

**S3**
- [ ] Sem buckets públicos (salvo intencional)
- [ ] Bucket policies revisadas
- [ ] Criptografia em repouso habilitada
- [ ] Versionamento para dados críticos
- [ ] Access logging habilitado
- [ ] Block public access ativado

**Rede**
- [ ] Security groups com least privilege
- [ ] Sem 0.0.0.0/0 em SSH/RDP
- [ ] VPC flow logs habilitados
- [ ] VPC default não usada em produção
- [ ] NACLs revisadas

**Compute**
- [ ] EC2 com IAM roles, não keys
- [ ] IMDSv2 obrigatório (sem IMDSv1)
- [ ] Volumes EBS criptografados
- [ ] Patch management em vigor

**Monitoramento**
- [ ] CloudTrail habilitado (todas as regiões)
- [ ] Logs CloudTrail em S3 + CloudWatch
- [ ] GuardDuty habilitado
- [ ] Config rules ativas

### 1.2 Cloud — GCP

**IAM**
- [ ] Políticas em nível de organização
- [ ] Sem roles primitivos (Owner/Editor) em produção
- [ ] Service accounts com least privilege
- [ ] Sem chaves de service account gerenciadas por usuário
- [ ] Domain-restricted sharing habilitado

**Storage**
- [ ] Sem buckets públicos
- [ ] Uniform bucket-level access
- [ ] Criptografia com CMEK quando exigido

**Rede**
- [ ] Regras de firewall revisadas
- [ ] VPC flow logs
- [ ] Private Google Access
- [ ] Cloud NAT para egress

### 1.3 Docker / Kubernetes

**Imagens**
- [ ] Base de registries confiáveis
- [ ] Sem tag `latest` em produção
- [ ] Varredura de vulnerabilidades no CI/CD
- [ ] Imagens assinadas

**Runtime**
- [ ] Containers não rodam como root
- [ ] Root filesystem read-only
- [ ] Resource limits definidos
- [ ] Sem modo privileged
- [ ] Security contexts definidos

**Kubernetes**
- [ ] RBAC habilitado e revisado
- [ ] Network policies em vigor
- [ ] Pod security standards aplicados
- [ ] Secrets criptografados em repouso
- [ ] Audit logging habilitado
- [ ] Workloads fora do namespace default

### 1.4 Aplicação

**Autenticação**
- [ ] Política de senha forte
- [ ] MFA disponível e incentivado
- [ ] Timeout de sessão configurado
- [ ] Fluxo seguro de reset de senha
- [ ] Bloqueio após tentativas falhas
- [ ] OAuth/OIDC configurado corretamente

**Autorização**
- [ ] RBAC implementado
- [ ] Least privilege
- [ ] Proteção contra IDOR
- [ ] Autorização em todos os endpoints

**Proteção de dados**
- [ ] Criptografia em trânsito (TLS 1.2+)
- [ ] Criptografia em repouso para dados sensíveis
- [ ] Tratamento de PII documentado
- [ ] Políticas de retenção definidas
- [ ] Criptografia de backup verificada

**Validação de entrada**
- [ ] Proteção contra SQL injection (queries parametrizadas)
- [ ] Proteção contra XSS (encoding de saída)
- [ ] Tokens CSRF
- [ ] Validação de upload de arquivos
- [ ] Rate limiting

### 1.5 Varredura local do ambiente OpenClaw

Os agentes (em especial **CyberSec** e **DevOps**) devem poder **executar ou recomendar** uma varredura de segurança **local** do ambiente onde o OpenClaw está instalado. A avaliação é **somente leitura por padrão**; correções exigem flag explícita e confirmação. Nenhum dado sai da máquina; nenhuma chamada de rede.

**Filosofia:** (1) **Local apenas** — zero telemetria, zero envio externo; (2) **Somente leitura por padrão** — alterações só com confirmação explícita; (3) **Operado pelo dono** — pensado para o dono do OpenClaw rodar na própria máquina.

**Categorias verificadas:**

| Categoria | Verificações | Severidade |
|-----------|--------------|------------|
| **Configuração OpenClaw** | Bind do gateway (evitar 0.0.0.0), força do token, permissões do config, modo de exec segura, exposição do browser, permissões de ferramentas | CRÍTICO–INFO |
| **Exposição de rede** | Portas públicas, firewall, SSH, exposição WAN | CRÍTICO–INFO |
| **Higiene de credenciais** | Chaves em texto puro, permissões de secrets, .gitignore, dados sensíveis em arquivos de memória | CRÍTICO–WARNING |
| **Hardening do SO** | Criptografia de disco, atualizações automáticas, versão do SO, uso de admin | HIGH–INFO |
| **Guardrails de agentes** | Existência de RULES.md, permissões de memória, controles de mensagens externas, exec elevada | HIGH–INFO |

**Saída:** níveis CRÍTICO (ação imediata), WARNING (corrigir), PASS (ok), INFO (contexto); pontuação final 0–100. Com flag de correção, o scanner pode sugerir ou aplicar correções seguras (ex.: restringir permissões de arquivo, adicionar entradas ao .gitignore), sempre com confirmação antes de cada mudança.

**Script de varredura local (Fase 2 — 023):** [scripts/ciso_local_scan.sh](../scripts/ciso_local_scan.sh) — executa checagens somente leitura (`.env` versionado, `.gitignore`, permissões de arquivos sensíveis) e emite relatório no formato acima. Uso: `./scripts/ciso_local_scan.sh` (sem alterar nada); opcional `--fix` para aplicar correções com confirmação.

### 1.6 Modelo de relatório de auditoria

```
RELATÓRIO DE AUDITORIA DE SEGURANÇA
Data: [Data]
Escopo: [O que foi auditado]
Auditor: [Nome/Agente]

RESUMO EXECUTIVO
- Achados críticos: X
- Altos: X
- Médios: X
- Baixos: X

ACHADOS CRÍTICOS
1. [Achado]
   - Risco: [Descrição do impacto]
   - Remediação: [Correção específica]
   - Prioridade: Imediata

ACHADOS ALTOS
[Mesmo formato]

RECOMENDAÇÕES
1. [Ações curto prazo]
2. [Melhorias médio prazo]
3. [Roadmap de segurança longo prazo]

ANEXO
- Ferramentas utilizadas
- Resultados completos de varredura
- Evidências (screenshots)
```

---

## 2. Conformidade

### 2.1 SOC 2

**Trust Service Criteria**

| Categoria | Foco |
|----------|------|
| **Security** | Proteção contra acesso não autorizado |
| **Availability** | Disponibilidade do sistema |
| **Processing Integrity** | Processamento completo e preciso |
| **Confidentiality** | Informação confidencial protegida |
| **Privacy** | Tratamento de dados pessoais |

**Type I vs Type II**

| Tipo | Cobertura | Prazo |
|------|-----------|-------|
| **Type I** | Desenho dos controles em um ponto no tempo | Snapshot |
| **Type II** | Efetividade dos controles ao longo do tempo | 6–12 meses |

**Checklist de evidências (Security)**
- [ ] Política de controle de acesso
- [ ] Registros de provisionamento/desprovisionamento
- [ ] Evidência de MFA
- [ ] Configuração de firewall
- [ ] Configuração de criptografia
- [ ] Resultados de pentest
- [ ] Relatórios de varredura de vulnerabilidades

**Gaps comuns SOC 2**

| Gap | Correção |
|-----|----------|
| Sem política formal de segurança | Redigir e aprovar documento de política |
| Revisões de acesso ausentes | Implementar revisões trimestrais |
| Sem background check | Incluir no processo de contratação |
| Offboarding incompleto | Checklist de offboarding com TI |
| Sem pentest | Agendar pentest anual |
| Avaliação de fornecedores ausente | Criar questionário de segurança |

### 2.2 GDPR / LGPD

**Requisitos principais**

| Requisito | Implementação |
|-----------|----------------|
| Base legal | Documentar base legal para cada processamento |
| Minimização | Coletar só o necessário |
| Limitação de finalidade | Usar dados só para fins declarados |
| Limitação de armazenamento | Definir e aplicar retenção |
| Direito de acesso | Processo para o usuário solicitar seus dados |
| Direito de exclusão | Processo para solicitar exclusão |
| Portabilidade | Exportar dados em formato padrão |
| Notificação de brecha | Processo de notificação em 72h |

**Checklist GDPR/LGPD**
- [ ] Política de privacidade atualizada e acessível
- [ ] Mecanismo de consentimento (cookies)
- [ ] Registros de processamento mantidos
- [ ] DPA assinado com todos os processadores
- [ ] Processo de pedidos do titular
- [ ] Procedimento de resposta a brecha
- [ ] DPIA para processamento de alto risco
- [ ] DPO designado (quando exigido)

### 2.3 ISO 27001

Domínios centrais: políticas de segurança da informação, organização, segurança de recursos humanos, gestão de ativos, controle de acesso, criptografia, segurança física, operações, comunicações, aquisição de sistemas, fornecedores, gestão de incidentes, continuidade de negócios, conformidade. Documentar **Declaração de Aplicabilidade** (quais controles se aplicam e por que outros não).

### 2.4 HIPAA

Safeguards administrativos (avaliação de risco, treinamento, planejamento de contingência, BAAs), físicos e técnicos. Regras de PHI: acesso mínimo necessário, criptografia em repouso e trânsito, auditoria de acesso a PHI, BAA com fornecedores que tratam PHI, notificação de brecha (60 dias).

---

## 3. Resposta a incidentes

### 3.1 Classificação

| Severidade | Definição | Tempo de resposta |
|-----------|-----------|-------------------|
| **Crítica** | Brecha ativa, exfiltração de dados, serviço fora | Imediato |
| **Alta** | Comprometimento confirmado, exploração de vulnerabilidade | < 4h |
| **Média** | Atividade suspeita, possível exposição | < 24h |
| **Baixa** | Violação de política, evento menor | < 72h |

### 3.2 Fases

1. **Detecção e identificação** — Triagem inicial, preservação de evidências (screenshot do alerta, preservar logs antes de rotação, timeline, sistemas afetados).
2. **Contenção** — Curto prazo: isolar sistemas (não desligar), bloquear IPs/domínios maliciosos, desabilitar contas comprometidas, revogar credenciais expostas. Longo prazo: patch, monitoramento adicional, segmentação.
3. **Erradicação** — Remover malware/backdoors, fechar vetor, rotacionar credenciais possivelmente comprometidas, aplicar patches, verificar ausência de persistência.
4. **Recuperação** — Restaurar de backups íntegros, reconstruir sistemas, validar integridade, restauração gradual, monitoramento reforçado.
5. **Lições aprendidas** — O que aconteceu, o que funcionou, o que melhorar, action items com donos e prazos.

### 3.3 Playbooks resumidos

- **Vazamento de credenciais:** Escopo → rotacionar imediatamente → auditar acesso → notificar usuários afetados → buscar reutilização → remediar origem.
- **Ransomware:** Isolar → identificar variante → avaliar escopo → preservar evidências → restaurar de backup limpo → reportar se exigido → não pagar resgate.
- **Phishing comprometido:** Reset de credenciais → revisar regras de e-mail → revogar apps OAuth suspeitos → revisar e-mails enviados → verificar persistência → treinamento.
- **Vazamento de dados:** Escopo (quais dados, volume, sensibilidade) → notificação legal (72h GDPR, etc.) → notificação a clientes → monitoramento de crédito se aplicável → reporte regulatório → comunicação pública coordenada.

### 3.4 Template de log de incidente

```
ID: INC-[AAAA]-[###]
Status: Aberto / Contido / Resolvido

LINHA DO TEMPO
[Timestamp] - [Evento]

SISTEMAS AFETADOS
- Sistema 1
- Sistema 2

AÇÕES REALIZADAS
- [ ] Ação 1
- [ ] Ação 2

EVIDÊNCIAS
- [Link para logs preservados]
- [Link para screenshots]

RESPONSÁVEL: [Nome]
PRÓXIMOS PASSOS: [Descrição]
```

---

## 4. Avaliação de fornecedores

### 4.1 Tiers de risco

| Tier | Critério | Nível de avaliação |
|------|----------|--------------------|
| **Crítico** | Acesso a dados sensíveis, infraestrutura crítica | Avaliação completa + revisão anual |
| **Alto** | Acesso a sistemas internos, alguns dados sensíveis | Questionário + revisão SOC 2 |
| **Médio** | Acesso limitado, dados de negócio | Questionário |
| **Baixo** | Sem acesso a dados, serviço commodity | Due diligence básica |

### 4.2 Processo

1. **Triagem inicial** — Verificar registro da empresa, tempo no mercado, estabilidade financeira (se aplicável), histórico público de brechas, reputação.
2. **Questionário de segurança** — Infraestrutura (armazenamento, criptografia, cloud, patch, acesso a produção), controles de acesso (MFA, offboarding, background check), resposta a incidentes (plano documentado, prazo de notificação, incidentes nos últimos 3 anos), conformidade (certificações, último SOC 2, GDPR, DPA), continuidade (SLA, testes de backup, RTO/RPO).
3. **Revisão de documentação** — Revisar relatório SOC 2 (tipo I/II, período, critérios, exceções, opinião do auditor, CUECs, subservice organizations). Red flags: opinião qualificada, exceções significativas, controles ausentes para seu tipo de dado, relatório antigo (>1 ano).
4. **Monitoramento contínuo** — Revisão anual (SOC 2 atualizado, incidentes/mudanças, status de conformidade); monitoramento contínuo (ratings de segurança, alertas de brecha, cumprimento contratual).

### 4.3 Requisitos de DPA e cláusulas de segurança

DPA: finalidades de processamento claras, notificação de subprocessadores, direito de auditoria, exclusão de dados ao término, prazo de notificação de brecha, mecanismos de transferência. Cláusulas contratuais: manutenção de certificação (SOC 2 Type II / ISO 27001), notificação de incidentes em X horas, criptografia em repouso e trânsito, pentest anual, direito de auditoria com X dias de aviso, seguro de responsabilidade cibernética mínimo $X.

### 4.4 Checklist de desligamento de fornecedor

- [ ] Devolução/exclusão de dados confirmada por escrito
- [ ] Credenciais de acesso revogadas
- [ ] Integrações SSO/OAuth removidas
- [ ] Conexões DNS/rede removidas
- [ ] API keys rotacionadas
- [ ] Certificado de exclusão de dados obtido
- [ ] Término contratual documentado

---

## Relação com a documentação

- [02-agentes.md](02-agentes.md) — Definição do Agente CyberSec (CISO/DPO) e demais agentes; este doc detalha as habilidades CISO.
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Zero Trust, credenciais, skills de terceiros; o CISO aplica essas regras nas operações.
- [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) — Validação pré-execução; o CyberSec aplica em comandos, URLs e paths.
- [15-seguranca-aplicacao-owasp.md](15-seguranca-aplicacao-owasp.md) — Auditoria de aplicação e OWASP; complementa auditoria de infraestrutura e conformidade deste doc.
