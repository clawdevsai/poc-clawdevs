"use client"

import { BarChart3, Zap, AlertTriangle, Lightbulb } from "lucide-react"
import { StatsCard } from "@/components/dashboard/stats-card"
import { Skeleton } from "@/components/ui/skeleton"

export interface Phase6MetricsData {
  query_enhancements?: {
    total_queries: number
    avg_expansion_terms: number
    semantic_coverage_improvement: string
  }
  semantic_reranking?: {
    total_reranks: number
    avg_rerank_improvement: string
    latency_p95: string
  }
  adaptive_compression?: Record<string, any>
  intelligent_summarization?: {
    chunks_summarized: number
    avg_reduction: string
    information_preservation: string
  }
  auto_categorization?: {
    chunks_categorized: number
    top_category: string
    categorization_confidence_avg: string
  }
  anomaly_detection?: {
    anomalies_detected: number
    critical_anomalies: number
    compression_skips: number
  }
  context_suggestions?: {
    suggestions_offered: number
    acceptance_rate: string
    avg_relevance_score: string
  }
}

interface Phase6MetricsCardProps {
  data?: Phase6MetricsData
  isLoading: boolean
}

export function Phase6MetricsCards({ data, isLoading }: Phase6MetricsCardProps) {
  if (isLoading) {
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

  if (!data) {
    return (
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-8 text-center">
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No Phase 6 metrics available yet. Queries to Phase 6 endpoints will populate data.
        </p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatsCard
        label="Query Enhancements"
        value={`${data.query_enhancements?.total_queries || 0}`}
        trend={{ value: 18, label: `Coverage +${data.query_enhancements?.semantic_coverage_improvement || "0%"}` }}
        icon={Zap}
      />
      <StatsCard
        label="Semantic Reranking"
        value={`${data.semantic_reranking?.avg_rerank_improvement || "+0%"}`}
        trend={{ value: 12, label: "Relevance improvement" }}
        icon={BarChart3}
      />
      <StatsCard
        label="Anomalies Detected"
        value={`${data.anomaly_detection?.anomalies_detected || 0}`}
        trend={{ value: data.anomaly_detection?.critical_anomalies || 0, label: `${data.anomaly_detection?.compression_skips || 0} skipped` }}
        icon={AlertTriangle}
      />
      <StatsCard
        label="Context Suggestions"
        value={`${data.context_suggestions?.acceptance_rate || "0%"}`}
        trend={{ value: 62, label: "User acceptance" }}
        icon={Lightbulb}
      />
    </div>
  )
}
