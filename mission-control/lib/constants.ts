// Constantes do Mission Control

export const AGENT_META: Record<
  string,
  { label: string; emoji: string; color: string; description: string }
> = {
  ceo: {
    label: "CEO",
    emoji: "👔",
    color: "#4f8ef7",
    description: "Orquestrador principal — rotas decisões estratégicas",
  },
  po: {
    label: "PO",
    emoji: "📋",
    color: "#a855f7",
    description: "Product Owner — quebra requisitos em issues",
  },
  architect: {
    label: "Arquiteto",
    emoji: "🏛️",
    color: "#06b6d4",
    description: "Decisões técnicas e revisão de arquitetura",
  },
  developer: {
    label: "Developer",
    emoji: "💻",
    color: "#22c55e",
    description: "Implementação de código e features",
  },
  ux: {
    label: "UX",
    emoji: "🎨",
    color: "#f97316",
    description: "Design de interfaces e experiência do usuário",
  },
  qa: {
    label: "QA",
    emoji: "🔬",
    color: "#eab308",
    description: "Testes, qualidade e validação",
  },
  devops: {
    label: "DevOps",
    emoji: "⚙️",
    color: "#64748b",
    description: "Infraestrutura, CI/CD e deploys",
  },
  cybersec: {
    label: "CyberSec",
    emoji: "🛡️",
    color: "#ef4444",
    description: "Segurança, SAST, análise de vulnerabilidades",
  },
  dba: {
    label: "DBA",
    emoji: "🗄️",
    color: "#8b5cf6",
    description: "Banco de dados, schemas e migrations",
  },
};

export const TASK_STATES = [
  "Backlog",
  "Em Andamento",
  "Em Revisão",
  "QA",
  "Concluído",
] as const;

export const STATE_COLORS: Record<string, string> = {
  Backlog: "#6366f1",
  "Em Andamento": "#3b82f6",
  "Em Revisão": "#f59e0b",
  QA: "#a855f7",
  Concluído: "#22c55e",
};

export const PRIORITY_COLORS: Record<string, string> = {
  low: "#64748b",
  medium: "#3b82f6",
  high: "#f59e0b",
  critical: "#ef4444",
};

export const PRIORITY_LABELS: Record<string, string> = {
  low: "Baixa",
  medium: "Média",
  high: "Alta",
  critical: "Crítica",
};

export const INTERVENTION_ACTIONS = [
  { value: "reassign", label: "Reatribuir agente" },
  { value: "pause", label: "Pausar tarefa" },
  { value: "cancel", label: "Cancelar tarefa" },
  { value: "prioritize", label: "Elevar prioridade" },
  { value: "comment", label: "Adicionar comentário" },
] as const;
