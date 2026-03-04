# OpenClaw Gateway no Kubernetes

Deployment do Gateway OpenClaw (Telegram, Slack, Ollama no cluster). Imagem local: `make openclaw-image`.

## Workspace compartilhado (pasta física no host)

Para que o workspace dos agentes seja **a mesma pasta na sua máquina** (ver soul, memória, skills e repositórios clonados fora do K8s):

### 1. Criar pasta no host

Exemplo (ajuste o caminho se quiser):

```bash
mkdir -p ~/clawdevs-shared
# ou dentro do repo: mkdir -p agent-shared
```

### 2. Montar no Minikube (obrigatório)

O processo precisa ficar rodando para o volume funcionar. **Use `make shared`** (recomendado) ou em um terminal:

```bash
minikube mount ~/clawdevs-shared:/agent-shared --uid=0 --gid=0
```

Ou em background: `nohup minikube mount ~/clawdevs-shared:/agent-shared --uid=0 --gid=0 &`

> **⚠️ OBRIGATÓRIO:** `--uid=0 --gid=0` é necessário porque o container do OpenClaw roda como root. Sem isso, o workspace fica com erro de I/O dentro do pod.

**Importante:** sem esse mount, o PV fica vazio/inacessível dentro do VM.

> **Nota:** `make up` agora verifica e inicia o mount automaticamente (target `shared-ensure`). Para subir tudo de uma vez, basta `make up`.

### 3. Aplicar PV e PVC do workspace compartilhado

Antes do deployment do OpenClaw:

```bash
kubectl apply -f k8s/management-team/openclaw/shared-workspace-pv.yaml
kubectl apply -f k8s/management-team/openclaw/shared-workspace-pvc.yaml
```

### 4. Aplicar o deployment

O deployment já usa o claim `openclaw-shared-workspace-pvc`. Suba o núcleo com `make up` ou aplique o deployment:

```bash
kubectl apply -f k8s/management-team/openclaw/deployment.yaml
```

### Estrutura na pasta do host

Após o init e o uso pelos agentes, você verá em `~/clawdevs-shared` (ou o caminho que escolheu):

| Pasta | Conteúdo |
|-------|----------|
| **soul/** | SOUL de cada agente (ceo.md, po.md, developer.md, …) |
| **ceo/**, **po/**, **devops/**, **architect/**, **developer/**, **qa/**, **cybersec/**, **ux/**, **dba/** | Cada um com SOUL.md, memory/, e arquivos que o OpenClaw criar (AGENTS.md, notas) |
| **workspace/** | Repositórios clonados pelos agentes (ex.: clawdevs/docs, outros repos) |

Repositórios que os agentes clonarem (ex.: via git ou ferramenta de download) devem ir em **`/workspace`** dentro do pod; na sua máquina isso aparece em `<pasta-host>/workspace/`.

### Observações

- **Performance:** O mount 9P do Minikube pode ter lentidão em pastas com muitos arquivos (>600). Para muitos repos, manter `workspace/<repo>/` com estrutura normal costuma ser aceitável.
- **UID/GID:** O mount DEVE usar `--uid=0 --gid=0` (o container roda como root). O `make shared` já faz isso. Sem as flags corretas, o pod terá `EIO: i/o error` e o agente não responderá.
- **Alternativa sem host:** Se não for usar pasta no host, use o PVC dinâmico original: em `deployment.yaml` troque `claimName` para `openclaw-workspace-pvc` e aplique `k8s/management-team/openclaw/pvc.yaml` em vez do PV/PVC compartilhado.
