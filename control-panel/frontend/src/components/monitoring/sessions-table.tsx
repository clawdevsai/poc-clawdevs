import { formatDistanceToNow } from "date-fns"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { SessionItem } from "@/lib/monitoring-api"

interface SessionsTableProps {
  items: SessionItem[]
  isLoading: boolean
}

export function SessionsTable({ items, isLoading }: SessionsTableProps) {
  if (isLoading) {
    return (
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-4 text-sm text-[hsl(var(--muted-foreground))]">
        Loading sessions...
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7] p-6 text-center">
        <p className="text-[20px] font-semibold text-[hsl(var(--foreground))]">No recent sessions</p>
        <p className="mt-2 text-[16px] text-[hsl(var(--muted-foreground))]">
          Sessions will appear here once the runtime starts. Check back after your
          next run.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))/0.7]">
      <Table className="text-[14px]">
        <TableHeader className="bg-[hsl(var(--muted))/0.35]">
          <TableRow className="hover:bg-transparent">
            <TableHead>Session</TableHead>
            <TableHead>Agent</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Messages</TableHead>
            <TableHead>Tokens</TableHead>
            <TableHead>Last active</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody className="text-[hsl(var(--foreground))]">
          {items.map((item) => (
            <TableRow key={item.id}>
              <TableCell className="font-medium">{item.session_label}</TableCell>
              <TableCell className="text-[hsl(var(--muted-foreground))]">
                {item.agent_slug ?? "—"}
              </TableCell>
              <TableCell className="capitalize">{item.status}</TableCell>
              <TableCell>{item.message_count}</TableCell>
              <TableCell>{item.token_count}</TableCell>
              <TableCell className="text-[hsl(var(--muted-foreground))]">
                {item.last_active_at
                  ? formatDistanceToNow(new Date(item.last_active_at), {
                      addSuffix: true,
                    })
                  : "—"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
