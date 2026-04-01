"use client"

import { Skeleton } from "@/components/ui/skeleton"

interface Phase6DetailRow {
  task: string
  metric: string
  value: string | number
}

interface Phase6DetailsTableProps {
  data?: Record<string, any>
  isLoading: boolean
}

export function Phase6DetailsTable({ data, isLoading }: Phase6DetailsTableProps) {
  const details: Phase6DetailRow[] = [
    {
      task: "Query Enhancement",
      metric: "Avg Expansion Terms",
      value: data?.query_enhancements?.avg_expansion_terms || 0,
    },
    {
      task: "Semantic Reranking",
      metric: "Latency (p95)",
      value: data?.semantic_reranking?.latency_p95 || "0ms",
    },
    {
      task: "Intelligent Summarization",
      metric: "Avg Reduction",
      value: data?.intelligent_summarization?.avg_reduction || "0%",
    },
    {
      task: "Intelligent Summarization",
      metric: "Info Preservation",
      value: data?.intelligent_summarization?.information_preservation || "0%",
    },
    {
      task: "Auto-Categorization",
      metric: "Chunks Categorized",
      value: data?.auto_categorization?.chunks_categorized || 0,
    },
    {
      task: "Auto-Categorization",
      metric: "Confidence Avg",
      value: data?.auto_categorization?.categorization_confidence_avg || "0%",
    },
    {
      task: "Context Suggestions",
      metric: "Avg Relevance",
      value: data?.context_suggestions?.avg_relevance_score || "0.0",
    },
  ]

  if (isLoading) {
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
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="border border-[hsl(var(--border))] rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.5)]">
            <th className="px-4 py-2 text-left font-medium text-[hsl(var(--foreground))]">
              Task
            </th>
            <th className="px-4 py-2 text-left font-medium text-[hsl(var(--foreground))]">
              Metric
            </th>
            <th className="px-4 py-2 text-left font-medium text-[hsl(var(--foreground))]">
              Value
            </th>
          </tr>
        </thead>
        <tbody>
          {details.map((row, idx) => (
            <tr
              key={idx}
              className="border-b border-[hsl(var(--border))] hover:bg-[hsl(var(--muted)/0.3)] transition-colors"
            >
              <td className="px-4 py-2 text-[hsl(var(--foreground))]">
                {row.task}
              </td>
              <td className="px-4 py-2 text-[hsl(var(--muted-foreground))]">
                {row.metric}
              </td>
              <td className="px-4 py-2 font-semibold text-[hsl(var(--foreground))]">
                {row.value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
