# Investigação: repositório “baixado pelo CEO” não aparece em ~/clawdevs-shared/repos

## Contexto

O CEO (via Slack) informou ter baixado o repositório e analisado a documentação. No host, `~/clawdevs-shared/repos` estava vazio (`tree` → 0 directories, 0 files). Investigação para entender onde o clone iria parar e por que não aparece onde o Diretor espera.

## Conclusão rápida

1. **Workspace do CEO no pod:** `workspace` do agente CEO é **`/workspace/ceo`** (openclaw.json).
2. **Onde o `exec` roda:** Comandos `exec` (ex.: `git clone`) rodam com CWD = `/workspace/ceo`.
3. **Clone sem caminho:** `git clone https://github.com/clawdevs-ai/clawdevs` criaria **`/workspace/ceo/clawdevs`** (ou nome do repo), não em `/workspace/repos`.
4. **No host:** `/workspace` no pod = `~/clawdevs-shared` no host. Logo:
   - Se o CEO clonou de fato → repo estaria em **`~/clawdevs-shared/ceo/clawdevs`** (ou `ceo/<nome-do-repo>`).
   - A pasta **`~/clawdevs-shared/repos`** no host corresponde a **`/workspace/repos`** no pod; essa pasta **não é criada** pelo init e só existe se algum agente criar e clonar aí.

## O que verificar

1. **No host – repo no workspace do CEO:**
   ```bash
   ls -la ~/clawdevs-shared/ceo/
   # Se o CEO clonou, algo como: clawdevs/ ou clawdevsai-clawdevs/
   ```

2. **Mount ativo:** O `make shared` (minikube mount) precisa estar rodando para o pod ver o mesmo conteúdo que o host:
   ```bash
   grep -l "Successfully mounted" ~/minikube-mount.log 2>/dev/null && echo "Mount OK" || echo "Verificar make shared"
   ```

3. **Dentro do pod (opcional):**
   ```bash
   kubectl exec -n ai-agents deploy/openclaw -- ls -la /workspace /workspace/ceo
   ```

## Possíveis causas do “não apareceu”

| Causa | Explicação |
|-------|------------|
| **Clone no workspace do agente** | CEO clonou em `/workspace/ceo` → aparece em `~/clawdevs-shared/ceo/`, não em `~/clawdevs-shared/repos/`. |
| **CEO não executou clone** | Resposta baseada em contexto/documentação (“analisei a documentação”) sem ter rodado `exec` com `git clone`; ou exec falhou (rede, permissão, tool desabilitada). |
| **Mount não estava ativo** | Se o mount foi iniciado depois do “clone”, o pod pode ter escrito no volume efêmero (PVC dinâmico) em vez do shared; ao trocar para shared, o conteúdo antigo não aparece. |
| **PVC diferente** | Se em algum momento o deployment usou `openclaw-workspace-pvc` em vez de `openclaw-shared-workspace-pvc`, o `/workspace` não seria o mesmo que `~/clawdevs-shared`. |

## Ajuste recomendado

Para que repositórios clonados pelo CEO apareçam em **`~/clawdevs-shared/repos`**, o CEO deve clonar **explicitamente** em `/workspace/repos`:

- Exemplo: `git clone https://github.com/clawdevs-ai/clawdevs /workspace/repos/clawdevs`

Foi adicionada instrução no workspace do CEO (TOOLS.md / bootstrap) para sempre clonar repositórios em **`/workspace/repos/<nome-repo>`**.

## Por que dá "Input/output error" em `/workspace/` (validate-workspace)

O `/workspace` no pod do OpenClaw vem do PVC `openclaw-shared-workspace-pvc`, que usa o PV com **hostPath: /agent-shared** no nó do Minikube. Esse path é preenchido pelo **minikube mount** (9P): `~/clawdevs-shared` no host é montado em `/agent-shared` dentro do Minikube.

- **Causa do I/O error:** o mount 9P pode ficar indisponível ou em estado ruim (mount não estava ativo quando o pod subiu, processo de mount caiu, ou operações pesadas no 9P geram erro). Ao acessar `/workspace/`, o pod lê em `/agent-shared`; se o 9P não responder, o kernel devolve "Input/output error".
- **Solução:** desmontar e remontar o shared e reiniciar o pod para ele reconectar ao volume:
  1. `make shared-unmount` — encerra o processo `minikube mount` (agent-shared).
  2. `make shared` — inicia de novo o mount.
  3. `kubectl rollout restart deployment/openclaw -n ai-agents` — o pod remonta o volume e passa a enxergar o mount novo.
  - Ou use `make shared-restart`, que faz os três passos.

## Referências

- `k8s/management-team/openclaw/configmap.yaml`: `agents.list[].workspace` = `/workspace/ceo` para o CEO.
- `k8s/management-team/openclaw/README.md`: estrutura do host (`repos/` = repositórios clonados).
- `k8s/management-team/openclaw/shared-workspace-pv.yaml`: PV usa `hostPath: /agent-shared` (minikube); `minikube mount ~/clawdevs-shared:/agent-shared` faz o vínculo.
