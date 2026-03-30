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

interface Metric {
  metric_type: string
  value: number
  period_start: string
}

interface UsageChartProps {
  metrics: Metric[]
  loading?: boolean
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

export function UsageChart({ metrics, loading = false }: UsageChartProps) {
  const data = metrics.map((m) => ({
    timestamp: parseISO(m.period_start).getTime(),
    value: m.value,
  }))

  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">Uso de Sessões</h3>
        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">Sessões ativas, últimas 24 horas (1-min)</p>
      </div>
      {loading ? (
        <Skeleton className="h-48 w-full" />
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -16 }}>
            <defs>
              <linearGradient id="primaryGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(195 100% 50%)" stopOpacity={0.25} />
                <stop offset="95%" stopColor="hsl(195 100% 50%)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="hsl(0 0% 16%)"
              vertical={false}
            />
            <XAxis
              dataKey="timestamp"
              type="number"
              scale="time"
              domain={["dataMin", "dataMax"]}
              tickFormatter={(value) => format(new Date(value), "HH:mm")}
              minTickGap={42}
              tick={{ fill: "hsl(0 0% 55%)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              dy={8}
            />
            <YAxis
              tick={{ fill: "hsl(0 0% 55%)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: "hsl(195 100% 50%)", strokeWidth: 1, strokeDasharray: "4 4" }} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="hsl(195 100% 50%)"
              strokeWidth={2}
              fill="url(#primaryGradient)"
              dot={false}
              activeDot={{ r: 4, fill: "hsl(195 100% 50%)", strokeWidth: 0 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
