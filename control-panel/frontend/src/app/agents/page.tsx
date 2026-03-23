"use client"

import { useEffect, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { formatDistanceToNow } from "date-fns"
import Link from "next/link"
import { Search } from "lucide-react"
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
  status: "online" | "idle" | "offline" | string
  model: string
  last_heartbeat?: string | null
  cron_expression?: string | null
  cron_status?: string | null
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
}

// ---- Fetchers -------------------------------------------------------------

const fetchAgents = () =>
  customInstance<PaginatedResponse<Agent>>({ url: "/agents", method: "GET" })

// ---- Sub-components -------------------------------------------------------

function statusBadgeVariant(status: string) {
  switch (status) {
    case "online":
      return "success"
    case "idle":
      return "warning"
    default:
      return "secondary"
  }
}

function AgentCardSkeleton() {
  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-full" />
        <div className="flex flex-col gap-1.5 flex-1">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-3 w-20" />
        </div>
        <Skeleton className="h-5 w-16 rounded-full" />
      </div>
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-32" />
        <Skeleton className="h-3 w-20" />
      </div>
    </div>
  )
}

function EmptyState({ query }: { query: string }) {
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-20 gap-3">
      <div className="h-12 w-12 rounded-full bg-[hsl(var(--muted))] flex items-center justify-center">
        <Search className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
      </div>
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        {query
          ? `No agents matching "${query}"`
          : "No agents found"}
      </p>
    </div>
  )
}

// ---- Page -----------------------------------------------------------------

export default function AgentsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")

  const { data, isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  })

  // Live-update via WebSocket "agents" channel
  useEffect(() => {
    if (!wsManager) return
    const unsub = wsManager.subscribe("agents", () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] })
    })
    return unsub
  }, [queryClient])

  const agents = data?.items ?? []
  const filtered = search.trim()
    ? agents.filter((a) =>
        a.display_name.toLowerCase().includes(search.toLowerCase()) ||
        a.slug.toLowerCase().includes(search.toLowerCase())
      )
    : agents

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
              Agents
            </h1>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
              {isLoading
                ? "Loading..."
                : `${agents.length} agent${agents.length !== 1 ? "s" : ""} registered`}
            </p>
          </div>

          {/* Search */}
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--muted-foreground))]" />
            <input
              type="text"
              placeholder="Search agents…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] pl-9 pr-3 py-2 text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] outline-none focus:border-[hsl(var(--primary))] transition-colors"
            />
          </div>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
          {isLoading ? (
            Array.from({ length: 9 }).map((_, i) => (
              <AgentCardSkeleton key={i} />
            ))
          ) : filtered.length === 0 ? (
            <EmptyState query={search} />
          ) : (
            filtered.map((agent) => (
              <Link
                key={agent.id}
                href={`/agents/${agent.slug}`}
                className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3 hover:border-[hsl(var(--primary)/0.4)] hover:bg-[hsl(var(--card)/0.8)] transition-colors group"
              >
                {/* Top row: avatar + name + status */}
                <div className="flex items-center gap-3">
                  <AgentAvatar
                    slug={agent.slug}
                    displayName={agent.display_name}
                    size="md"
                  />
                  <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                    <span className="text-sm font-semibold text-[hsl(var(--foreground))] truncate group-hover:text-[hsl(var(--primary))] transition-colors">
                      {agent.display_name}
                    </span>
                    <span className="text-xs text-[hsl(var(--muted-foreground))] truncate">
                      {agent.role}
                    </span>
                  </div>
                  <Badge
                    variant={
                      statusBadgeVariant(agent.status) as
                        | "success"
                        | "warning"
                        | "secondary"
                    }
                  >
                    <span
                      className={cn(
                        "mr-1 h-1.5 w-1.5 rounded-full inline-block",
                        agent.status === "online"
                          ? "bg-green-400"
                          : agent.status === "idle"
                          ? "bg-yellow-400"
                          : "bg-white/30"
                      )}
                    />
                    {agent.status}
                  </Badge>
                </div>

                {/* Bottom row: model + last seen */}
                <div className="flex items-center justify-between text-xs text-[hsl(var(--muted-foreground))]">
                  <span
                    className="font-mono truncate max-w-[140px]"
                    title={agent.model}
                  >
                    {agent.model}
                  </span>
                  <span>
                    {agent.last_heartbeat
                      ? formatDistanceToNow(new Date(agent.last_heartbeat), {
                          addSuffix: true,
                        })
                      : "no heartbeat"}
                  </span>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </AppLayout>
  )
}
