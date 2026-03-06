// Mission Control — API client
// Comunica com o kanban-api (Flask/Redis) para dados de agentes, tarefas e tokens.

export type AgentStatus = "active" | "idle" | "offline";
export type TaskState = "Backlog" | "Em Andamento" | "Em Revisão" | "QA" | "Concluído";
export type TaskPriority = "low" | "medium" | "high" | "critical";
export type InterventionAction = "reassign" | "pause" | "cancel" | "prioritize" | "comment";

export interface Agent {
  id: string;
  status: AgentStatus;
  last_heartbeat: number | null;
  current_task: string;
  tokens_total: number;
}

export interface Task {
  id: string;
  type: "task" | "story" | "epic";
  title: string;
  summary: string;
  state: TaskState | string;
  priority: TaskPriority | string;
  created_by: string;
  created_at: number;
  updated_at?: number;
}

export interface BoardData {
  columns: string[];
  board: Record<string, Task[]>;
  total: number;
}

export interface TokenData {
  by_agent: Record<string, { tokens: number; cost_usd: number }>;
  total_tokens: number;
  daily_cap_usd: number;
}

export interface Activity {
  id: number;
  agent: string;
  message: string;
  timestamp: number;
}

function apiBase(): string {
  if (typeof window !== "undefined") return "/api";
  return (
    process.env.INTERNAL_API_URL ||
    "http://kanban-api-service.ai-agents.svc.cluster.local:5001/api"
  );
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API ${path} → ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

// ── Agents ────────────────────────────────────────────────────────────────────

export const fetchAgents = (): Promise<Agent[]> => apiFetch("/agents");

// ── Board / Tasks ─────────────────────────────────────────────────────────────

export const fetchBoard = (): Promise<BoardData> => apiFetch("/board");

export const createTask = (data: {
  title: string;
  summary?: string;
  priority?: string;
  state?: string;
  type?: string;
  agent?: string;
}): Promise<{ ok: boolean; id: string; state: string }> =>
  apiFetch("/issues", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

export const moveTask = (
  id: string,
  state: string,
  agent = "director"
): Promise<{ ok: boolean; from: string; to: string }> =>
  apiFetch(`/issues/${id}/state`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ state, agent }),
  });

export const deleteTask = (id: string): Promise<{ ok: boolean }> =>
  apiFetch(`/issues/${id}`, { method: "DELETE" });

// ── Tokens ────────────────────────────────────────────────────────────────────

export const fetchTokens = (): Promise<TokenData> => apiFetch("/tokens");

// ── Activities ────────────────────────────────────────────────────────────────

export const fetchActivities = (limit = 30): Promise<Activity[]> =>
  apiFetch(`/activities?limit=${limit}`);

// ── Interventions ─────────────────────────────────────────────────────────────

export const postIntervention = (data: {
  issue_id: string;
  action: InterventionAction;
  target_agent?: string;
  note?: string;
}): Promise<{ ok: boolean }> =>
  apiFetch("/interventions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

// ── SSE ───────────────────────────────────────────────────────────────────────

export const getSSEUrl = (): string => `${apiBase()}/events`;
