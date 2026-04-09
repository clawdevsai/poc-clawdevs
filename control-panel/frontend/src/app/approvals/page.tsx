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

import { useEffect, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Clock, CheckCircle, XCircle } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Skeleton } from "@/components/ui/skeleton"
import { KanbanColumn } from "@/components/approvals/kanban-column"
import { DecisionDialog } from "@/components/approvals/decision-dialog"
import { customInstance } from "@/lib/axios-instance"
import { wsManager } from "@/lib/ws"
import type { Approval } from "@/components/approvals/types"

// ---- Types -----------------------------------------------------------------

interface ApprovalsResponse {
  items: Approval[]
  total: number
}

interface ApprovalStats {
  pending: number
  approved_today: number
  rejected_today: number
}

// ---- Fetchers --------------------------------------------------------------

const fetchApprovals = (status: "pending" | "approved" | "rejected") =>
  customInstance<ApprovalsResponse>({
    url: "/approvals",
    method: "GET",
    params: { status, page: 1, page_size: 50 },
  })

const fetchStats = () =>
  customInstance<ApprovalStats>({
    url: "/approvals/stats",
    method: "GET",
  })

// ---- Stats bar -------------------------------------------------------------

interface StatItemProps {
  icon: React.ElementType
  label: string
  value: number | undefined
  loading: boolean
  color?: string
}

function StatItem({ icon: Icon, label, value, loading, color }: StatItemProps) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-3 flex-1">
      <div
        className="h-8 w-8 rounded-lg flex items-center justify-center shrink-0"
        style={{
          backgroundColor: color ? `${color}1A` : "hsl(var(--muted))",
        }}
      >
        <Icon
          className="h-4 w-4"
          style={{ color: color ?? "hsl(var(--muted-foreground))" }}
        />
      </div>
      <div className="flex flex-col gap-0.5 min-w-0">
        <span className="text-xs text-[hsl(var(--muted-foreground))] truncate">
          {label}
        </span>
        {loading ? (
          <Skeleton className="h-5 w-8" />
        ) : (
          <span
            className="text-lg font-bold leading-none"
            style={{ color: color ?? "hsl(var(--foreground))" }}
          >
            {value ?? 0}
          </span>
        )}
      </div>
    </div>
  )
}

// ---- Page ------------------------------------------------------------------

export default function ApprovalsPage() {
  const queryClient = useQueryClient()

  // Dialog state
  const [dialogApproval, setDialogApproval] = useState<Approval | null>(null)
  const [dialogDecision, setDialogDecision] = useState<
    "approved" | "rejected"
  >("approved")

  // Data queries — fetch all three columns in parallel
  const { data: pendingData, isLoading: pendingLoading } = useQuery({
    queryKey: ["approvals", "pending"],
    queryFn: () => fetchApprovals("pending"),
  })

  const { data: approvedData, isLoading: approvedLoading } = useQuery({
    queryKey: ["approvals", "approved"],
    queryFn: () => fetchApprovals("approved"),
  })

  const { data: rejectedData, isLoading: rejectedLoading } = useQuery({
    queryKey: ["approvals", "rejected"],
    queryFn: () => fetchApprovals("rejected"),
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["approvals", "stats"],
    queryFn: fetchStats,
  })

  // Live updates via WebSocket "approvals" channel
  useEffect(() => {
    if (!wsManager) return
    const unsub = wsManager.subscribe("approvals", () => {
      queryClient.invalidateQueries({ queryKey: ["approvals"] })
    })
    return unsub
  }, [queryClient])

  // Action handlers
  function handleApprove(approval: Approval) {
    setDialogDecision("approved")
    setDialogApproval(approval)
  }

  function handleReject(approval: Approval) {
    setDialogDecision("rejected")
    setDialogApproval(approval)
  }

  function handleDialogClose() {
    setDialogApproval(null)
  }

  const pending = pendingData?.items ?? []
  const approved = approvedData?.items ?? []
  const rejected = rejectedData?.items ?? []

  return (
    <AppLayout>
      <div className="flex flex-col gap-6 h-full">
        {/* Page heading */}
        <div>
          <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
            Aprovações
          </h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
            Revise e decida sobre as solicitações de ação dos agentes
          </p>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <StatItem
            icon={Clock}
            label="Pendentes"
            value={stats?.pending}
            loading={statsLoading}
            color="#FBBF24"
          />
          <StatItem
            icon={CheckCircle}
            label="Aprovadas Hoje"
            value={stats?.approved_today}
            loading={statsLoading}
            color="#00FF9C"
          />
          <StatItem
            icon={XCircle}
            label="Rejeitadas Hoje"
            value={stats?.rejected_today}
            loading={statsLoading}
            color="#F87171"
          />
        </div>

        {/* Kanban board */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 flex-1">
          <KanbanColumn
            title="Pendentes"
            approvals={pending}
            loading={pendingLoading}
            onApprove={handleApprove}
            onReject={handleReject}
            accentColor="#FBBF24"
          />
          <KanbanColumn
            title="Aprovadas"
            approvals={approved}
            loading={approvedLoading}
            accentColor="#00FF9C"
          />
          <KanbanColumn
            title="Rejeitadas"
            approvals={rejected}
            loading={rejectedLoading}
            accentColor="#F87171"
          />
        </div>
      </div>

      {/* Decision dialog */}
      <DecisionDialog
        approval={dialogApproval}
        decision={dialogDecision}
        open={dialogApproval !== null}
        onClose={handleDialogClose}
      />
    </AppLayout>
  )
}
