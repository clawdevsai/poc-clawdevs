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

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { format, parseISO } from "date-fns"
import { Skeleton } from "@/components/ui/skeleton"
import type { MetricsPoint } from "@/lib/monitoring-api"

interface UsageChartProps {
  metrics: MetricsPoint[]
  loading?: boolean
  error?: boolean
}

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{ value: number }>
  label?: number
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null
  const labelDate = typeof label === "number" ? new Date(label) : null
  return (
    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--popover))] px-3 py-2 shadow-lg">
      <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">
        {labelDate ? format(labelDate, "d MMM, HH:mm") : "—"}
      </p>
      <p className="text-sm font-semibold text-[hsl(var(--primary))]">
        {payload[0].value} sessões ativas
      </p>
    </div>
  )
}

export function UsageChart({
  metrics,
  loading = false,
  error = false,
}: UsageChartProps) {
  const data = metrics
    .map((metric) => ({
      metricType: metric.metric_type ?? "active_sessions",
      timestamp: parseISO(metric.period_start).getTime(),
      value: Number(metric.value),
    }))
    .filter(
      (metric) =>
        metric.metricType === "active_sessions" &&
        Number.isFinite(metric.timestamp) &&
        Number.isFinite(metric.value)
    )
    .sort((a, b) => a.timestamp - b.timestamp)
    .map((metric) => ({
      timestamp: metric.timestamp,
      value: metric.value,
    }))

  return (
    <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
          Uso de Sessões
        </h3>
        <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
          Sessões ativas, últimas 24 horas (1-min)
        </p>
      </div>
      {loading ? (
        <Skeleton className="h-[220px] w-full" />
      ) : error ? (
        <div className="flex h-[220px] items-center justify-center rounded-lg border border-dashed border-[hsl(var(--border))] text-sm text-[hsl(var(--muted-foreground))]">
          Nao foi possivel carregar os dados de uso.
        </div>
      ) : data.length === 0 ? (
        <div className="flex h-[220px] items-center justify-center rounded-lg border border-dashed border-[hsl(var(--border))] text-sm text-[hsl(var(--muted-foreground))]">
          Sem dados de uso no período selecionado.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -16 }}>
            <defs>
              <linearGradient id="primaryGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.24} />
                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="hsl(var(--border))"
              vertical={false}
            />
            <XAxis
              dataKey="timestamp"
              type="number"
              scale="time"
              domain={["dataMin", "dataMax"]}
              tickFormatter={(value) => format(new Date(value), "HH:mm")}
              minTickGap={42}
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              dy={8}
            />
            <YAxis
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip
              content={<CustomTooltip />}
              cursor={{
                stroke: "hsl(var(--primary))",
                strokeWidth: 1,
                strokeDasharray: "4 4",
              }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              fill="url(#primaryGradient)"
              dot={false}
              activeDot={{ r: 4, fill: "hsl(var(--primary))", strokeWidth: 0 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
