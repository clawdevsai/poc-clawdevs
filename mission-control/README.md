# Mission Control — ClawDevs AI

> Painel de controle unificado para o Diretor gerenciar o time de agentes de IA.

## Por que "Mission Control"?

O nome comunica exatamente o que o Diretor faz: supervisionar, coordenar e intervir em missões de desenvolvimento executadas por agentes autônomos — assim como uma Central de Controle de Missões supervisiona uma operação espacial. O Diretor nunca escreve código; ele dá ordens e intervém quando necessário.

## Funcionalidades

| Seção | O que mostra |
|-------|-------------|
| **Dashboard** | Status de saúde dos 9 agentes + resumo de tokens + contagem de tarefas |
| **Central de Missões** | Kanban com estados: Backlog → Em Andamento → Em Revisão → QA → Concluído |
| **FinOps / Tokens** | Uso de tokens por agente + custo estimado + teto diário (FINOPS_DAILY_CAP) |
| **Feed de Atividades** | Log em tempo real de todas as ações dos agentes e intervenções do Diretor |

## Intervenção do Diretor

Em qualquer card de tarefa, o Diretor pode:
- **Mover** para outro estado
- **Reatribuir** para um agente diferente
- **Pausar** ou **cancelar** a tarefa
- **Elevar prioridade** emergencialmente
- **Adicionar comentário** de contexto

Toda intervenção é registrada no log de atividades e publicada no stream Redis `kanban:events`.

## Stack

- **Next.js 15** (App Router, TypeScript)
- **Tailwind CSS** (design dark, profissional)
- **Server-Sent Events** (atualizações em tempo real via Redis Stream)
- **kanban-api** Flask (backend)

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `KANBAN_API_URL` | URL interna K8s | Base URL do kanban-api |
| `NEXT_PUBLIC_APP_ENV` | `production` | Ambiente |

## Desenvolvimento local

```bash
cd mission-control
npm install
KANBAN_API_URL=http://localhost:5001 npm run dev
# Acesse http://localhost:3000
```

## Deploy no K8s

```bash
# Build da imagem
make kanban-image   # reutiliza o mesmo script (ajuste a tag se necessário)

# Apply no cluster
kubectl apply -f k8s/kanban/
```

> O Makefile referencia `mission-control/` para build e deploy.
