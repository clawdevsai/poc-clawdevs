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

import { useEffect, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { formatDistanceToNow } from "date-fns"
import Link from "next/link"
import { AxiosError } from "axios"
import { BarChart3, RefreshCw } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { StatsCard } from "@/components/dashboard/stats-card"
import { customInstance } from "@/lib/axios-instance"
import { wsManager } from "@/lib/ws"
import { cn } from "@/lib/utils"

// ---- Types ----------------------------------------------------------------

interface ContextModeMetrics {
  status: string
  compression_rate: number
  tokens_saved_estimate: number
  total_executions: number
  total_agents: number
  indexed_agents: number
  average_compression_ratio: number
  monthly_savings_estimate: number
  last_updated: string
}

interface AgentMetrics {
  agent_id: string
  display_name?: string
  compression_ratio: number
  tokens_saved: number
  indexed_at: string
  memory_size_bytes: number
  status: "indexed" | "pending" | "error"
}

interface ContextModeResponse {
  metrics: ContextModeMetrics
  agents?: AgentMetrics[]
}

// ---- Fetchers -------------------------------------------------------------

const fetchContextModeMetrics = () =>
  customInstance<ContextModeMetrics>({
    url: "/context-mode/metrics",
    method: "GET",
  })

const fetchAgentMetrics = () =>
  customInstance<AgentMetrics[]>({
    url: "/context-mode/metrics",
    method: "GET",
  })

// ---- Sub-components -------------------------------------------------------

function MetricsSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5"
        >
          <div className="flex flex-col gap-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>
      ))}
    </div>
  )
}

function AgentMetricsSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex gap-4"
        >
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-24" />
        </div>
      ))}
    </div>
  )
}

function statusBadgeVariant(status: string) {
  switch (status) {
    case "indexed":
      return "success"
    case "pending":
      return "warning"
    case "error":
      return "error"
    default:
      return "secondary"
  }
}

// ---- Page -----------------------------------------------------------------

export default function MonitoringPage() {
  const queryClient = useQueryClient()
  const [isRefreshing, setIsRefreshing] = useState(false)

  const { data: metrics, isLoading, isError, error } = useQuery({
    queryKey: ["context-mode", "metrics"],
    queryFn: fetchContextModeMetrics,
    retry: false,
    refetchInterval: 60000, // Refetch every minute
  })

  const { data: agentMetrics, isLoading: agentsLoading } = useQuery({
    queryKey: ["context-mode", "agents"],
    queryFn: fetchAgentMetrics,
    retry: false,
    refetchInterval: 120000, // Refetch every 2 minutes
  })

  // Live-update via WebSocket "context-mode-metrics" channel
  useEffect(() => {
    if (!wsManager) return
    const unsub = wsManager.subscribe("context-mode-metrics", (event: any) => {
      if (event.event_type === "metric_updated") {
        queryClient.invalidateQueries({ queryKey: ["context-mode", "metrics"] })
        queryClient.invalidateQueries({
          queryKey: ["context-mode", "agents"],
        })
      }
    })
    return unsub
  }, [queryClient])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      await queryClient.refetchQueries({
        queryKey: ["context-mode", "metrics"],
      })
      await queryClient.refetchQueries({
        queryKey: ["context-mode", "agents"],
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
              Monitoring
            </h1>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
              {isLoading
                ? "Loading metrics..."
                : `Context-mode compression metrics ${metrics?.last_updated ? `(updated ${formatDistanceToNow(new Date(metrics.last_updated), { addSuffix: true })})` : ""}`}
            </p>
          </div>

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] text-sm font-medium text-[hsl(var(--foreground))] hover:bg-[hsl(var(--card)/0.8)] disabled:opacity-50 transition-colors"
          >
            <RefreshCw
              className={cn(
                "h-4 w-4",
                isRefreshing && "animate-spin"
              )}
            />
            Refresh
          </button>
        </div>

        {/* Error State */}
        {isError && (
          <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 text-sm text-[hsl(var(--muted-foreground))]">
            {(error as AxiosError | null)?.response?.status === 401 ? (
              <>
                Session expired or not authenticated.{" "}
                <Link
                  href="/login"
                  className="text-[hsl(var(--primary))] underline underline-offset-2"
                >
                  Sign in again
                </Link>
                .
              </>
            ) : (
              "Could not load monitoring metrics right now."
            )}
          </div>
        )}

        {/* Metrics Overview */}
        {isLoading ? (
          <MetricsSkeleton />
        ) : metrics ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatsCard
              label="Compression Rate"
              value={`${(metrics.compression_rate * 100).toFixed(1)}%`}
              trend={metrics.compression_rate > 0.8 ? "↑" : "→"}
              icon={BarChart3}
            />
            <StatsCard
              label="Tokens Saved/Hour"
              value={`${(metrics.tokens_saved_estimate / 1000).toFixed(0)}K`}
              trend="↑"
              icon={BarChart3}
            />
            <StatsCard
              label="Monthly Savings"
              value={`$${metrics.monthly_savings_estimate.toFixed(0)}`}
              trend="↑"
              icon={BarChart3}
            />
            <StatsCard
              label="Indexed Agents"
              value={`${metrics.indexed_agents}/${metrics.total_agents}`}
              trend={
                metrics.indexed_agents === metrics.total_agents ? "✓" : "→"
              }
              icon={BarChart3}
            />
          </div>
        ) : null}

        {/* Per-Agent Metrics Table */}
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-[hsl(var(--foreground))]">
              Per-Agent Metrics
            </h2>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-1">
              Compression ratio and memory usage by agent
            </p>
          </div>

          {agentsLoading ? (
            <AgentMetricsSkeleton />
          ) : agentMetrics && agentMetrics.length > 0 ? (
            <div className="rounded-lg border border-[hsl(var(--border))] overflow-hidden">
              <table className="w-full">
                <thead className="bg-[hsl(var(--card))] border-b border-[hsl(var(--border))]">
                  <tr className="text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
                    <th className="px-6 py-3 text-left">Agent</th>
                    <th className="px-6 py-3 text-left">Compression</th>
                    <th className="px-6 py-3 text-left">Tokens Saved</th>
                    <th className="px-6 py-3 text-left">Last Indexed</th>
                    <th className="px-6 py-3 text-left">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[hsl(var(--border))]">
                  {agentMetrics.map((agent) => (
                    <tr
                      key={agent.agent_id}
                      className="hover:bg-[hsl(var(--card)/0.5)] transition-colors"
                    >
                      <td className="px-6 py-4 text-sm font-medium text-[hsl(var(--foreground))]">
                        {agent.display_name || agent.agent_id}
                      </td>
                      <td className="px-6 py-4 text-sm text-[hsl(var(--muted-foreground))]">
                        {(agent.compression_ratio * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 text-sm font-mono text-[hsl(var(--muted-foreground))]">
                        {(agent.tokens_saved / 1000).toFixed(1)}K
                      </td>
                      <td className="px-6 py-4 text-sm text-[hsl(var(--muted-foreground))]">
                        {formatDistanceToNow(new Date(agent.indexed_at), {
                          addSuffix: true,
                        })}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <Badge
                          variant={
                            statusBadgeVariant(agent.status) as
                              | "success"
                              | "warning"
                              | "error"
                              | "secondary"
                          }
                        >
                          {agent.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-8 text-center">
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                No agent metrics available yet. Compression data will appear here
                after agents run.
              </p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  )
}
