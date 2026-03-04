# [team-devs-ai] Auto-atualização do ambiente (runtime e skills)

**Fase:** 8 — Skills e ambiente  
**Labels:** ops, devops, skills

## Descrição

Manter runtime do orquestrador e todas as skills instaladas atualizadas via cron em sessão isolada; resumo ao Diretor. Configuração e execução pelo DevOps; alinhado a Zero Trust e descoberta de skills.

## Critérios de aceite

- [ ] Cron (ou Job K8s agendado) que executa atualização do runtime OpenClaw e das skills instaladas em sessão isolada.
- [ ] Resumo das atualizações (o que foi atualizado, sucesso/falha) enviado ao Diretor (ex.: Telegram ou log).
- [ ] Configuração documentada (frequência, como desativar, onde ver logs).
- [ ] DevOps responsável por configurar e executar; nenhuma atualização automática de skills não aprovadas (apenas as já instaladas).

## Referências

- [21-auto-atualizacao-ambiente.md](../../07-operations/21-auto-atualizacao-ambiente.md)

## Verificação (Fase 8)

- CronJob K8s: [cronjob-auto-update-env.yaml](../../../k8s/orchestrator/cronjob-auto-update-env.yaml) (schedule 04:00 UTC); ConfigMaps [configmap-auto-update-env.yaml](../../../k8s/orchestrator/configmap-auto-update-env.yaml), [configmap-auto-update-scripts.yaml](../../../k8s/orchestrator/configmap-auto-update-scripts.yaml).
- Resumo: script emite resumo para stdout; Diretor consulta via `kubectl logs job/auto-update-env-<suffix>` ou integração ao digest.
- Configuração: doc [21-auto-atualizacao-ambiente.md](../../07-operations/21-auto-atualizacao-ambiente.md) (§ Customização, Desabilitar).
