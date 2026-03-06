# 10 — Infraestrutura e Kubernetes
> **Objetivo:** Mapear a topologia e as configurações (NetworkPolicies, ResourceQuotas) do cluster Minikube local.
> **Público-alvo:** DevOps, Devs
> **Ação Esperada:** Devs utilizam como referência para deployments e troubleshooting; garante a política de Zero Trust.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Visão dos Namespaces

```mermaid
graph LR
    subgraph K8S["☸️ Minikube Cluster (local)"]

        subgraph NS_GW["clawdevs-gateway"]
            OC_POD["pod: openclaw\n:18789"]
        end

        subgraph NS_AGENTS["clawdevs-agents"]
            ORCH["pod: orchestrator"]
            CEO_P["pod: agent-ceo"]
            PO_P["pod: agent-po"]
            ARCH_P["pod: agent-architect"]
            DEV_P["pod: agent-developer"]
            QA_P["pod: agent-qa"]
        end

        subgraph NS_INFRA["clawdevs-infra"]
            OLLAMA_P["pod: ollama\n:11434"]
        end
    end

    INTERNET(("🌐 Internet")) -->|"Telegram/Slack API"| OC_POD
    OC_POD -->|"NetworkPolicy: permitido"| ORCH
    ORCH -->|"NetworkPolicy: permitido"| CEO_P & PO_P & ARCH_P & DEV_P & QA_P
    CEO_P & PO_P & ARCH_P & DEV_P & QA_P -->|":11434"| OLLAMA_P

    style NS_GW fill:#7C3AED22,stroke:#7C3AED
    style NS_AGENTS fill:#05966922,stroke:#059669
    style NS_INFRA fill:#D9770622,stroke:#D97706
```

---

## NetworkPolicy — Zero Trust entre namespaces

```mermaid
graph TD
    subgraph RULES["Regras de tráfego (NetworkPolicy)"]
        R1["✅ gateway → agents\nIngress permitido"]
        R2["✅ agents → infra\nEgress: :11434"]
        R5["❌ agents → internet\nBloqueado — sem acesso direto"]
        R6["❌ agents → agents\nSem comunicação P2P — apenas via orchestrator"]
        R7["❌ infra → agents\nSem iniciativa — apenas responde requisições"]
    end

    style R1 fill:#05966922,stroke:#059669
    style R2 fill:#05966922,stroke:#059669
    style R3 fill:#05966922,stroke:#059669
    style R4 fill:#05966922,stroke:#059669
    style R5 fill:#DC262622,stroke:#DC2626
    style R6 fill:#DC262622,stroke:#DC2626
    style R7 fill:#DC262622,stroke:#DC2626
```

---

## Anatomia de um pod de agente

```mermaid
graph TD
    subgraph POD["pod: agent-developer (namespace: clawdevs-agents)"]
        CONT["Container: clawdevs/agent-base:latest"]

        subgraph ENV["Variáveis de ambiente"]
            E1["AGENT_ROLE=developer"]
            E2["SOUL_PATH=/config/souls/developer.yaml"]
            E3["OLLAMA_ENDPOINT=http://ollama-service...:11434"]
            E4["OPENROUTER_API_KEY ← Secret K8s"]
        end

        subgraph VOL["Volumes"]
            V1["ConfigMap: soul-config\n→ /config/souls/"]
            V2["PVC: workspace-pvc\n→ /workspace/"]
        end

        subgraph RES["Resources"]
            RL["Limits: 4Gi RAM · 2 CPU"]
            RR["Requests: 2Gi RAM · 500m CPU"]
        end
    end

    CM["ConfigMap\nagent-souls"] -->|"mount"| V1
    PVC["PersistentVolumeClaim\nworkspace-pvc"] -->|"mount"| V2
    SEC["Secret\nclawdevs-secrets"] -->|"secretKeyRef"| E4

    style POD fill:#05966922,stroke:#059669
```

---

## Volumes e persistência

```mermaid
graph LR
    subgraph PVCs["PersistentVolumeClaims"]
        WS["workspace-pvc\nReadWriteMany\n100Gi\n→ /workspace dos agentes"]
        OL_V["ollama-models-pvc\nReadWriteOnce\n200Gi\n→ /root/.ollama"]
    end

    AGENTS["Pods de agentes"] -->|"leitura/escrita de código"| WS
    OLLAMA_P["Pod Ollama"] -->|"modelos persistem entre restarts"| OL_V
```

---

## ResourceQuotas — Proteção do cluster

```mermaid
xychart-beta
    title "Limites de recursos por namespace"
    x-axis ["CPU Request", "CPU Limit", "RAM Request (Gi)", "RAM Limit (Gi)"]
    y-axis "Valor" 0 --> 30
    bar [4, 8, 16, 24]
```

| Namespace | CPU Request | CPU Limit | RAM Request | RAM Limit | Max Pods |
|---|---|---|---|---|---|
| clawdevs-agents | 4 cores | 8 cores | 16 Gi | 24 Gi | 10 |
| clawdevs-infra | 6 cores | 10 cores | 24 Gi | 32 Gi | 8 |
| clawdevs-gateway | 1 core | 2 cores | 2 Gi | 4 Gi | 3 |

---

## Hardware de referência

```mermaid
graph LR
    subgraph HW["Máquina de referência"]
        CPU["CPU\n8+ cores\nIntel i7 / AMD Ryzen 7"]
        RAM["RAM\n32 GB DDR4/DDR5"]
        GPU["GPU (opcional)\nNVIDIA RTX 3060\n12 GB VRAM"]
        DISK["Disco\n500 GB NVMe SSD"]
        OS["SO\nUbuntu 22.04 LTS\nou macOS 14+"]
    end

    subgraph PROFILES["Perfis de execução"]
        LITE["Perfil LITE\n4 agentes simultâneos\nSem GPU"]
        FULL["Perfil FULL\nTime completo\nCom GPU"]
    end

    CPU & RAM --> LITE & FULL
    GPU --> FULL
    DISK --> LITE & FULL

    style LITE fill:#D9770622,stroke:#D97706
    style FULL fill:#05966922,stroke:#059669
```

---

## Manifests YAML de referência

### Namespace base

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: clawdevs-agents
  labels:
    name: clawdevs-agents
    env: production
    managed-by: clawdevs
```

### NetworkPolicy — isolamento de agentes

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agent-isolation
  namespace: clawdevs-agents
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: clawdevs-gateway
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: clawdevs-infra
    ports:
    - port: 11434   # Ollama
```

### ResourceQuota — agentes

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: agents-quota
  namespace: clawdevs-agents
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 16Gi
    limits.cpu: "8"
    limits.memory: 24Gi
    pods: "10"
```

### Deployment — agente genérico

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-developer
  namespace: clawdevs-agents
  labels:
    app: clawdevs
    role: developer
spec:
  replicas: 1
  selector:
    matchLabels:
      role: developer
  template:
    metadata:
      labels:
        role: developer
    spec:
      containers:
      - name: agent-developer
        image: clawdevs/agent-base:latest
        env:
        - name: AGENT_ROLE
          value: "developer"
        - name: SOUL_PATH
          value: "/config/souls/developer.yaml"
        - name: OLLAMA_ENDPOINT
          value: "http://ollama-service.clawdevs-infra:11434"
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: clawdevs-secrets
              key: openrouter-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: soul-config
          mountPath: /config/souls
          readOnly: true
        - name: workspace
          mountPath: /workspace
      volumes:
      - name: soul-config
        configMap:
          name: agent-souls
      - name: workspace
        persistentVolumeClaim:
          claimName: workspace-pvc
```

### Deployment — Ollama

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ollama
  namespace: clawdevs-infra
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ollama
  template:
    metadata:
      labels:
        app: ollama
    spec:
      containers:
      - name: ollama
        image: ollama/ollama:latest
        ports:
        - containerPort: 11434
        resources:
          limits:
            nvidia.com/gpu: 1       # remover se sem GPU
            memory: "20Gi"
            cpu: "4000m"
          requests:
            memory: "8Gi"
            cpu: "2000m"
        volumeMounts:
        - name: ollama-models
          mountPath: /root/.ollama
      volumes:
      - name: ollama-models
        persistentVolumeClaim:
          claimName: ollama-models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ollama-service
  namespace: clawdevs-infra
spec:
  selector:
    app: ollama
  ports:
  - port: 11434
    targetPort: 11434
  type: ClusterIP
```


