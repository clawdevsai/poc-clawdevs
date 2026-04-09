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

import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

interface TaskHealthData {
  healthy: number
  blocked: number
  stalled: number
  failed: number
}

interface TaskHealthProps {
  data?: TaskHealthData
  loading: boolean
}

export function TaskHealth({ data, loading }: TaskHealthProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-4">
        <Skeleton className="h-5 w-32 mb-4" />
        <div className="grid grid-cols-2 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
    )
  }

  const { healthy = 0, blocked = 0, stalled = 0, failed = 0 } = data || {}
  const total = healthy + blocked + stalled + failed

  return (
    <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-4">
      <h2 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-4">
        Saúde das Tarefas
      </h2>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex items-center gap-3 rounded-lg border border-emerald-500/25 bg-emerald-500/10 p-3">
          <CheckCircle className="h-5 w-5 text-emerald-500" />
          <div>
            <p className="text-lg font-semibold text-green-500">{healthy}</p>
            <p className="text-xs text-green-500/70">Saudável</p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-lg border border-amber-500/25 bg-amber-500/10 p-3">
          <Clock className="h-5 w-5 text-amber-500" />
          <div>
            <p className="text-lg font-semibold text-yellow-500">{stalled}</p>
            <p className="text-xs text-yellow-500/70">Paralisada</p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-lg border border-rose-500/25 bg-rose-500/10 p-3">
          <XCircle className="h-5 w-5 text-rose-500" />
          <div>
            <p className="text-lg font-semibold text-red-500">{failed}</p>
            <p className="text-xs text-red-500/70">Falhou</p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-lg border border-orange-500/25 bg-orange-500/10 p-3">
          <AlertTriangle className="h-5 w-5 text-orange-500" />
          <div>
            <p className="text-lg font-semibold text-orange-500">{blocked}</p>
            <p className="text-xs text-orange-500/70">Bloqueada</p>
          </div>
        </div>
      </div>
      {total > 0 && (
        <div className="mt-3 pt-3 border-t border-[hsl(var(--border))]">
          <div className="h-2 rounded-full bg-[hsl(var(--muted))] overflow-hidden flex">
            <div 
              className="h-full bg-green-500" 
              style={{ width: `${(healthy / total) * 100}%` }}
            />
            <div 
              className="h-full bg-yellow-500" 
              style={{ width: `${(stalled / total) * 100}%` }}
            />
            <div 
              className="h-full bg-red-500" 
              style={{ width: `${(failed / total) * 100}%` }}
            />
            <div 
              className="h-full bg-orange-500" 
              style={{ width: `${(blocked / total) * 100}%` }}
            />
          </div>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mt-2">
            {total} tarefas no total
          </p>
        </div>
      )}
    </div>
  )
}
