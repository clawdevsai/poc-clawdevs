"use client"

import { formatDistanceToNow } from "date-fns"
import { AgentAvatar } from "@/components/agents/agent-avatar"
import { Badge } from "@/components/ui/badge"
import type { Approval } from "./types"

interface ApprovalCardProps {
  approval: Approval
  onApprove?: (approval: Approval) => void
  onReject?: (approval: Approval) => void
}

export function ApprovalCard({
  approval,
  onApprove,
  onReject,
}: ApprovalCardProps) {
  const description =
    approval.payload?.description ??
    approval.payload?.action_type ??
    "No description"

  const rubricEntries = approval.rubric_scores
    ? Object.entries(approval.rubric_scores)
    : []

  const isPending = approval.status === "pending"

  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3">
      {/* Top row: avatar + agent id */}
      <div className="flex items-center gap-3">
        <AgentAvatar
          slug={approval.agent_id}
          displayName={approval.agent_id}
          size="sm"
        />
        <div className="flex flex-col gap-0.5 flex-1 min-w-0">
          <span className="text-sm font-semibold text-[hsl(var(--foreground))] truncate font-mono">
            {approval.agent_id}
          </span>
          <span className="text-xs text-[hsl(var(--muted-foreground))] truncate">
            session:{" "}
            <span className="font-mono">
              {approval.openclaw_session_id.slice(0, 8)}…
            </span>
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-[hsl(var(--foreground))] line-clamp-2 leading-relaxed">
        {description}
      </p>

      {/* Rubric scores */}
      {rubricEntries.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {rubricEntries.map(([key, value]) => (
            <Badge
              key={key}
              variant="outline"
              className="text-[10px] px-1.5 py-0 gap-1"
            >
              <span className="text-[hsl(var(--muted-foreground))]">{key}</span>
              <span
                className={
                  value >= 0.7
                    ? "text-green-400"
                    : value >= 0.4
                    ? "text-yellow-400"
                    : "text-red-400"
                }
              >
                {(value * 100).toFixed(0)}%
              </span>
            </Badge>
          ))}
        </div>
      )}

      {/* Footer: timestamp + actions */}
      <div className="flex items-center justify-between gap-2 mt-auto">
        <span className="text-xs text-[hsl(var(--muted-foreground))]">
          {formatDistanceToNow(new Date(approval.created_at), {
            addSuffix: true,
          })}
        </span>

        {isPending && onApprove && onReject && (
          <div className="flex gap-1.5">
            <button
              onClick={() => onReject(approval)}
              className="px-2.5 py-1 rounded-md text-xs font-medium bg-red-500/15 text-red-400 border border-red-500/25 hover:bg-red-500/25 transition-colors"
            >
              Reject
            </button>
            <button
              onClick={() => onApprove(approval)}
              className="px-2.5 py-1 rounded-md text-xs font-medium bg-[#00FF9C]/15 text-[#00FF9C] border border-[#00FF9C]/25 hover:bg-[#00FF9C]/25 transition-colors"
            >
              Approve
            </button>
          </div>
        )}

        {!isPending && (
          <Badge
            variant={approval.status === "approved" ? "success" : "error"}
            className="text-[10px]"
          >
            {approval.status}
          </Badge>
        )}
      </div>
    </div>
  )
}
