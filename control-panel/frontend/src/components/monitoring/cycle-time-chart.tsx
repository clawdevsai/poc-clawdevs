import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Skeleton } from "@/components/ui/skeleton"

interface CycleTimeChartProps {
  averageSeconds: number
  p95Seconds: number
  loading?: boolean
  error?: boolean
}

interface TooltipProps {
  active?: boolean
  payload?: Array<{ value: number }>
  label?: string
}

function CycleTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--popover))] px-3 py-2 shadow-lg">
      <p className="text-xs text-[hsl(var(--muted-foreground))]">{label}</p>
      <p className="text-sm font-semibold text-[hsl(var(--primary))]">
        {payload[0].value}s
      </p>
    </div>
  )
}

export function CycleTimeChart({
  averageSeconds,
  p95Seconds,
  loading = false,
  error = false,
}: CycleTimeChartProps) {
  const averageValue = Number.isFinite(averageSeconds) ? Math.max(0, Math.round(averageSeconds)) : 0
  const p95Value = Number.isFinite(p95Seconds) ? Math.max(0, Math.round(p95Seconds)) : 0
  const data = [
    { name: "Average", value: averageValue },
    { name: "P95", value: p95Value },
  ].filter((entry) => entry.value > 0)

  return (
    <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
          Cycle Time
        </h3>
        <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
          Latência média e percentil p95 por task
        </p>
      </div>
      <div className="mb-4 grid grid-cols-2 gap-2">
        <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--muted))]/20 px-3 py-2">
          <p className="text-[10px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
            Average
          </p>
          <p className="mt-1 text-sm font-semibold text-[hsl(var(--foreground))]">
            {averageValue > 0 ? `${averageValue}s` : "—"}
          </p>
        </div>
        <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--muted))]/20 px-3 py-2">
          <p className="text-[10px] font-medium uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
            P95
          </p>
          <p className="mt-1 text-sm font-semibold text-[hsl(var(--foreground))]">
            {p95Value > 0 ? `${p95Value}s` : "—"}
          </p>
        </div>
      </div>
      {loading ? (
        <Skeleton className="h-[220px] w-full" />
      ) : error ? (
        <div className="flex h-[220px] items-center justify-center rounded-lg border border-dashed border-[hsl(var(--border))] text-sm text-[hsl(var(--muted-foreground))]">
          Nao foi possivel carregar os dados de cycle time.
        </div>
      ) : data.length === 0 ? (
        <div className="flex h-[220px] items-center justify-center rounded-lg border border-dashed border-[hsl(var(--border))] text-sm text-[hsl(var(--muted-foreground))]">
          Sem dados de cycle time no período selecionado.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data} margin={{ top: 6, right: 8, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
            <XAxis
              dataKey="name"
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip cursor={{ fill: "hsl(var(--muted))/0.3" }} content={<CycleTooltip />} />
            <Bar dataKey="value" radius={[8, 8, 0, 0]} fill="hsl(var(--primary))" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
