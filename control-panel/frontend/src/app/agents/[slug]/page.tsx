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

import { use, useEffect, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { formatDistanceToNow, format } from "date-fns"
import Link from "next/link"
import * as Tabs from "@radix-ui/react-tabs"
import { ArrowLeft, Clock, Calendar, CheckSquare, Brain, Eye, Download, X, MessageSquare } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { AgentAvatar } from "@/components/agents/agent-avatar"
import { customInstance } from "@/lib/axios-instance"
import { wsManager } from "@/lib/ws"
import { cn } from "@/lib/utils"

// ---- Types ----------------------------------------------------------------

interface Agent {
  id: string
  slug: string
  display_name: string
  role: string
  avatar_url?: string | null
  status: "online" | "idle" | "offline" | string
  runtime_status?: "online" | "working" | "idle" | "offline" | string | null
  model?: string | null
  current_model?: string | null
  last_heartbeat?: string | null
  last_heartbeat_at?: string | null
  cron_expression?: string | null
  cron_status?: string | null
  current_activity?: string | null
  current_activity_full?: string | null
  current_activity_at?: string | null
}

interface Session {
  id: string
  agent_slug: string
  openclaw_session_id: string
  openclaw_session_key?: string | null
  session_kind?: string
  session_label?: string
  status: string
  created_at: string
  last_active_at?: string | null
  ended_at?: string | null
  task_description?: string | null
}

interface Approval {
  id: string
  agent_slug?: string | null
  action_type: string
  status: string
  created_at: string
  description?: string | null
}

interface MemoryEntry {
  id: string
  agent_slug: string
  entry_type: string
  title: string
  body: string
  tags?: string[]
  created_at: string
}

interface MemoryFileResponse {
  agent_slug: string
  file_name: string
  content: string
  updated_at?: string | null
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
}

// ---- Fetchers -------------------------------------------------------------

const fetchAgent = (slug: string) =>
  customInstance<Agent>({ url: `/agents/${slug}`, method: "GET" })

const fetchSessions = (slug: string, page: number) =>
  customInstance<PaginatedResponse<Session>>({
    url: "/sessions",
    method: "GET",
    params: { agent_slug: slug, page, page_size: 100 },
  })

const fetchApprovals = (slug: string) =>
  customInstance<PaginatedResponse<Approval>>({
    url: "/approvals",
    method: "GET",
    params: { agent_slug: slug },
  })

const fetchMemory = (slug: string) =>
  customInstance<PaginatedResponse<MemoryEntry>>({
    url: "/memory",
    method: "GET",
    params: { agent_slug: slug },
  })

const fetchMemoryFile = (slug: string) =>
  customInstance<MemoryFileResponse>({
    url: `/memory/agent/${slug}/file`,
    method: "GET",
  })

const fetchMemoryFileDownload = (slug: string) =>
  customInstance<Blob>({
    url: `/memory/agent/${slug}/file/download`,
    method: "GET",
    responseType: "blob",
  })

// ---- Status helpers -------------------------------------------------------

function statusBadgeVariant(status: string) {
  switch (status) {
    case "online":
    case "working":
      return "success"
    case "idle":
      return "warning"
    case "error":
      return "error"
    case "stopped":
      return "secondary"
    default:
      return "secondary"
  }
}

function StatusDot({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-block h-2.5 w-2.5 rounded-full",
        status === "online"
          ? "bg-green-400 shadow-[0_0_6px_#4ade80]"
          : status === "idle"
          ? "bg-yellow-400"
          : status === "error"
          ? "bg-red-400 shadow-[0_0_6px_#f87171]"
          : "bg-white/30"
      )}
    />
  )
}

// ---- Hero Skeleton --------------------------------------------------------

function HeroSkeleton() {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5 pb-6 border-b border-[hsl(var(--border))]">
      <Skeleton className="h-16 w-16 rounded-full shrink-0" />
      <div className="flex flex-col gap-2 flex-1">
        <Skeleton className="h-6 w-40" />
        <div className="flex gap-2">
          <Skeleton className="h-5 w-20 rounded-full" />
          <Skeleton className="h-5 w-24 rounded-full" />
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
        <Skeleton className="h-4 w-32" />
      </div>
    </div>
  )
}

// ---- Overview Tab ---------------------------------------------------------

function OverviewTab({ agent }: { agent: Agent }) {
  const [showFullWork, setShowFullWork] = useState(false)
  const fullWork = agent.current_activity_full ?? agent.current_activity ?? ""

  const fields: { label: string; value: React.ReactNode }[] = [
    { label: "ID", value: <span className="font-mono text-xs">{agent.id}</span> },
    { label: "Slug", value: <span className="font-mono text-xs">{agent.slug}</span> },
    { label: "Role", value: agent.role },
    { label: "Model", value: <span className="font-mono text-xs">{agent.model ?? agent.current_model ?? "—"}</span> },
    {
      label: "Current Work",
      value: agent.current_activity ? (
        <div className="flex flex-col gap-1">
          <div className="flex items-start gap-2">
            <span className="text-sm text-[hsl(var(--foreground))] whitespace-normal break-words flex-1">
              {agent.current_activity}
            </span>
            {fullWork && (
              <button
                onClick={() => setShowFullWork(true)}
                className="inline-flex items-center justify-center h-6 w-6 rounded border border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] hover:text-[hsl(var(--primary))] transition-colors"
                aria-label="Ver trabalho atual completo"
              >
                <Eye className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
          {agent.current_activity_at && (
            <span className="text-xs text-[hsl(var(--muted-foreground))]">
              updated {formatDistanceToNow(parseApiDate(agent.current_activity_at), { addSuffix: true })}
            </span>
          )}
        </div>
      ) : (
        <span className="text-xs text-[hsl(var(--muted-foreground))]">No current activity reported</span>
      ),
    },
    {
      label: "Last Heartbeat",
      value: (agent.last_heartbeat ?? agent.last_heartbeat_at)
        ? formatDistanceToNow(parseApiDate((agent.last_heartbeat ?? agent.last_heartbeat_at) as string), { addSuffix: true })
        : "—",
    },
  ]

  if (agent.cron_expression) {
    fields.push({
      label: "Cron Schedule",
      value: (
        <span className="font-mono text-xs flex items-center gap-1.5">
          <Calendar className="h-3 w-3" />
          {agent.cron_expression}
          {agent.cron_status && (
            <Badge variant="secondary" className="ml-1 text-[10px]">
              {agent.cron_status}
            </Badge>
          )}
        </span>
      ),
    })
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-[hsl(var(--foreground))]">
        Identity
      </h3>
      <dl className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] divide-y divide-[hsl(var(--border))]">
        {fields.map(({ label, value }) => (
          <div key={label} className="flex items-center gap-4 px-4 py-3">
            <dt className="w-32 shrink-0 text-xs text-[hsl(var(--muted-foreground))]">
              {label}
            </dt>
            <dd
              className={cn(
                "text-sm text-[hsl(var(--foreground))] flex-1",
                label === "Current Work" ? "whitespace-normal break-words" : "truncate"
              )}
            >
              {value}
            </dd>
          </div>
        ))}
      </dl>
      {showFullWork && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-3xl rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] overflow-hidden">
            <div className="px-4 py-3 border-b border-[hsl(var(--border))] flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-[hsl(var(--foreground))]">Current Work (Full)</p>
              <button
                onClick={() => setShowFullWork(false)}
                className="inline-flex items-center justify-center h-8 w-8 rounded-lg border border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] hover:text-[hsl(var(--primary))] transition-colors"
                aria-label="Fechar"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-4">
              <pre className="text-xs leading-5 font-mono whitespace-pre-wrap break-words rounded-lg border border-[hsl(var(--border))] bg-black/30 p-4 overflow-auto max-h-[60vh]">
                {fullWork}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ---- Sessions Tab ---------------------------------------------------------

function SessionsTab({ slug }: { slug: string }) {
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ["sessions", slug, page],
    queryFn: () => fetchSessions(slug, page),
  })

  const sessions = data?.items ?? []
  const statusPriority = (status: string) => (status === "active" ? 0 : 1)
  const sortedSessions = [...sessions].sort((a, b) => {
    const byStatus = statusPriority(a.status) - statusPriority(b.status)
    if (byStatus !== 0) return byStatus

    const aTime = new Date(a.last_active_at ?? a.created_at).getTime()
    const bTime = new Date(b.last_active_at ?? b.created_at).getTime()
    return bTime - aTime
  })
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / 100)

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    )
  }

  if (sessions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-2 text-[hsl(var(--muted-foreground))]">
        <Clock className="h-8 w-8 opacity-40" />
        <p className="text-sm">No sessions found for this agent</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-[hsl(var(--muted-foreground))]">
        {total} session{total !== 1 ? "s" : ""} total
      </p>
      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] divide-y divide-[hsl(var(--border))]">
        {sortedSessions.map((session) => {
          const chatKey = session.openclaw_session_key
          const chatHref =
            chatKey != null && chatKey.length > 0
              ? `/chat?session=${encodeURIComponent(chatKey)}`
              : null
          return (
          <div
            key={session.id}
            className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center sm:gap-3"
          >
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-medium text-[hsl(var(--foreground))] truncate">
                  {session.session_label ?? "—"}
                </span>
                {session.session_kind === "sub" ? (
                  <Badge variant="secondary" className="text-[10px]">
                    Subagente
                  </Badge>
                ) : null}
              </div>
              <p
                className="text-xs font-mono text-[hsl(var(--muted-foreground))] truncate mt-0.5"
                title={session.openclaw_session_key ?? session.openclaw_session_id}
              >
                {session.openclaw_session_key ?? session.openclaw_session_id}
              </p>
              {session.task_description && (
                <p className="text-xs text-[hsl(var(--muted-foreground))] truncate mt-0.5">
                  {session.task_description}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2 shrink-0 flex-wrap justify-end">
              {chatHref ? (
                <Link
                  href={chatHref}
                  className="inline-flex items-center gap-1 rounded-lg border border-[hsl(var(--border))] px-2 py-1 text-xs text-[hsl(var(--foreground))] hover:border-[hsl(var(--primary))] hover:text-[hsl(var(--primary))] transition-colors"
                >
                  <MessageSquare className="h-3.5 w-3.5" />
                  Abrir no chat
                </Link>
              ) : null}
              <Badge
                variant={
                  session.status === "active"
                    ? "success"
                    : session.status === "completed"
                    ? "secondary"
                    : "error"
                }
              >
                {session.status}
              </Badge>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                {formatDistanceToNow(
                  parseApiDate((session.last_active_at ?? session.created_at) as string),
                  {
                  addSuffix: true,
                  }
                )}
              </span>
            </div>
          </div>
          )
        })}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 text-xs rounded-lg border border-[hsl(var(--border))] disabled:opacity-40 hover:border-[hsl(var(--primary))] transition-colors"
          >
            Previous
          </button>
          <span className="text-xs text-[hsl(var(--muted-foreground))]">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1.5 text-xs rounded-lg border border-[hsl(var(--border))] disabled:opacity-40 hover:border-[hsl(var(--primary))] transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

// ---- Approvals Tab --------------------------------------------------------

function ApprovalsTab({ slug }: { slug: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["approvals", slug],
    queryFn: () => fetchApprovals(slug),
  })

  const approvals = data?.items ?? []

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    )
  }

  if (approvals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-2 text-[hsl(var(--muted-foreground))]">
        <CheckSquare className="h-8 w-8 opacity-40" />
        <p className="text-sm">No approvals found for this agent</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <p className="text-xs text-[hsl(var(--muted-foreground))]">
        {data?.total ?? 0} approval{(data?.total ?? 0) !== 1 ? "s" : ""} total
      </p>
      <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] divide-y divide-[hsl(var(--border))]">
        {approvals.map((approval) => (
          <div key={approval.id} className="flex items-center gap-3 px-4 py-3">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-[hsl(var(--foreground))] truncate">
                {approval.action_type}
              </p>
              {approval.description && (
                <p className="text-xs text-[hsl(var(--muted-foreground))] truncate mt-0.5">
                  {approval.description}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Badge
                variant={
                  approval.status === "approved"
                    ? "success"
                    : approval.status === "pending"
                    ? "warning"
                    : "error"
                }
              >
                {approval.status}
              </Badge>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">
                {formatDistanceToNow(parseApiDate(approval.created_at), {
                  addSuffix: true,
                })}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ---- Memory Tab -----------------------------------------------------------

function MemoryTab({ slug }: { slug: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ["memory", slug],
    queryFn: () => fetchMemory(slug),
  })
  const [viewerOpen, setViewerOpen] = useState(false)
  const [viewerLoading, setViewerLoading] = useState(false)
  const [viewerError, setViewerError] = useState<string | null>(null)
  const [memoryFile, setMemoryFile] = useState<MemoryFileResponse | null>(null)

  const entries = data?.items ?? []

  const openFullMemory = async () => {
    setViewerOpen(true)
    setViewerLoading(true)
    setViewerError(null)
    try {
      const file = await fetchMemoryFile(slug)
      setMemoryFile(file)
    } catch (error) {
      console.error(error)
      setViewerError("Failed to load full memory file")
      setMemoryFile(null)
    } finally {
      setViewerLoading(false)
    }
  }

  const downloadMemory = async () => {
    try {
      const blob = await fetchMemoryFileDownload(slug)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${slug}-MEMORY.md`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error(error)
      setViewerError("Failed to download memory file")
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-lg" />
        ))}
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-2 text-[hsl(var(--muted-foreground))]">
        <Brain className="h-8 w-8 opacity-40" />
        <p className="text-sm">No memory entries for this agent</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs text-[hsl(var(--muted-foreground))]">
          {data?.total ?? 0} entr{(data?.total ?? 0) !== 1 ? "ies" : "y"} total
        </p>
        <button
          onClick={openFullMemory}
          className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg border border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] hover:text-[hsl(var(--primary))] transition-colors"
          aria-label="Ver arquivo MEMORY.md completo"
        >
          <Eye className="h-3.5 w-3.5" />
          Ver tudo
        </button>
      </div>
      <div className="space-y-3">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 space-y-2"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-[hsl(var(--foreground))] truncate">
                  {entry.title}
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
                  {format(new Date(entry.created_at), "MMM d, yyyy · HH:mm")}
                </p>
              </div>
              <Badge variant="secondary" className="text-[10px] shrink-0">
                {entry.entry_type}
              </Badge>
            </div>
            <p className="text-xs text-[hsl(var(--muted-foreground))] line-clamp-3">
              {entry.body}
            </p>
            {entry.tags && entry.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {entry.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-[10px] px-1.5 py-0.5 rounded bg-[hsl(var(--primary)/0.1)] text-[hsl(var(--primary))] font-mono"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {viewerOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-5xl max-h-[88vh] rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] overflow-hidden">
            <div className="px-4 py-3 border-b border-[hsl(var(--border))] flex items-center justify-between gap-3">
              <div className="min-w-0">
                <p className="text-sm font-semibold text-[hsl(var(--foreground))] truncate">
                  {memoryFile?.file_name ?? "MEMORY.md"}
                </p>
                {memoryFile?.updated_at && (
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
                    Updated {formatDistanceToNow(parseApiDate(memoryFile.updated_at), { addSuffix: true })}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={downloadMemory}
                  className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg border border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] hover:text-[hsl(var(--primary))] transition-colors"
                  aria-label="Baixar MEMORY.md"
                >
                  <Download className="h-3.5 w-3.5" />
                  Baixar
                </button>
                <button
                  onClick={() => setViewerOpen(false)}
                  className="inline-flex items-center justify-center h-8 w-8 rounded-lg border border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] hover:text-[hsl(var(--primary))] transition-colors"
                  aria-label="Fechar"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="p-4">
              {viewerLoading ? (
                <Skeleton className="h-[60vh] w-full rounded-lg" />
              ) : viewerError ? (
                <p className="text-sm text-red-400">{viewerError}</p>
              ) : (
                <pre className="text-xs leading-5 font-mono whitespace-pre-wrap break-words rounded-lg border border-[hsl(var(--border))] bg-black/30 p-4 overflow-auto max-h-[65vh]">
                  {memoryFile?.content || "No content available."}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function parseApiDate(value: string): Date {
  const hasTimezone = /[zZ]$|[+-]\d{2}:\d{2}$/.test(value)
  return new Date(hasTimezone ? value : `${value}Z`)
}

// ---- Page -----------------------------------------------------------------

const TAB_VALUES = ["overview", "sessions", "approvals", "memory"] as const
type TabValue = (typeof TAB_VALUES)[number]

interface PageProps {
  params: Promise<{ slug: string }>
}

export default function AgentProfilePage({ params }: PageProps) {
  const { slug } = use(params)
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<TabValue>("overview")

  const { data: agent, isLoading, isError } = useQuery({
    queryKey: ["agents", slug],
    queryFn: () => fetchAgent(slug),
  })

  // Live-update agent status via WebSocket
  useEffect(() => {
    if (!wsManager) return
    const unsub = wsManager.subscribe("agents", () => {
      queryClient.invalidateQueries({ queryKey: ["agents", slug] })
    })
    return unsub
  }, [queryClient, slug])

  if (isError) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <p className="text-[hsl(var(--muted-foreground))] text-sm">
            Agent &quot;{slug}&quot; not found.
          </p>
          <Link
            href="/agents"
            className="flex items-center gap-1.5 text-sm text-[hsl(var(--primary))] hover:underline"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Agents
          </Link>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6 max-w-4xl">
        {/* Back button */}
        <Link
          href="/agents"
          className="inline-flex items-center gap-1.5 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--primary))] transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          All Agents
        </Link>

        {/* Hero section */}
        {isLoading ? (
          <HeroSkeleton />
        ) : agent ? (
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5 pb-6 border-b border-[hsl(var(--border))]">
            <AgentAvatar
              slug={agent.slug}
              displayName={agent.display_name}
              avatarUrl={agent.avatar_url}
              size="lg"
            />
            <div className="flex flex-col gap-2 flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {agent.display_name}
              </h1>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline">{agent.role}</Badge>
                <Badge variant="secondary" className="font-mono text-[10px]">
                  {agent.model ?? agent.current_model ?? "—"}
                </Badge>
                {(() => {
                  const effectiveStatus = (agent.runtime_status ?? agent.status) as string
                  return (
                <Badge
                  variant={
                    statusBadgeVariant(effectiveStatus) as
                      | "success"
                      | "warning"
                      | "error"
                      | "secondary"
                  }
                >
                  <StatusDot status={effectiveStatus} />
                  <span className="ml-1.5 capitalize">{effectiveStatus}</span>
                </Badge>
                  )
                })()}
              </div>
              {(agent.last_heartbeat ?? agent.last_heartbeat_at) && (
                <p className="text-xs text-[hsl(var(--muted-foreground))]">
                  Last seen{" "}
                  {formatDistanceToNow(parseApiDate((agent.last_heartbeat ?? agent.last_heartbeat_at) as string), {
                    addSuffix: true,
                  })}
                </p>
              )}
            </div>
          </div>
        ) : null}

        {/* Tabs */}
        <Tabs.Root
          value={activeTab}
          onValueChange={(v) => setActiveTab(v as TabValue)}
        >
          <Tabs.List className="flex gap-1 border-b border-[hsl(var(--border))] mb-6">
            {TAB_VALUES.map((tab) => (
              <Tabs.Trigger
                key={tab}
                value={tab}
                className={cn(
                  "px-4 py-2 text-sm font-medium capitalize transition-colors border-b-2 -mb-px",
                  activeTab === tab
                    ? "border-[hsl(var(--primary))] text-[hsl(var(--primary))]"
                    : "border-transparent text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
                )}
              >
                {tab}
              </Tabs.Trigger>
            ))}
          </Tabs.List>

          <Tabs.Content value="overview" className="outline-none">
            {agent && <OverviewTab agent={agent} />}
            {isLoading && (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full rounded-lg" />
                ))}
              </div>
            )}
          </Tabs.Content>

          <Tabs.Content value="sessions" className="outline-none">
            {activeTab === "sessions" && <SessionsTab slug={slug} />}
          </Tabs.Content>

          <Tabs.Content value="approvals" className="outline-none">
            {activeTab === "approvals" && <ApprovalsTab slug={slug} />}
          </Tabs.Content>

          <Tabs.Content value="memory" className="outline-none">
            {activeTab === "memory" && <MemoryTab slug={slug} />}
          </Tabs.Content>
        </Tabs.Root>
      </div>
    </AppLayout>
  )
}
