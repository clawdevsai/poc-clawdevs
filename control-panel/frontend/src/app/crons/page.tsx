"use client"

import { useEffect, useState } from "react"
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query"
import { formatDistanceToNow } from "date-fns"
import { Play, Clock, RefreshCw } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { AgentAvatar } from "@/components/agents/agent-avatar"
import { customInstance } from "@/lib/axios-instance"
import { wsManager } from "@/lib/ws"
import { cn } from "@/lib/utils"

// ---- Types ----------------------------------------------------------------

interface Agent {
  id: string
  slug: string
  display_name: string
  role: string
  status: string
  model: string
  cron_expression?: string | null
  cron_status?: string | null
  last_heartbeat?: string | null
}

interface AgentsResponse {
  items: Agent[]
  total: number
}

interface CronExecution {
  id: string
  agent_id: string
  agent_slug?: string
  started_at: string
  finished_at?: string | null
  exit_code?: number | null
  log_tail?: string | null
  status: string
}

interface CronExecutionsResponse {
  items: CronExecution[]
  total: number
}

// ---- Fetchers / Mutators --------------------------------------------------

const fetchAgents = () =>
  customInstance<AgentsResponse>({ url: "/agents", method: "GET" })

const fetchCronExecutions = () =>
  customInstance<CronExecutionsResponse>({
    url: "/cron-executions",
    method: "GET",
    params: { page: 1, page_size: 20 },
  })

const triggerCron = (agentSlug: string) =>
  customInstance<unknown>({
    url: `/crons/${agentSlug}/trigger`,
    method: "POST",
  })

// ---- Helpers --------------------------------------------------------------

function cronStatusVariant(
  status: string
): "success" | "warning" | "error" | "secondary" {
  switch (status) {
    case "running":
      return "warning"
    case "idle":
      return "secondary"
    case "error":
      return "error"
    default:
      return "secondary"
  }
}

function execStatusVariant(
  status: string
): "success" | "error" | "secondary" {
  if (status === "success") return "success"
  if (status === "error" || status === "failed") return "error"
  return "secondary"
}

function durationLabel(exec: CronExecution) {
  if (!exec.finished_at) return "—"
  const ms =
    new Date(exec.finished_at).getTime() -
    new Date(exec.started_at).getTime()
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

// ---- Sub-components -------------------------------------------------------

function CronCardSkeleton() {
  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 space-y-3">
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-full" />
        <div className="flex flex-col gap-1.5 flex-1">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-3 w-20" />
        </div>
        <Skeleton className="h-5 w-14 rounded-full" />
      </div>
      <Skeleton className="h-3 w-40" />
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-7 w-24 rounded-lg" />
      </div>
    </div>
  )
}

function CronCard({
  agent,
  onTrigger,
  triggering,
}: {
  agent: Agent
  onTrigger: (slug: string) => void
  triggering: boolean
}) {
  const status = agent.cron_status ?? "idle"

  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3">
      {/* Top row */}
      <div className="flex items-center gap-3">
        <AgentAvatar
          slug={agent.slug}
          displayName={agent.display_name}
          size="md"
        />
        <div className="flex flex-col gap-0.5 flex-1 min-w-0">
          <span className="text-sm font-semibold text-[hsl(var(--foreground))] truncate">
            {agent.display_name}
          </span>
          <span className="text-xs text-[hsl(var(--muted-foreground))] truncate">
            {agent.role}
          </span>
        </div>
        <Badge variant={cronStatusVariant(status)}>
          <span
            className={cn(
              "mr-1 h-1.5 w-1.5 rounded-full inline-block",
              status === "running"
                ? "bg-yellow-400"
                : status === "error"
                ? "bg-red-400"
                : "bg-white/30"
            )}
          />
          {status}
        </Badge>
      </div>

      {/* Cron expression */}
      <div className="flex items-center gap-1.5 text-xs text-[hsl(var(--muted-foreground))]">
        <Clock className="h-3 w-3 shrink-0" />
        <code className="font-mono">{agent.cron_expression}</code>
      </div>

      {/* Footer row */}
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs text-[hsl(var(--muted-foreground))]">
          {agent.last_heartbeat
            ? `Last run ${formatDistanceToNow(new Date(agent.last_heartbeat), { addSuffix: true })}`
            : "No runs yet"}
        </span>
        <button
          onClick={() => onTrigger(agent.slug)}
          disabled={triggering}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-[hsl(var(--primary))]/10 text-[hsl(var(--primary))] border border-[hsl(var(--primary))]/30 hover:bg-[hsl(var(--primary))]/20 disabled:opacity-50 transition-colors"
        >
          {triggering ? (
            <RefreshCw className="h-3 w-3 animate-spin" />
          ) : (
            <Play className="h-3 w-3" />
          )}
          Trigger Now
        </button>
      </div>
    </div>
  )
}

function ExecTableRowSkeleton() {
  return (
    <tr className="border-b border-[hsl(var(--border))]">
      {Array.from({ length: 5 }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  )
}

// ---- Page -----------------------------------------------------------------

export default function CronsPage() {
  const queryClient = useQueryClient()
  const [triggeringSlug, setTriggeringSlug] = useState<string | null>(null)

  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  })

  const { data: execData, isLoading: execLoading } = useQuery({
    queryKey: ["cron-executions"],
    queryFn: fetchCronExecutions,
  })

  const triggerMutation = useMutation({
    mutationFn: triggerCron,
    onSettled: () => {
      setTriggeringSlug(null)
      queryClient.invalidateQueries({ queryKey: ["cron-executions"] })
      queryClient.invalidateQueries({ queryKey: ["agents"] })
    },
  })

  // Live updates via WebSocket "crons" channel
  useEffect(() => {
    if (!wsManager) return
    const unsub = wsManager.subscribe("crons", () => {
      queryClient.invalidateQueries({ queryKey: ["cron-executions"] })
      queryClient.invalidateQueries({ queryKey: ["agents"] })
    })
    return unsub
  }, [queryClient])

  const agents = (agentsData?.items ?? []).filter(
    (a) => a.cron_expression && a.cron_expression.trim() !== ""
  )
  const executions = execData?.items ?? []

  function handleTrigger(slug: string) {
    setTriggeringSlug(slug)
    triggerMutation.mutate(slug)
  }

  return (
    <AppLayout>
      <div className="flex flex-col gap-8">
        {/* Header */}
        <div>
          <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
            Cron Monitor
          </h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
            {agentsLoading
              ? "Loading…"
              : `${agents.length} scheduled agent${agents.length !== 1 ? "s" : ""}`}
          </p>
        </div>

        {/* Cron agent cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
          {agentsLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <CronCardSkeleton key={i} />
            ))
          ) : agents.length === 0 ? (
            <div className="col-span-full flex flex-col items-center justify-center py-16 gap-3">
              <div className="h-12 w-12 rounded-full bg-[hsl(var(--muted))] flex items-center justify-center">
                <Clock className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
              </div>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                No agents with cron expressions configured
              </p>
            </div>
          ) : (
            agents.map((agent) => (
              <CronCard
                key={agent.slug}
                agent={agent}
                onTrigger={handleTrigger}
                triggering={triggeringSlug === agent.slug}
              />
            ))
          )}
        </div>

        {/* Execution history */}
        <div className="flex flex-col gap-3">
          <h2 className="text-base font-semibold text-[hsl(var(--foreground))]">
            Execution History
          </h2>
          <div className="rounded-xl border border-[hsl(var(--border))] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30">
                    {["Agent", "Started", "Duration", "Exit Code", "Status"].map(
                      (h) => (
                        <th
                          key={h}
                          className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide"
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {execLoading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                      <ExecTableRowSkeleton key={i} />
                    ))
                  ) : executions.length === 0 ? (
                    <tr>
                      <td
                        colSpan={5}
                        className="px-4 py-10 text-center text-sm text-[hsl(var(--muted-foreground))]"
                      >
                        No executions recorded yet.
                      </td>
                    </tr>
                  ) : (
                    executions.map((exec) => (
                      <tr
                        key={exec.id}
                        className="border-b border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/10 transition-colors"
                      >
                        <td className="px-4 py-3 font-mono text-xs text-[hsl(var(--foreground))]">
                          {exec.agent_slug ?? exec.agent_id.slice(0, 12)}
                        </td>
                        <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))]">
                          {formatDistanceToNow(new Date(exec.started_at), {
                            addSuffix: true,
                          })}
                        </td>
                        <td className="px-4 py-3 text-xs tabular-nums text-[hsl(var(--foreground))]">
                          {durationLabel(exec)}
                        </td>
                        <td className="px-4 py-3 text-xs tabular-nums text-[hsl(var(--foreground))]">
                          {exec.exit_code ?? "—"}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={execStatusVariant(exec.status)}>
                            {exec.status}
                          </Badge>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
