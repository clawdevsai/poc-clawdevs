"use client"

import { useEffect } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Users, CheckSquare, Activity, Clock } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { StatsCard } from "@/components/dashboard/stats-card"
import { AgentsGrid } from "@/components/dashboard/agents-grid"
import { ActivityFeed } from "@/components/dashboard/activity-feed"
import { UsageChart } from "@/components/dashboard/usage-chart"
import { customInstance } from "@/lib/axios-instance"
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
  model: string
  last_heartbeat?: string | null
}

interface ActivityEvent {
  id: string
  event_type: string
  description: string
  agent_id?: string | null
  created_at: string
}

interface Metric {
  metric_type: string
  value: number
  period_start: string
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
  customInstance<PaginatedResponse<Metric>>({
    url: "/metrics",
    method: "GET",
    params: { metric_type: "sessions", days: 7 },
  })

// ---- Page -----------------------------------------------------------------

export default function DashboardPage() {
  const queryClient = useQueryClient()

  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  })

  const { data: approvalsData, isLoading: approvalsLoading } = useQuery({
    queryKey: ["approvals", "pending"],
    queryFn: fetchApprovals,
  })

  const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
    queryKey: ["sessions"],
    queryFn: fetchSessions,
  })

  const { data: tasksData, isLoading: tasksLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: fetchTasks,
  })

  const { data: activityData, isLoading: activityLoading } = useQuery({
    queryKey: ["activity-events"],
    queryFn: fetchActivity,
  })

  const { data: metricsData, isLoading: metricsLoading } = useQuery({
    queryKey: ["metrics", "sessions", 7],
    queryFn: fetchMetrics,
  })

  // Subscribe to dashboard WebSocket channel and refetch all dashboard queries on new messages
  useEffect(() => {
    if (!wsManager) return
    const unsubscribe = wsManager.subscribe("dashboard", () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] })
      queryClient.invalidateQueries({ queryKey: ["approvals", "pending"] })
      queryClient.invalidateQueries({ queryKey: ["sessions"] })
      queryClient.invalidateQueries({ queryKey: ["tasks"] })
      queryClient.invalidateQueries({ queryKey: ["activity-events"] })
      queryClient.invalidateQueries({ queryKey: ["metrics"] })
    })
    return unsubscribe
  }, [queryClient])

  const agents = agentsData?.items ?? []
  const activeAgents = agents.filter((a) => a.status === "online").length
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
            ClawDevs AI Control Panel — real-time overview
          </p>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            icon={Clock}
            label="Total Sessions (24h)"
            value={totalSessions}
            loading={statsLoading}
          />
          <StatsCard
            icon={CheckSquare}
            label="Pending Approvals"
            value={pendingApprovals}
            loading={statsLoading}
          />
          <StatsCard
            icon={Users}
            label="Active Agents"
            value={activeAgents}
            loading={statsLoading}
          />
          <StatsCard
            icon={Activity}
            label="Total Tasks"
            value={totalTasks}
            loading={statsLoading}
          />
        </div>

        {/* Main content: agents + activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agents grid — takes 2 columns */}
          <div className="lg:col-span-2 flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-[hsl(var(--foreground))]">
                Agents
                {!agentsLoading && (
                  <span className="ml-2 text-[hsl(var(--muted-foreground))] font-normal">
                    ({agents.length})
                  </span>
                )}
              </h2>
            </div>
            <AgentsGrid agents={agents} loading={agentsLoading} />
          </div>

          {/* Activity feed — 1 column, full height */}
          <div className="flex flex-col" style={{ minHeight: "400px" }}>
            <ActivityFeed events={activityEvents} loading={activityLoading} />
          </div>
        </div>

        {/* Usage chart — full width */}
        <UsageChart metrics={metrics} loading={metricsLoading} />
      </div>
    </AppLayout>
  )
}
