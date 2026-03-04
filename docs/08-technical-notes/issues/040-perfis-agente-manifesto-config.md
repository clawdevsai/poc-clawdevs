# [team-devs-ai] Perfis por agente (manifesto de configuração)

**Fase:** 4 — Configuração  
**Labels:** config, openclaw, prompts

**Implementação:** ConfigMap [k8s/security/agent-profiles-configmap.yaml](../../k8s/security/agent-profiles-configmap.yaml); doc canônico em [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md). Validação: [validacao-040-041-completa.md](validacao-040-041-completa.md).

## Descrição

Implementar o manifesto de configuração por agente: modelo, temperatura, skills, memory, constraints. CEO e PO (nuvem); Developer, Architect, DevOps, QA, CyberSec, UX (Ollama + limites de recurso).

## Critérios de aceite

- [ ] Perfil CEO: modelo nuvem (gpt-4o/gemini-1.5-pro), temperature 0.7, skills (web_search, telegram_notify, etc.), constraint (proibido código; freio $5/dia; **filtrar tarefas e visão** antes de enviar ao PO para não estourar orçamento de API).
- [ ] Perfil PO: modelo nuvem, temperature 0.3, skills (github_api_manager, kanban_sync), constraint (não alterar requisitos em In-Progress **exceto** sob evento **technical_blocker** do Architect; usar ciclo de rascunho **draft.2.issue** para Architect validar viabilidade antes da tarefa ir para desenvolvimento).
- [ ] Perfis locais: Developer (deepseek-coder, 4GB/4 threads, file_writer, gpu_lock, git_commit), Architect (llama3:8b, code_analyzer, adr_generator; avalia draft.2.issue, emite draft_rejected ou technical_blocker), DevOps (phi3:mini, **CPU-only** via node selectors, minikube_monitor, resource_scaler, gpu_temp_check, prioridade 65%, zero binários em skills), QA (llama3:8b, sandbox_executor, pytest_automation), CyberSec (llama3:8b, vulnerability_scanner, prompt_injection_filter), UX (**phi3:mini em CPU** via node selectors, temperature 0.6).
- [ ] Constraints por agente aplicadas (ex.: Architect recusa PR sem 80% cobertura; DevOps pausa se GPU > 82°C; DevOps/UX apenas CPU).

## Referências

- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md)
