"use client"

import Link from "next/link"
import { formatDistanceToNow } from "date-fns"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

interface Agent {
  id: string
  slug: string
  display_name: string
  role: string
  status: "online" | "idle" | "offline" | string
  model: string
  last_heartbeat?: string | null
}

interface AgentsGridProps {
  agents: Agent[]
  loading?: boolean
}

function getInitials(name: string): string {
  return name
    .split(/[\s_-]+/)
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

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
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-3 w-16" />
        </div>
        <Skeleton className="h-5 w-14 rounded-full" />
      </div>
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-3 w-16" />
      </div>
    </div>
  )
}

export function AgentsGrid({ agents, loading = false }: AgentsGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <AgentCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
      {agents.map((agent) => (
        <Link
          key={agent.id}
          href={`/agents/${agent.slug}`}
          className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3 hover:border-[hsl(var(--primary)/0.4)] hover:bg-[hsl(var(--card))/0.8] transition-colors group"
        >
          <div className="flex items-center gap-3">
            {/* Avatar */}
            <div className="h-10 w-10 rounded-full bg-[hsl(var(--primary)/0.15)] border border-[hsl(var(--primary)/0.3)] flex items-center justify-center shrink-0">
              <span className="text-xs font-bold text-[hsl(var(--primary))]">
                {getInitials(agent.display_name)}
              </span>
            </div>
            <div className="flex flex-col gap-0.5 flex-1 min-w-0">
              <span className="text-sm font-semibold text-[hsl(var(--foreground))] truncate group-hover:text-[hsl(var(--primary))] transition-colors">
                {agent.display_name}
              </span>
              <span className="text-xs text-[hsl(var(--muted-foreground))] truncate">
                {agent.role}
              </span>
            </div>
            <Badge variant={statusBadgeVariant(agent.status) as "success" | "warning" | "secondary"}>
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
          <div className="flex items-center justify-between text-xs text-[hsl(var(--muted-foreground))]">
            <span className="font-mono truncate max-w-[120px]" title={agent.model}>
              {agent.model}
            </span>
            <span>
              {agent.last_heartbeat
                ? formatDistanceToNow(new Date(agent.last_heartbeat), { addSuffix: true })
                : "no heartbeat"}
            </span>
          </div>
        </Link>
      ))}
    </div>
  )
}
