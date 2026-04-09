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
    case "approval.approved":
    case "task_completed":
    case "task.completed":
      return { Icon: CheckCircle, color: "text-green-400" }
    case "approval_rejected":
    case "approval.rejected":
    case "task_failed":
    case "task.failed":
      return { Icon: AlertCircle, color: "text-red-400" }
    case "agent_started":
    case "agent_stopped":
      return { Icon: Bot, color: "text-[hsl(var(--primary))]" }
    case "session_created":
    case "session_ended":
    case "task.queued_to_ceo":
    case "task.sent_to_ceo":
    case "task.forwarded":
    case "task.processing":
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
    <div className="flex h-full flex-col rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7]">
      <div className="border-b border-[hsl(var(--border))] px-4 py-3">
        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">Atividade Recente</h3>
        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">Fluxo de eventos ao vivo</p>
      </div>
      <div className="flex-1 divide-y divide-[hsl(var(--border))] overflow-y-auto px-4">
        {loading ? (
          Array.from({ length: 8 }).map((_, i) => <ActivitySkeleton key={i} />)
        ) : events.length === 0 ? (
          <div className="py-12 flex flex-col items-center justify-center text-center">
            <Activity size={32} className="text-[hsl(var(--muted-foreground))] opacity-20 mb-3" />
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              Nenhuma atividade recente
            </p>
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
