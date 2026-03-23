"use client"

import { type LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { Skeleton } from "@/components/ui/skeleton"

interface StatsCardProps {
  icon: LucideIcon
  label: string
  value: number | string
  trend?: {
    value: number
    label?: string
  }
  loading?: boolean
  className?: string
}

export function StatsCard({
  icon: Icon,
  label,
  value,
  trend,
  loading = false,
  className,
}: StatsCardProps) {
  if (loading) {
    return (
      <div
        className={cn(
          "rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 flex flex-col gap-3",
          className
        )}
      >
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-8 rounded-lg" />
        </div>
        <Skeleton className="h-8 w-16" />
        <Skeleton className="h-3 w-20" />
      </div>
    )
  }

  const trendPositive = trend && trend.value >= 0

  return (
    <div
      className={cn(
        "rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 flex flex-col gap-2 hover:border-[hsl(var(--primary)/0.4)] transition-colors",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm text-[hsl(var(--muted-foreground))]">{label}</span>
        <div className="rounded-lg bg-[hsl(var(--primary)/0.1)] p-2">
          <Icon size={16} className="text-[hsl(var(--primary))]" />
        </div>
      </div>
      <div className="text-3xl font-bold text-[hsl(var(--foreground))]">
        {value}
      </div>
      {trend && (
        <div
          className={cn(
            "text-xs font-medium",
            trendPositive ? "text-green-400" : "text-red-400"
          )}
        >
          {trendPositive ? "+" : ""}
          {trend.value}% {trend.label ?? "vs yesterday"}
        </div>
      )}
    </div>
  )
}
