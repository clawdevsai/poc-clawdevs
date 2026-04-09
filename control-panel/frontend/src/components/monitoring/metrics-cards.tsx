interface MetricsCardsProps {
  activeSessions: number
  tasksInProgress: number
  tokensConsumed: number
  failures: number
}

const cardBase =
  "rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] px-4 py-4 sm:px-5"

export function MetricsCards({
  activeSessions,
  tasksInProgress,
  tokensConsumed,
  failures,
}: MetricsCardsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div className={cardBase}>
        <span className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
          Active sessions
        </span>
        <span className="mt-3 text-2xl font-semibold text-[hsl(var(--foreground))]">
          {activeSessions}
        </span>
      </div>
      <div className={cardBase}>
        <span className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
          Tasks in progress
        </span>
        <span className="mt-3 text-2xl font-semibold text-[hsl(var(--foreground))]">
          {tasksInProgress}
        </span>
      </div>
      <div className={cardBase}>
        <span className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
          Tokens consumed
        </span>
        <span className="mt-3 text-2xl font-semibold text-[hsl(var(--foreground))]">
          {tokensConsumed.toLocaleString()}
        </span>
      </div>
      <div className={cardBase}>
        <span className="text-[11px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
          Failures
        </span>
        <span className="mt-3 text-2xl font-semibold text-red-500">
          {failures}
        </span>
      </div>
    </div>
  )
}
