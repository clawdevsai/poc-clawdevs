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

import { useEffect, useMemo, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"

import { AppLayout } from "@/components/layout/app-layout"
import { MonitoringTabs, type MonitoringTab } from "@/components/monitoring/monitoring-tabs"
import { MetricsCards } from "@/components/monitoring/metrics-cards"
import { SessionsTable } from "@/components/monitoring/sessions-table"
import { FailurePanel } from "@/components/monitoring/failure-panel"
import { CycleTimeChart } from "@/components/monitoring/cycle-time-chart"
import { ThroughputChart } from "@/components/monitoring/throughput-chart"
import {
  getCycleTime,
  getFailures,
  getOverviewMetrics,
  getThroughput,
  listAgents,
  listSessions,
} from "@/lib/monitoring-api"
import { wsManager } from "@/lib/ws"
import { cn } from "@/lib/utils"

const WINDOW_OPTIONS = [30, 60, 360, 1440]

export default function MonitoringPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<MonitoringTab>("Sessions")
  const [windowMinutes, setWindowMinutes] = useState(30)
  const [showAllSessions, setShowAllSessions] = useState(false)
  const [selectedFailureId, setSelectedFailureId] = useState<string | null>(null)

  const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
    queryKey: ["sessions", showAllSessions ? "all" : windowMinutes],
    queryFn: () =>
      listSessions({ windowMinutes: showAllSessions ? null : windowMinutes }),
  })

  const { data: overview, isLoading: overviewLoading, isError: overviewError } = useQuery({
    queryKey: ["overview", windowMinutes],
    queryFn: () => getOverviewMetrics({ windowMinutes }),
  })

  const { data: cycleTime, isLoading: cycleTimeLoading, isError: cycleTimeError } = useQuery({
    queryKey: ["cycle-time", windowMinutes],
    queryFn: () => getCycleTime({ windowMinutes }),
  })

  const { data: throughput, isLoading: throughputLoading, isError: throughputError } = useQuery({
    queryKey: ["throughput", windowMinutes],
    queryFn: () => getThroughput({ windowMinutes, groupBy: "label" }),
  })

  const { data: failures, isLoading: failuresLoading } = useQuery({
    queryKey: ["failures"],
    queryFn: () => getFailures(),
  })

  const { data: agents, isLoading: agentsLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: () => listAgents(),
  })

  useEffect(() => {
    if (!wsManager) return
    const unsub = wsManager.subscribe("context-mode-metrics", (event: unknown) => {
      const e = event as { type?: string }
      if (e?.type === "context-mode-metrics") {
        queryClient.invalidateQueries({ queryKey: ["overview"] })
        queryClient.invalidateQueries({ queryKey: ["sessions"] })
      }
    })
    return unsub
  }, [queryClient])

  const activeSessions = sessionsData?.total ?? 0
  const tasksInProgress = overview?.tasks_in_progress ?? 0
  const tokensConsumed = overview?.tokens_consumed_total ?? 0
  const failureCount = failures?.total ?? 0

  const throughputItems = throughput?.items ?? []
  const agentItems = agents?.items ?? []

  const cycleAvg = cycleTime?.cycle_time_avg_seconds ?? 0
  const cycleP95 = cycleTime?.cycle_time_p95_seconds ?? 0

  const failuresList = failures?.tasks ?? []
  const selectedFailureTask = failuresList.find((task) => task.id === selectedFailureId)
  const overviewStatsLoading = (overviewLoading && !overview) || overviewError

  const windowLabel = useMemo(() => {
    if (windowMinutes === 30) return "Last 30m"
    if (windowMinutes === 60) return "Last 1h"
    if (windowMinutes === 360) return "Last 6h"
    if (windowMinutes === 1440) return "Last 24h"
    return `Last ${windowMinutes}m`
  }, [windowMinutes])

  return (
    <AppLayout>
      <div className="space-y-6">
        <section className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,2.2fr)_minmax(0,1fr)]">
          <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.65] px-4 py-4 sm:px-5">
            <h1 className="text-xl font-semibold tracking-tight text-[hsl(var(--foreground))]">
              Monitoring Control Panel
            </h1>
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              Real-time operations overview, chart telemetry, and failure visibility.
            </p>
          </div>
          <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.65] px-4 py-4 sm:px-5">
            <p className="text-xs font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
              Active Window
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {WINDOW_OPTIONS.map((opt) => (
                <button
                  key={opt}
                  onClick={() => setWindowMinutes(opt)}
                  className={cn(
                    "rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors",
                    opt === windowMinutes
                      ? "border-[hsl(var(--primary))] bg-[hsl(var(--primary))/0.12] text-[hsl(var(--foreground))]"
                      : "border-[hsl(var(--border))] text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
                  )}
                >
                  {opt === 30
                    ? "30m"
                    : opt === 60
                      ? "1h"
                      : opt === 360
                        ? "6h"
                        : "24h"}
                </button>
              ))}
            </div>
          </div>
        </section>

        <MetricsCards
          activeSessions={activeSessions}
          tasksInProgress={tasksInProgress}
          tokensConsumed={tokensConsumed}
          failures={failureCount}
        />

        <section className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.65] p-2">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <MonitoringTabs active={activeTab} onChange={setActiveTab} />
            <div className="rounded-lg border border-[hsl(var(--border))] px-3 py-1.5 text-xs text-[hsl(var(--muted-foreground))]">
              {showAllSessions ? "All sessions enabled" : `Scope: ${windowLabel}`}
            </div>
          </div>
        </section>

        {activeTab === "Sessions" && (
          <section className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-sm font-semibold text-[hsl(var(--foreground))]">
                  Sessions
                </h2>
                <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
                  Session stream and runtime activity for the selected time scope.
                </p>
              </div>
              <button
                onClick={() => setShowAllSessions((prev) => !prev)}
                className="rounded-lg border border-[hsl(var(--border))] px-3 py-1.5 text-xs font-medium text-[hsl(var(--primary))] transition-colors hover:bg-[hsl(var(--primary))/0.1]"
              >
                {showAllSessions ? "Show recent" : "Show all"}
              </button>
            </div>
            <SessionsTable items={sessionsData?.items ?? []} isLoading={sessionsLoading} />
          </section>
        )}

        {activeTab === "Tasks" && (
          <section className="space-y-4">
            <div className="grid min-w-0 grid-cols-1 gap-4 xl:grid-cols-5">
              <div className="min-w-0 xl:col-span-3">
                <CycleTimeChart
                  averageSeconds={cycleAvg}
                  p95Seconds={cycleP95}
                  loading={cycleTimeLoading}
                  error={cycleTimeError}
                />
              </div>
              <div className="min-w-0 xl:col-span-2">
                <ThroughputChart
                  items={throughputItems}
                  loading={throughputLoading}
                  error={throughputError}
                />
              </div>
            </div>

            <div className="grid min-w-0 grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
              <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-4">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
                    Failures
                  </h3>
                  {!failuresLoading && (
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      {failuresList.length} entries
                    </span>
                  )}
                </div>
                <div className="space-y-2">
                  {failuresLoading ? (
                    <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading failures...</p>
                  ) : failuresList.length === 0 ? (
                    <p className="text-sm text-[hsl(var(--muted-foreground))]">
                      No failures detected in the current window.
                    </p>
                  ) : (
                    failuresList.map((task) => (
                      <button
                        key={task.id}
                        onClick={() => setSelectedFailureId(task.id)}
                        className={cn(
                          "w-full rounded-xl border px-3 py-2 text-left transition-colors",
                          selectedFailureId === task.id
                            ? "border-red-500/40 bg-red-500/10 text-[hsl(var(--foreground))]"
                            : "border-[hsl(var(--border))] text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/30 hover:text-[hsl(var(--foreground))]"
                        )}
                      >
                        <div className="flex items-center justify-between gap-3">
                          <span className="truncate">{task.title}</span>
                          <span className="shrink-0 text-xs font-medium">{task.failure_count}x</span>
                        </div>
                        <p className="mt-1 truncate text-xs opacity-80">
                          {task.last_error ?? "No error recorded"}
                        </p>
                      </button>
                    ))
                  )}
                </div>
              </div>
              <FailurePanel taskId={selectedFailureTask?.id ?? null} />
            </div>
          </section>
        )}

        {activeTab === "Agents" && (
          <section className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
                Agents
              </h3>
              {!agentsLoading && (
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {agentItems.length} active entries
                </span>
              )}
            </div>
            <div className="space-y-2 text-sm">
              {agentsLoading ? (
                <p className="text-[hsl(var(--muted-foreground))]">Loading agents...</p>
              ) : agentItems.length === 0 ? (
                <p className="text-[hsl(var(--muted-foreground))]">No agents available.</p>
              ) : (
                agentItems.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between border-b border-[hsl(var(--border))] pb-2"
                  >
                    <span className="text-[hsl(var(--foreground))]">{agent.display_name}</span>
                    <span className="text-[hsl(var(--muted-foreground))]">{agent.status}</span>
                  </div>
                ))
              )}
            </div>
          </section>
        )}

        {activeTab === "Metrics" && (
          <section className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] px-4 py-4">
              <p className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                Tokens avg per task
              </p>
              <p className="mt-3 text-2xl font-semibold text-[hsl(var(--foreground))]">
                {overviewStatsLoading ? "—" : overview?.tokens_consumed_avg_per_task?.toFixed(1) ?? "0"}
              </p>
            </div>
            <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] px-4 py-4">
              <p className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                Backlog count
              </p>
              <p className="mt-3 text-2xl font-semibold text-[hsl(var(--foreground))]">
                {overviewStatsLoading ? "—" : overview?.backlog_count ?? 0}
              </p>
            </div>
            <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] px-4 py-4">
              <p className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                Tasks completed
              </p>
              <p className="mt-3 text-2xl font-semibold text-[hsl(var(--foreground))]">
                {overviewStatsLoading ? "—" : overview?.tasks_completed ?? 0}
              </p>
            </div>
            <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] px-4 py-4">
              <p className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                Tasks in review
              </p>
              <p className="mt-3 text-2xl font-semibold text-[hsl(var(--foreground))]">
                {overviewStatsLoading ? "—" : overview?.open_tasks ?? 0}
              </p>
            </div>
          </section>
        )}
      </div>
    </AppLayout>
  )
}
