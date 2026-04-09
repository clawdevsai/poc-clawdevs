/* 
 * Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

"use client"

import { useEffect } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Users, CheckSquare, Activity, Clock } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { StatsCard } from "@/components/dashboard/stats-card"
import { AgentsGrid } from "@/components/dashboard/agents-grid"
import { ActivityFeed } from "@/components/dashboard/activity-feed"
import { UsageChart } from "@/components/dashboard/usage-chart"
import { TaskHealth } from "@/components/dashboard/task-health"
import { customInstance } from "@/lib/axios-instance"
import { getMetricsSeries } from "@/lib/monitoring-api"
import { wsManager } from "@/lib/ws"

// ---- Types ----------------------------------------------------------------

interface PaginatedResponse<T> {
  items: T[]
  total: number
}

interface Agent {
  id: string
  slug: string
  display_name: string
  role: string
  status: string
  runtime_status?: string | null
  model?: string | null
  current_model?: string | null
  last_heartbeat?: string | null
  last_heartbeat_at?: string | null
}

interface ActivityEvent {
  id: string
  event_type: string
  description: string
  agent_id?: string | null
  created_at: string
}

// ---- Fetchers -------------------------------------------------------------

const fetchAgents = () =>
  customInstance<PaginatedResponse<Agent>>({ url: "/agents", method: "GET" })

const fetchApprovals = () =>
  customInstance<PaginatedResponse<unknown>>({
    url: "/approvals",
    method: "GET",
    params: { status: "pending" },
  })

const fetchSessions = () =>
  customInstance<PaginatedResponse<unknown>>({ url: "/sessions", method: "GET" })

const fetchTasks = () =>
  customInstance<PaginatedResponse<unknown>>({ url: "/tasks", method: "GET" })

const fetchActivity = () =>
  customInstance<PaginatedResponse<ActivityEvent>>({
    url: "/activity-events",
    method: "GET",
    params: { limit: 20 },
  })

const fetchMetrics = () =>
  getMetricsSeries({
    metricType: "active_sessions",
    hours: 24,
    intervalMinutes: 1,
  })

const fetchHealthSummary = () =>
  customInstance<{ healthy: number; stalled: number; failed: number; blocked: number }>({
    url: "/api/health/summary",
    method: "GET",
  })

// ---- Page -----------------------------------------------------------------

export default function DashboardPage() {
  const queryClient = useQueryClient()

  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
    refetchInterval: 15000,
  })

  const { data: approvalsData, isLoading: approvalsLoading } = useQuery({
    queryKey: ["approvals-pending-count"],
    queryFn: fetchApprovals,
    refetchInterval: 15000,
  })

  const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
    queryKey: ["sessions"],
    queryFn: fetchSessions,
    refetchInterval: 15000,
  })

  const { data: tasksData, isLoading: tasksLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: fetchTasks,
    refetchInterval: 15000,
  })

  const { data: activityData, isLoading: activityLoading } = useQuery({
    queryKey: ["activity-events"],
    queryFn: fetchActivity,
    refetchInterval: 15000,
  })

   const { data: metricsData, isLoading: metricsLoading, isError: metricsError } = useQuery({
     queryKey: ["metrics", "active_sessions", 24, 1],
     queryFn: fetchMetrics,
     refetchInterval: 60000,
   })

   const { data: healthData, isLoading: healthLoading } = useQuery({
     queryKey: ["health-summary"],
     queryFn: fetchHealthSummary,
     refetchInterval: 15000,
   })

  // Subscribe to dashboard WebSocket channel and refetch all dashboard queries on new messages
  useEffect(() => {
    if (!wsManager) return
    const unsubscribe = wsManager.subscribe("dashboard", () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] })
      queryClient.invalidateQueries({ queryKey: ["approvals-pending-count"] })
      queryClient.invalidateQueries({ queryKey: ["sessions"] })
      queryClient.invalidateQueries({ queryKey: ["tasks"] })
      queryClient.invalidateQueries({ queryKey: ["activity-events"] })
      queryClient.invalidateQueries({ queryKey: ["metrics"] })
    })
    return unsubscribe
  }, [queryClient])

  const agents = agentsData?.items ?? []
  const activeAgents = agents.filter((a) => {
    const status = a.runtime_status ?? a.status
    return status === "online" || status === "working"
  }).length
  const pendingApprovals = approvalsData?.total ?? 0
  const totalSessions = sessionsData?.total ?? 0
  const totalTasks = tasksData?.total ?? 0
  const activityEvents = activityData?.items ?? []
  const metrics = metricsData?.items ?? []

  const statsLoading =
    agentsLoading || approvalsLoading || sessionsLoading || tasksLoading

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Page heading */}
        <div>
          <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">Dashboard</h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
            Painel de Controle ClawDevs AI — visão geral em tempo real
          </p>
        </div>

        <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatsCard
            icon={Clock}
            label="Sessões Totais (24h)"
            value={totalSessions}
            loading={statsLoading}
          />
          <StatsCard
            icon={CheckSquare}
            label="Aprovações Pendentes"
            value={pendingApprovals}
            loading={statsLoading}
          />
          <StatsCard
            icon={Users}
            label="Agentes Ativos"
            value={activeAgents}
            loading={statsLoading}
          />
          <StatsCard
            icon={Activity}
            label="Total de Tarefas"
            value={totalTasks}
            loading={statsLoading}
          />
        </section>

        <section className="grid min-w-0 grid-cols-1 gap-4 xl:grid-cols-5">
          <div className="min-w-0 xl:col-span-3">
            <UsageChart metrics={metrics} loading={metricsLoading} error={metricsError} />
          </div>
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4">
            <h2 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-4">
              Ciclos dos Agentes
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[hsl(var(--muted-foreground))]">Memory Curator</span>
                <span className="text-xs text-green-500">Saudável</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[hsl(var(--muted-foreground))]">Dev Backend</span>
                <span className="text-xs text-green-500">Saudável</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-[hsl(var(--muted-foreground))]">QA Engineer</span>
                <span className="text-xs text-yellow-500">3 tentativas</span>
              </div>
            </div>
          </div>
        </section>

        {/* Agents grid — full width */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-[hsl(var(--foreground))]">
              Agentes
              {!agentsLoading && (
                <span className="ml-2 text-[hsl(var(--muted-foreground))] font-normal">
                  ({agents.length})
                </span>
              )}
            </h2>
          </div>
          <div className="min-w-0 xl:col-span-2">
            <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-[hsl(var(--foreground))]">
                  Agents
                </h2>
                {!agentsLoading && (
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    {agents.length} active entries
                  </span>
                )}
              </div>
              <AgentsGrid agents={agents} loading={agentsLoading} />
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  )
}
