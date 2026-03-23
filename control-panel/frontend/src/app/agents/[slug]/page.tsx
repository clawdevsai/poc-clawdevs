"use client"

import { use, useEffect, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { formatDistanceToNow, format } from "date-fns"
import Link from "next/link"
import * as Tabs from "@radix-ui/react-tabs"
import { ArrowLeft, Clock, Calendar, CheckSquare, Brain } from "lucide-react"
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
  status: "online" | "idle" | "offline" | string
  model: string
  last_heartbeat?: string | null
  cron_expression?: string | null
  cron_status?: string | null
}

interface Session {
  id: string
  agent_slug: string
  status: string
  created_at: string
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
    params: { agent_slug: slug, page, page_size: 20 },
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

// ---- Status helpers -------------------------------------------------------

function statusBadgeVariant(status: string) {
  switch (status) {
    case "online":
      return "success"
    case "idle":
      return "warning"
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
  const fields: { label: string; value: React.ReactNode }[] = [
    { label: "ID", value: <span className="font-mono text-xs">{agent.id}</span> },
    { label: "Slug", value: <span className="font-mono text-xs">{agent.slug}</span> },
    { label: "Role", value: agent.role },
    { label: "Model", value: <span className="font-mono text-xs">{agent.model}</span> },
    {
      label: "Last Heartbeat",
      value: agent.last_heartbeat
        ? formatDistanceToNow(new Date(agent.last_heartbeat), { addSuffix: true })
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
            <dd className="text-sm text-[hsl(var(--foreground))] flex-1 truncate">
              {value}
            </dd>
          </div>
        ))}
      </dl>
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
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / 20)

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
        {sessions.map((session) => (
          <div
            key={session.id}
            className="flex items-center gap-3 px-4 py-3"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-mono text-[hsl(var(--foreground))] truncate">
                {session.id}
              </p>
              {session.task_description && (
                <p className="text-xs text-[hsl(var(--muted-foreground))] truncate mt-0.5">
                  {session.task_description}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2 shrink-0">
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
                {formatDistanceToNow(new Date(session.created_at), {
                  addSuffix: true,
                })}
              </span>
            </div>
          </div>
        ))}
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
                {formatDistanceToNow(new Date(approval.created_at), {
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

  const entries = data?.items ?? []

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
      <p className="text-xs text-[hsl(var(--muted-foreground))]">
        {data?.total ?? 0} entr{(data?.total ?? 0) !== 1 ? "ies" : "y"} total
      </p>
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
    </div>
  )
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
              size="lg"
            />
            <div className="flex flex-col gap-2 flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {agent.display_name}
              </h1>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline">{agent.role}</Badge>
                <Badge variant="secondary" className="font-mono text-[10px]">
                  {agent.model}
                </Badge>
                <Badge
                  variant={
                    statusBadgeVariant(agent.status) as
                      | "success"
                      | "warning"
                      | "secondary"
                  }
                >
                  <StatusDot status={agent.status} />
                  <span className="ml-1.5 capitalize">{agent.status}</span>
                </Badge>
              </div>
              {agent.last_heartbeat && (
                <p className="text-xs text-[hsl(var(--muted-foreground))]">
                  Last seen{" "}
                  {formatDistanceToNow(new Date(agent.last_heartbeat), {
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
