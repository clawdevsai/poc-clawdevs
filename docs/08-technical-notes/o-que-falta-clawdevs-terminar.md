# O que falta para o ClawDevs terminar

**Objetivo:** Validar, com base na documentação e nas validações existentes, o que já está pronto e o que ainda falta para o ecossistema ClawDevs ser considerado “terminado” (conforme visão do projeto).

**Sobre o vídeo Intro-clawdevs.mp4:** Ferramentas de leitura disponíveis não transcrevem vídeo (MP4). Para converter o conteúdo em texto é preciso usar um transcritor externo (ex.: Whisper local, serviço de transcrição). Este documento foi gerado a partir dos **docs e do backlog** do repositório.

---

## 1. Visão de “terminado”

Pela documentação, o ClawDevs está “terminado” quando:

- **Qualquer um pode ter seu ClawDevs** na própria máquina (replicável com máquina de referência).
- **Fase 0** (fundação): CEO via Telegram + Ollama no K8s, cluster estável.
- **Fase 1** (agentes): 9 agentes definidos, SOUL, pods/config, fluxo evento-driven e line-up documentados.
- **Fase 2** (segurança): Zero Trust, quarentena, OWASP/CISO, kill switch, phase2-config aplicada.
- **Operação autônoma nível 4**: recuperação automática, digest, five strikes, freio de mão quando necessário.
- **Custo zero no núcleo**, open source, alta performance (65% hardware, FinOps).

---

## 2. O que já está pronto (validado nos docs)

| Área | Status | Onde |
|------|--------|------|
| **Fase 0** | Validada | [validacao-fase0-001-003-008.md](issues/validacao-fase0-001-003-008.md): máquina de referência, Minikube/Redis/Ollama 65%, imagem gateway enxuta. |
| **Fase 1** | Fechada no repo | [validacao-fase1-completa.md](issues/validacao-fase1-completa.md): 010–019 com entregáveis em código e docs (agentes, SOUL, pods, fluxo Redis, line-up, E2E 2FA, autonomia nível 4 doc). |
| **Fase 2** | Implementada no repo | [validacao-fase2-completa.md](issues/validacao-fase2-completa.md): 020–029, 126, 128 (Zero Trust, phase2-config, quarentena, token bucket, etc.). |
| **K8s** | Estrutura pronta | `make up`, `make configmaps-pipeline`, `make security-apply`, `make orchestrator-apply`; Redis, Ollama, OpenClaw, development-team, security, orchestrator. |
| **Scripts e integração** | Parcial | Truncamento na borda, pre-flight Summarize, TTL working buffer, microADR, validate_reverse_po, finops_attempt_cost, gateway adapter com `/publish-to-cloud`. |

---

## 3. O que ainda falta (por fase e tema)

### 3.1 Fase 0 / Fundação (001–009, 124, 125)

| Item | O que falta |
|------|-------------|
| **124 – Contingência cluster acéfalo** | Validar em ambiente: heartbeat, branch efêmera, retomada automática (3 ciclos estáveis, checkout limpo + Architect), notificação ao Diretor. |
| **125 – Pipeline explícito e slot único** | Garantir que o pipeline de revisão (GPU Lock, slot único code:ready) está de fato em uso nos triggers e documentado no runbook. |
| **009 – Transcrição áudio** | Script/tool m4a → .md referenciado no setup; verificar se está no `scripts/` e no 09-setup-e-scripts. |

### 3.2 Fase 1 – Evoluções operacionais

| Item | O que falta |
|------|-------------|
| **Pods por agente (014)** | Architect, QA, CyberSec, DBA com `replicas: 0`; ativar quando for usar pipeline completo com um pod por agente. |
| **017 no orquestrador** | Five strikes, orçamento de degradação, digest diário: script de referência existe; integrar de fato no CronJob/consumer do orchestrator. |
| **Publicação Redis pelo gateway** | Gateway-redis-adapter (POST /publish → XADD) opcional; usar se o OpenClaw não publicar direto no Redis. |
| **OpenCode no Developer** | Build opcional; integrar OpenCode na imagem do pod Developer quando for prioridade. |
| **019 – Teste manual nuvem** | Validar management-team com provedor em nuvem (secret + llm-providers) no seu ambiente; checklist em validacao-fase1-019.md. |

### 3.3 Fase 2 – Integração e validação em runtime

| Item | O que falta |
|------|-------------|
| **Adapter com Fase 2** | Rodar `make gateway-redis-adapter-configmap` e garantir que o deployment usa phase2-config (DEGRADATION_THRESHOLD_PCT, five strikes, etc.). |
| **Aplicar Fase 2 no cluster** | `make phase2-apply` (ou `make up` já aplica k8s/security/); validar egress-whitelist, token rotation, url-sandbox, quarentena conforme docs. |
| **028 – Sandbox seccomp/eBPF** | Restrições de kernel no sandbox efêmero (bloqueio execve/socket na instalação de deps); ver se há manifest ou doc de implementação. |

### 3.4 Fase 3 – Operações (030–039, 127)

| Item | O que falta |
|------|-------------|
| **030 – Manual primeiros socorros GPU** | Completar checklist: Fase 1 diagnóstico, Fase 2 reset cirúrgico, Fase 3 reset driver; documentar que recuperação padrão é automática. |
| **032–036** | Five strikes (032), aprovação por omissão cosmética (033), loop de consenso pré-freio (034), QA auditor dívida técnica (035), digest e alertas (036): implementação operacional no orquestrador (CronJobs, consumers). |
| **127 – Disjuntor draft_rejected** | 3 draft_rejected consecutivos → congelar tarefa; RAG health check; descongelar com rejeição + contexto saneado. |

### 3.5 Fase 4 – Configuração (040–041, FinOps)

| Item | O que falta |
|------|-------------|
| **Max tokens no OpenClaw** | finops-config existe; aplicar limite no código do OpenClaw (ou sempre passar pelo adapter com `/publish-to-cloud`). |
| **Pre-flight Summarize** | Orquestrador/gateway **invocar** preflight_summarize.py para payloads com >N interações antes de enviar à nuvem. |
| **Validação reversa PO** | Garantir que o pipeline que gera resumo chama validate_reverse_po.py e rejeita truncamento se critérios forem omitidos. |
| **Freio $5/dia e token bucket** | Já na Fase 2 (126); validar em runtime. |

### 3.6 Fases 5–11 (Self-improvement, ferramentas, integrações, avançado)

- **Fase 5 (050–059):** Memória Elite, WAL, .learnings/, microADRs no Warm Store — docs existem; integração explícita com Warm Store e rotinas no cluster.
- **Fase 6–8:** Habilidades transversais, ferramentas (browser, summarize, gh, OpenCode), skills e ambiente — várias issues com doc; implementação por prioridade.
- **Fase 9–10:** API Gateway (Maton), dados/watchlist, Exa, busca web, frontend/UX — integrações e melhorias contínuas.
- **Fase 11:** War Room, Chaos Engineering, balanceamento avançado — avançado; depois do núcleo estável.

---

## 4. Checklist prático “ClawDevs terminado (núcleo)”

Use isto como lista de verificação mínima para considerar o núcleo “terminado”:

- [ ] **Fase 0:** `make prepare && make up` sobe cluster; CEO responde no Telegram com Ollama no K8s; Redis e Ollama estáveis.
- [ ] **Fase 1:** Todos os agentes têm SOUL e config; fluxo evento-driven (Redis) documentado e testado; line-up e 019 validados (ao menos em doc).
- [ ] **Fase 2:** `make security-apply` e phase2-config aplicados; adapter com Fase 2 se usado; egress, quarentena e token bucket configurados.
- [ ] **Orquestrador:** ConfigMaps do orchestrator aplicados; digest/alertas e (se possível) five strikes / freio de mão integrados.
- [ ] **Documentação:** 09-setup-e-scripts reflete o setup real; manual de primeiros socorros GPU (030) completo; INDEX e README atualizados.
- [ ] **Replicabilidade:** Outra pessoa com máquina de referência consegue seguir os docs e ter o CEO no Telegram + pipeline básico.

---

## 5. Resumo

- **Já está “pronto no papel”:** Fase 0, Fase 1 e Fase 2 estão implementadas e validadas no repositório (docs + código + K8s).
- **Já implementado no repo (núcleo do plano):** 017 no orquestrador (deployment-autonomy, deployment-disjuntor, CronJobs digest/cosmetic, configmap com orchestrator_autonomy, strikes, disjuntor, rag_health_check); 124 (deployment-acefalo-monitor, deployment-acefalo-heartbeat); 125 (runbook em 06-operacoes.md); 009 (m4a_to_md.sh + app/features/m4a_to_md.py + ref em 09-setup); 030 (first-aid-gpu.sh --phase 1|2|3 + doc); validação reversa PO (script path corrigido); adapter com security-config (Fase 2); 028 (k8s/sandbox/ já existente).
- **Falta sobretudo:** (1) **validação em ambiente real** (124, 019, phase2, orquestrador no cluster); (2) **pre-flight e validação reversa** efetivamente chamados pelo pipeline que gera resumo (adapter já faz pre-flight em /publish-to-cloud); (3) **Fases 5–11** conforme prioridade do PO (Memória Elite no cluster, ferramentas, skills, integrações, War Room).

Para **transcrever o Intro-clawdevs.mp4** e alinhar o vídeo a esta lista: usar ferramenta de transcrição (ex.: Whisper) e depois mapear cada tópico do vídeo para as issues e aos itens acima.

---

## 6. Ainda falta desenvolver (resumo objetivo)

| Tipo | O que fazer |
|------|-------------|
| **Validação (não é código novo)** | Rodar `make up`, `make orchestrator-configmap`, `make configmap-acefalo`, aplicar k8s/orchestrator; testar CEO no Telegram, contingência 124, digest, five strikes em ambiente real. |
| **Ativação opcional** | Pods por agente (014): mudar `replicas: 0` para `1` nos deployments Architect, QA, CyberSec, DBA se quiser um pod por agente. Gateway-redis-adapter: `replicas: 1` se OpenClaw não publicar direto no Redis. |
| **Integração no pipeline** | Garantir que o passo que **gera resumo** (compactação/truncamento) chama `validate_reverse_po_after_summary.sh` antes de aplicar; que chamadas à nuvem passem pelo adapter `/publish-to-cloud` (pre-flight + max tokens). |
| **OpenCode no Developer** | Integrar OpenCode na imagem do pod Developer (Dockerfile) quando for prioridade. |
| **Fase 5** | Jobs/cron no cluster que promovem .learnings/ para SOUL/AGENTS, microADRs no Warm Store (docs existem). |
| **Fases 6–11** | Habilidades transversais, ferramentas (browser, summarize, gh, OpenCode Controller), skills, API Gateway (Maton), Exa, frontend/UX, War Room, Chaos Engineering — conforme backlog e prioridade do PO. |
