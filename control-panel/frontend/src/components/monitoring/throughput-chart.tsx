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
import type { ThroughputItem } from "@/lib/monitoring-api"

interface ThroughputChartProps {
  items: ThroughputItem[]
  loading?: boolean
  error?: boolean
}

interface TooltipProps {
  active?: boolean
  payload?: Array<{ value: number }>
  label?: string
}

function ThroughputTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--popover))] px-3 py-2 shadow-lg">
      <p className="text-xs text-[hsl(var(--muted-foreground))]">{label}</p>
      <p className="text-sm font-semibold text-[hsl(var(--primary))]">
        {payload[0].value} tasks completadas
      </p>
    </div>
  )
}

export function ThroughputChart({
  items,
  loading = false,
  error = false,
}: ThroughputChartProps) {
  const data = [...items]
    .map((item) => ({
      group: item.group ?? "unlabeled",
      completedCount: Number.isFinite(item.completed_count) ? item.completed_count : 0,
    }))
    .sort((a, b) => b.completedCount - a.completedCount)
    .slice(0, 8)
    .map((item) => ({
      label: item.group || "unlabeled",
      completed: Math.max(0, item.completedCount),
    }))

  return (
    <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
          Throughput by Label
        </h3>
        <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
          Volume de tasks concluídas por categoria
        </p>
      </div>
      {loading ? (
        <Skeleton className="h-[220px] w-full" />
      ) : error ? (
        <div className="flex h-[220px] items-center justify-center rounded-lg border border-dashed border-[hsl(var(--border))] text-sm text-[hsl(var(--muted-foreground))]">
          Nao foi possivel carregar os dados de throughput.
        </div>
      ) : data.length === 0 ? (
        <div className="flex h-[220px] items-center justify-center rounded-lg border border-dashed border-[hsl(var(--border))] text-sm text-[hsl(var(--muted-foreground))]">
          Sem dados de throughput no período selecionado.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data} margin={{ top: 6, right: 8, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
            <XAxis
              dataKey="label"
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              interval={0}
              angle={-15}
              textAnchor="end"
              height={45}
            />
            <YAxis
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip cursor={{ fill: "hsl(var(--muted))/0.3" }} content={<ThroughputTooltip />} />
            <Bar dataKey="completed" radius={[8, 8, 0, 0]} fill="hsl(var(--primary))" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
