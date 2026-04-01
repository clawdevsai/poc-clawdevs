/*
 * Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
 */

"use client"

import { useQuery } from "@tanstack/react-query"
import { AlertCircle, CheckCircle, Clock } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { customInstance } from "@/lib/axios-instance"
import { formatDistanceToNow } from "date-fns"

interface CronJobMetric {
  job_name: string
  status: "healthy" | "warning" | "error"
  last_execution: string
  execution_count: number
  average_duration_ms: number
  last_error?: string
}

const fetchCronMetrics = () =>
  customInstance<CronJobMetric[]>({
    url: "/context-mode/cron-metrics",
    method: "GET",
  })

function getStatusIcon(status: string) {
  switch (status) {
    case "healthy":
      return <CheckCircle className="h-4 w-4 text-green-500" />
    case "warning":
      return <Clock className="h-4 w-4 text-yellow-500" />
    case "error":
      return <AlertCircle className="h-4 w-4 text-red-500" />
    default:
      return null
  }
}

function getStatusVariant(status: string) {
  switch (status) {
    case "healthy":
      return "success"
    case "warning":
      return "warning"
    case "error":
      return "error"
    default:
      return "secondary"
  }
}

export function CronHealth() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["context-mode", "cron-metrics"],
    queryFn: fetchCronMetrics,
    retry: false,
    refetchInterval: 300000, // Refetch every 5 minutes
  })

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full rounded-lg" />
        ))}
      </div>
    )
  }

  if (isError || !data || data.length === 0) {
    return (
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 text-center">
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No cron job metrics available.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
        Cron Job Health
      </h3>
      {data.map((job) => (
        <div
          key={job.job_name}
          className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex items-center gap-4"
        >
          <div className="flex-shrink-0">{getStatusIcon(job.status)}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-[hsl(var(--foreground))] truncate">
              {job.job_name}
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              Last run:{" "}
              {formatDistanceToNow(new Date(job.last_execution), {
                addSuffix: true,
              })}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-[hsl(var(--muted-foreground))]">
              {job.average_duration_ms}ms
            </span>
            <Badge
              variant={
                getStatusVariant(job.status) as
                  | "success"
                  | "warning"
                  | "error"
                  | "secondary"
              }
            >
              {job.status}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  )
}
