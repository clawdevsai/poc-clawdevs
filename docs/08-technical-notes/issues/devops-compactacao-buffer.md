# Compactação segura de buffer (truncamento-finops)

Higiene de buffers Markdown preservando blocos `<!-- CRITERIOS_ACEITE -->` e `<!-- INVARIANTE_NEGOCIO -->`. O DevOps deve usar este fluxo na rotina de limpeza.

Ref: [041-truncamento-contexto-finops.md](041-truncamento-contexto-finops.md), [integracao-040-041-gateway-orquestrador.md](integracao-040-041-gateway-orquestrador.md).

---

## Uso manual

```bash
# Gerar arquivo compactado (revisar e depois substituir o original se desejado)
./scripts/devops_compact_safe.sh < /caminho/do/buffer.md > /caminho/do/buffer.md.compact
# Ou com Python direto:
python3 scripts/compact_preserve_protected.py < buffer.md > buffer.md.compact
```

---

## Agendamento (cron ou CronJob)

- **No host:** adicione ao crontab um job que rode o script sobre os paths de buffer (ex.: `docs/agents-devs/*.md` ou o diretório configurado para working buffer).
- **No cluster:** use um CronJob que monte o script (ConfigMap) e o volume com os buffers (PVC) e execute a compactação. Exemplo de comando dentro do pod:

  ```bash
  for f in /data/buffers/*.md; do
    [ -f "$f" ] && python3 /config/compact_preserve_protected.py < "$f" > "$f.compact" && mv "$f.compact" "$f"
  done
  ```

- **Exemplo de CronJob:** ver [k8s/development-team/devops-compact-cronjob-example.yaml](../../k8s/development-team/devops-compact-cronjob-example.yaml). É necessário criar o ConfigMap com o script (`make devops-compact-configmap`) e o PVC para os buffers antes de aplicar o CronJob.
