import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { getFailureDetail } from "@/lib/monitoring-api"

interface FailurePanelProps {
  taskId: string | null
}

export function FailurePanel({ taskId }: FailurePanelProps) {
  const [expanded, setExpanded] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ["failure-detail", taskId],
    queryFn: () => (taskId ? getFailureDetail(taskId) : Promise.resolve(null)),
    enabled: Boolean(taskId),
  })

  if (!taskId) {
    return (
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-5 text-sm text-[hsl(var(--muted-foreground))]">
        Select a failed task to inspect details.
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-5 text-sm text-[hsl(var(--muted-foreground))]">
        Loading failure detail...
      </div>
    )
  }

  const message = data?.message ?? "No failure message recorded."

  return (
    <div className="space-y-4 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-5">
      <div>
        <p className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
          Failure message
        </p>
        <p className="mt-2 text-[16px] text-[hsl(var(--foreground))]">{message}</p>
      </div>
      <button
        onClick={() => setExpanded((prev) => !prev)}
        className="text-[13px] font-medium text-[hsl(var(--primary))] hover:opacity-90"
      >
        {expanded ? "Hide details" : "Show stack trace & evidence"}
      </button>
      {expanded && (
        <div className="space-y-3">
          <div>
            <p className="text-[12px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
              Stack trace
            </p>
            <pre className="mt-2 whitespace-pre-wrap rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30 p-3 text-[13px] text-[hsl(var(--foreground))]">
              {data?.stack_trace ?? "No stack trace captured."}
            </pre>
          </div>
          <div>
            <p className="text-[12px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
              Evidence
            </p>
            <ul className="mt-2 space-y-1 text-[14px] text-[hsl(var(--foreground))]">
              {data?.evidence?.length ? (
                data.evidence.map((item, idx) => <li key={idx}>{item}</li>)
              ) : (
                <li className="text-[hsl(var(--muted-foreground))]">
                  No evidence attached.
                </li>
              )}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
