"use client"

import { useQuery } from "@tanstack/react-query"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { customInstance } from "@/lib/axios-instance"
import { AlertCircle, CheckCircle2 } from "lucide-react"

interface OllamaHealthResponse {
  status: "active" | "unavailable"
  model: string
  online: boolean
  vram_used?: number
  vram_total?: number
  avg_latency_ms?: number
}

const fetchOllamaHealth = () =>
  customInstance<OllamaHealthResponse>({
    url: "/context-mode/phase6/ollama-health",
    method: "GET",
  })

export function OllamaHealthCard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["ollama", "health"],
    queryFn: fetchOllamaHealth,
    retry: false,
    refetchInterval: 30000, // Check every 30s
  })

  if (isLoading) {
    return (
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 space-y-3">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-32" />
      </div>
    )
  }

  const isOnline = data?.status === "active" && data?.online
  const statusIcon = isOnline ? CheckCircle2 : AlertCircle
  const StatusIcon = statusIcon

  return (
    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4">
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-[hsl(var(--foreground))]">
            Ollama (phi4-mini-reasoning)
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <StatusIcon
            className={`h-5 w-5 ${
              isOnline ? "text-green-500" : "text-red-500"
            }`}
          />
          <Badge
            variant={isOnline ? "success" : "error"}
            className="text-xs"
          >
            {data?.status || "unknown"}
          </Badge>
        </div>

        {data && (
          <div className="space-y-1 text-sm text-[hsl(var(--muted-foreground))]">
            <p>Model: <span className="font-mono text-xs">{data.model}</span></p>
            {data.vram_used !== undefined && data.vram_total !== undefined && (
              <p>
                VRAM: {data.vram_used}MB / {data.vram_total}MB
              </p>
            )}
            {data.avg_latency_ms !== undefined && (
              <p>Avg Latency: {data.avg_latency_ms}ms</p>
            )}
          </div>
        )}

        {error && (
          <p className="text-xs text-[hsl(var(--destructive))]">
            Unable to check Ollama health
          </p>
        )}
      </div>
    </div>
  )
}
