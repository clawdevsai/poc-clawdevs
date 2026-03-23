"use client"

import { formatDistanceToNow } from "date-fns"
import { CheckCircle, AlertCircle, Activity, Info, Zap, Bot, Clock } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

interface ActivityEvent {
  id: string
  event_type: string
  description: string
  agent_id?: string | null
  created_at: string
}

interface ActivityFeedProps {
  events: ActivityEvent[]
  loading?: boolean
}

function getEventIcon(event_type: string) {
  switch (event_type) {
    case "approval_approved":
    case "task_completed":
      return { Icon: CheckCircle, color: "text-green-400" }
    case "approval_rejected":
    case "task_failed":
      return { Icon: AlertCircle, color: "text-red-400" }
    case "agent_started":
    case "agent_stopped":
      return { Icon: Bot, color: "text-[hsl(var(--primary))]" }
    case "session_created":
    case "session_ended":
      return { Icon: Zap, color: "text-blue-400" }
    case "cron_triggered":
      return { Icon: Clock, color: "text-purple-400" }
    case "info":
      return { Icon: Info, color: "text-[hsl(var(--muted-foreground))]" }
    default:
      return { Icon: Activity, color: "text-[hsl(var(--muted-foreground))]" }
  }
}

function ActivitySkeleton() {
  return (
    <div className="flex gap-3 py-3 border-b border-[hsl(var(--border))] last:border-0">
      <Skeleton className="h-8 w-8 rounded-full shrink-0" />
      <div className="flex flex-col gap-1.5 flex-1">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-2/3" />
        <Skeleton className="h-2.5 w-16" />
      </div>
    </div>
  )
}

export function ActivityFeed({ events, loading = false }: ActivityFeedProps) {
  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] flex flex-col h-full">
      <div className="px-4 py-3 border-b border-[hsl(var(--border))]">
        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">Recent Activity</h3>
        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">Live event stream</p>
      </div>
      <div className="flex-1 overflow-y-auto px-4 divide-y divide-[hsl(var(--border))]">
        {loading ? (
          Array.from({ length: 8 }).map((_, i) => <ActivitySkeleton key={i} />)
        ) : events.length === 0 ? (
          <div className="py-8 text-center text-sm text-[hsl(var(--muted-foreground))]">
            No recent activity
          </div>
        ) : (
          events.map((event) => {
            const { Icon, color } = getEventIcon(event.event_type)
            return (
              <div key={event.id} className="flex gap-3 py-3">
                <div
                  className={cn(
                    "h-7 w-7 rounded-full flex items-center justify-center shrink-0 mt-0.5",
                    "bg-[hsl(var(--secondary))]"
                  )}
                >
                  <Icon size={13} className={color} />
                </div>
                <div className="flex flex-col gap-0.5 min-w-0 flex-1">
                  <p className="text-xs text-[hsl(var(--foreground))] leading-relaxed line-clamp-2">
                    {event.description}
                  </p>
                  <span className="text-[10px] text-[hsl(var(--muted-foreground))]">
                    {formatDistanceToNow(new Date(event.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
