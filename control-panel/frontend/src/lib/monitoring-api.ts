/*
 * Monitoring API client helpers
 */

import { customInstance } from "./axios-instance"

export interface SessionItem {
  id: string
  agent_slug: string | null
  session_label: string
  session_kind: string
  status: string
  message_count: number
  token_count: number
  last_active_at: string | null
  created_at: string
}

export interface SessionsResponse {
  items: SessionItem[]
  total: number
}

export interface MetricsPoint {
  metric_type: string | null
  value: number
  period_start: string
}

export interface MetricsResponse {
  items: MetricsPoint[]
  total: number
}

export interface OverviewMetrics {
  active_agents: number
  pending_approvals: number
  open_tasks: number
  tokens_24h: number
  tokens_consumed_total: number
  tokens_consumed_avg_per_task: number
  backlog_count: number
  tasks_in_progress: number
  tasks_completed: number
}

export interface CycleTimeResponse {
  cycle_time_avg_seconds: number
  cycle_time_p95_seconds: number
  window_minutes: number
}

export interface ThroughputItem {
  group: string
  completed_count: number
}

export interface ThroughputResponse {
  window_minutes: number
  group_by: string
  items: ThroughputItem[]
}

export interface FailureListItem {
  id: string
  title: string
  status: string
  failure_count: number
  consecutive_failures: number
  last_error: string | null
  last_failed_at: string | null
  escalated: boolean
}

export interface FailuresResponse {
  total: number
  offset: number
  limit: number
  tasks: FailureListItem[]
}

export interface FailureDetail {
  message: string | null
  stack_trace: string | null
  evidence: string[]
}

export interface AgentItem {
  id: string
  slug: string
  display_name: string
  status: string
}

export interface AgentsResponse {
  items: AgentItem[]
  total: number
}

export interface RuntimeSettings {
  limits: Record<string, unknown>
  flags: Record<string, unknown>
  model_provider: string
  model_name: string
  agent_updates: unknown[]
  thresholds: Record<string, unknown>
}

export interface RuntimeSettingsUpdatePayload {
  limits?: Record<string, unknown>
  flags?: Record<string, unknown>
  model_provider?: string
  model_name?: string
  agent_updates?: Array<Record<string, unknown>>
  thresholds?: Record<string, unknown>
  confirm_text?: string
}

export const listSessions = async (opts: { windowMinutes?: number | null }) => {
  const params =
    typeof opts.windowMinutes === "number"
      ? { window_minutes: opts.windowMinutes }
      : undefined
  return customInstance<SessionsResponse>({
    url: "/sessions",
    method: "GET",
    params,
  })
}

export const getMetricsSeries = async (opts: {
  metricType?: string
  hours?: number
  intervalMinutes?: number
}) => {
  return customInstance<MetricsResponse>({
    url: "/metrics",
    method: "GET",
    params: {
      metric_type: opts.metricType ?? "active_sessions",
      hours: opts.hours ?? 24,
      interval_minutes: opts.intervalMinutes ?? 1,
    },
  })
}

export const getOverviewMetrics = async (opts: { windowMinutes?: number }) => {
  return customInstance<OverviewMetrics>({
    url: "/metrics/overview",
    method: "GET",
    params: { window_minutes: opts.windowMinutes ?? 30 },
  })
}

export const getCycleTime = async (opts: { windowMinutes?: number }) => {
  return customInstance<CycleTimeResponse>({
    url: "/metrics/cycle-time",
    method: "GET",
    params: { window_minutes: opts.windowMinutes ?? 30 },
  })
}

export const getThroughput = async (opts: {
  windowMinutes?: number
  groupBy?: string
}) => {
  return customInstance<ThroughputResponse>({
    url: "/metrics/throughput",
    method: "GET",
    params: {
      window_minutes: opts.windowMinutes ?? 30,
      group_by: opts.groupBy ?? "label",
    },
  })
}

export const getFailures = async () =>
  customInstance<FailuresResponse>({
    url: "/api/health/failures",
    method: "GET",
  })

export const getFailureDetail = async (taskId: string) =>
  customInstance<FailureDetail>({
    url: `/tasks/${taskId}/failure`,
    method: "GET",
  })

export const listAgents = async () =>
  customInstance<AgentsResponse>({
    url: "/agents",
    method: "GET",
  })

export const getRuntimeSettings = async () =>
  customInstance<RuntimeSettings>({
    url: "/settings/runtime",
    method: "GET",
  })

export const updateRuntimeSettings = async (payload: RuntimeSettingsUpdatePayload) =>
  customInstance<RuntimeSettings>({
    url: "/settings/runtime",
    method: "PUT",
    data: payload,
  })
