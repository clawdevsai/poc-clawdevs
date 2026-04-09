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
          "rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-5 flex flex-col gap-3",
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
        "rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-5 flex flex-col gap-2 hover:border-[hsl(var(--primary)/0.4)] transition-colors",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm text-[hsl(var(--muted-foreground))]">{label}</span>
        <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--secondary))/0.8] p-2">
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
            trendPositive ? "text-emerald-600" : "text-rose-600"
          )}
        >
          {trendPositive ? "+" : ""}
          {trend.value}% {trend.label ?? "vs ontem"}
        </div>
      )}
    </div>
  )
}
