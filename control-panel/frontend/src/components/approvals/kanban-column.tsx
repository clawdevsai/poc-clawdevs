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

import { Skeleton } from "@/components/ui/skeleton"
import { ApprovalCard } from "./approval-card"
import type { Approval } from "./types"

interface KanbanColumnProps {
  title: string
  approvals: Approval[]
  loading?: boolean
  onApprove?: (approval: Approval) => void
  onReject?: (approval: Approval) => void
  accentColor?: string
}

function CardSkeleton() {
  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <Skeleton className="h-8 w-8 rounded-full shrink-0" />
        <div className="flex flex-col gap-1.5 flex-1">
          <Skeleton className="h-3.5 w-28" />
          <Skeleton className="h-3 w-20" />
        </div>
      </div>
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <div className="flex justify-between items-center">
        <Skeleton className="h-3 w-16" />
        <div className="flex gap-1.5">
          <Skeleton className="h-6 w-12 rounded-md" />
          <Skeleton className="h-6 w-14 rounded-md" />
        </div>
      </div>
    </div>
  )
}

function EmptyState({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-2">
      <div className="h-10 w-10 rounded-full bg-white/5 flex items-center justify-center">
        <span className="text-lg">—</span>
      </div>
      <p className="text-xs text-[hsl(var(--muted-foreground))] text-center">
        Nenhuma solicitação de {title.toLowerCase()}
      </p>
    </div>
  )
}

export function KanbanColumn({
  title,
  approvals,
  loading = false,
  onApprove,
  onReject,
  accentColor,
}: KanbanColumnProps) {
  return (
    <div className="flex flex-col min-w-0 flex-1">
      {/* Column header */}
      <div className="flex items-center gap-2 mb-3">
        <h2
          className="text-sm font-semibold"
          style={{ color: accentColor ?? "hsl(var(--foreground))" }}
        >
          {title}
        </h2>
        {!loading && (
          <span
            className="inline-flex items-center justify-center rounded-full px-2 py-0.5 text-xs font-medium"
            style={{
              backgroundColor: accentColor ? `${accentColor}1A` : "hsl(var(--muted))",
              color: accentColor ?? "hsl(var(--muted-foreground))",
              border: accentColor ? `1px solid ${accentColor}33` : undefined,
            }}
          >
            {approvals.length}
          </span>
        )}
      </div>

      {/* Column body — scrollable */}
      <div className="flex flex-col gap-2 overflow-y-auto max-h-[calc(100vh-240px)] pr-0.5">
        {loading ? (
          <>
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </>
        ) : approvals.length === 0 ? (
          <EmptyState title={title} />
        ) : (
          approvals.map((approval) => (
            <ApprovalCard
              key={approval.id}
              approval={approval}
              onApprove={onApprove}
              onReject={onReject}
            />
          ))
        )}
      </div>
    </div>
  )
}
