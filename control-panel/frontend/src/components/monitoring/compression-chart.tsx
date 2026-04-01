/*
 * Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
 */

"use client"

import { useQuery } from "@tanstack/react-query"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Skeleton } from "@/components/ui/skeleton"
import { customInstance } from "@/lib/axios-instance"

interface CompressionDataPoint {
  timestamp: string
  compression_rate: number
  tokens_saved: number
}

const fetchCompressionHistory = () =>
  customInstance<CompressionDataPoint[]>({
    url: "/context-mode/metrics/history?days=30",
    method: "GET",
  })

export function CompressionChart() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["context-mode", "compression-history"],
    queryFn: fetchCompressionHistory,
    retry: false,
    refetchInterval: 3600000, // Refetch every hour
  })

  if (isLoading) {
    return (
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
        <Skeleton className="h-80 w-full" />
      </div>
    )
  }

  if (isError || !data || data.length === 0) {
    return (
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 text-center">
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No compression history available. Check back after agents run.
        </p>
      </div>
    )
  }

  const chartData = data.map((point) => ({
    date: new Date(point.timestamp).toLocaleDateString(),
    rate: Math.round(point.compression_rate * 100),
    saved: Math.round(point.tokens_saved / 1000),
  }))

  return (
    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
      <h3 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-6">
        Compression Rate (Last 30 Days)
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="hsl(var(--border))"
          />
          <XAxis
            dataKey="date"
            stroke="hsl(var(--muted-foreground))"
            style={{ fontSize: "12px" }}
          />
          <YAxis
            stroke="hsl(var(--muted-foreground))"
            style={{ fontSize: "12px" }}
            label={{ value: "Rate (%)", angle: -90, position: "insideLeft" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              color: "hsl(var(--foreground))",
            }}
            formatter={(value: any) => value ? `${value}%` : "-"}
          />
          <Line
            type="monotone"
            dataKey="rate"
            stroke="hsl(var(--primary))"
            dot={false}
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
