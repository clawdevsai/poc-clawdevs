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

import Link from "next/link"
import { formatDistanceToNow } from "date-fns"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { AgentAvatar } from "@/components/agents/agent-avatar"
import { cn } from "@/lib/utils"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

interface Agent {
  id: string
  slug: string
  display_name: string
  role: string
  avatar_url?: string | null
  status: "online" | "idle" | "offline" | string
  runtime_status?: "online" | "working" | "idle" | "offline" | string | null
  model?: string | null
  current_model?: string | null
  last_heartbeat?: string | null
  last_heartbeat_at?: string | null
}

interface AgentsGridProps {
  agents: Agent[]
  loading?: boolean
}

function statusBadgeVariant(status: string) {
  switch (status) {
    case "online":
    case "working":
      return "success"
    case "idle":
      return "warning"
    case "error":
      return "error"
    case "stopped":
      return "secondary"
    default:
      return "secondary"
  }
}

function AgentCardSkeleton() {
  return (
    <div className="flex min-w-0 flex-col gap-3 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-4">
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
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <AgentCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {agents.map((agent) => {
        const effectiveStatus = (agent.runtime_status ?? agent.status) as string
        return (
          <Link
            key={agent.id}
            href={`/agents/${agent.slug}`}
            className="group flex min-w-0 flex-col gap-3 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-4 transition-colors hover:border-[hsl(var(--primary)/0.4)] hover:bg-[hsl(var(--card))/0.85]"
          >
            <div className="flex min-w-0 items-center gap-3">
              <AgentAvatar
                slug={agent.slug}
                displayName={agent.display_name}
                avatarUrl={agent.avatar_url}
                size="md"
              />
              <div className="flex min-w-0 flex-1 flex-col gap-0.5">
                <span className="truncate text-sm font-semibold text-[hsl(var(--foreground))] transition-colors group-hover:text-[hsl(var(--primary))]">
                  {agent.display_name}
                </span>
                <span className="truncate text-xs text-[hsl(var(--muted-foreground))]">
                  {agent.role}
                </span>
              </div>
              <Badge variant={statusBadgeVariant(effectiveStatus) as "success" | "warning" | "error" | "secondary"}>
                <span
                  className={cn(
                    "mr-1 inline-block h-1.5 w-1.5 rounded-full",
                    effectiveStatus === "online" || effectiveStatus === "working"
                      ? "bg-emerald-500"
                      : effectiveStatus === "idle"
                        ? "bg-amber-500"
                        : effectiveStatus === "error"
                          ? "bg-rose-500"
                          : "bg-white/30"
                  )}
                />
                {effectiveStatus}
              </Badge>
            </div>
            <div className="flex items-center justify-between text-xs text-[hsl(var(--muted-foreground))]">
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="max-w-[120px] truncate font-mono">
                    {agent.model ?? agent.current_model ?? "—"}
                  </span>
                </TooltipTrigger>
                {(agent.model ?? agent.current_model) && (
                  <TooltipContent>
                    Modelo: {agent.model ?? agent.current_model}
                  </TooltipContent>
                )}
              </Tooltip>
              <span>
                {(agent.last_heartbeat ?? agent.last_heartbeat_at)
                  ? formatDistanceToNow(new Date((agent.last_heartbeat ?? agent.last_heartbeat_at) as string), { addSuffix: true })
                  : "sem heartbeat"}
              </span>
            </div>
          </Link>
        )
      })}
    </div>
  )
}
