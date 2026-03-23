"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { formatDistanceToNow } from "date-fns"
import { Search, ChevronDown, ChevronUp } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { AgentAvatar } from "@/components/agents/agent-avatar"
import { customInstance } from "@/lib/axios-instance"
import { cn } from "@/lib/utils"

// ---- Types ----------------------------------------------------------------

interface MemoryEntry {
  id: string
  agent_slug: string
  title: string
  body: string
  entry_type: "active" | "archived" | "promoted" | string
  tags: string[]
  created_at: string
}

interface MemoryResponse {
  items: MemoryEntry[]
  total: number
}

interface Agent {
  id: string
  slug: string
  display_name: string
  role: string
  status: string
}

interface AgentsResponse {
  items: Agent[]
  total: number
}

// ---- Fetchers -------------------------------------------------------------

const fetchAgents = () =>
  customInstance<AgentsResponse>({ url: "/agents", method: "GET" })

const fetchMemory = (agentSlug: string, search: string, page: number) =>
  customInstance<MemoryResponse>({
    url: "/memory",
    method: "GET",
    params: {
      ...(agentSlug ? { agent_slug: agentSlug } : {}),
      ...(search ? { search } : {}),
      page,
      page_size: 30,
    },
  })

// ---- Helpers --------------------------------------------------------------

function entryTypeBadgeVariant(
  type: string
): "success" | "secondary" | "default" {
  switch (type) {
    case "active":
      return "success"
    case "archived":
      return "secondary"
    case "promoted":
      return "default"
    default:
      return "secondary"
  }
}

// ---- Sub-components -------------------------------------------------------

function MemoryCardSkeleton() {
  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 space-y-3">
      <div className="flex items-center justify-between gap-3">
        <Skeleton className="h-4 w-48" />
        <Skeleton className="h-5 w-16 rounded-full" />
      </div>
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-3/4" />
      <div className="flex items-center gap-2">
        <Skeleton className="h-3 w-20 rounded-full" />
        <Skeleton className="h-3 w-16 rounded-full" />
      </div>
    </div>
  )
}

function MemoryCard({ entry }: { entry: MemoryEntry }) {
  const [expanded, setExpanded] = useState(false)
  const preview =
    entry.body.length > 160 ? entry.body.slice(0, 160) + "…" : entry.body

  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 space-y-2.5">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-semibold text-[hsl(var(--foreground))] leading-snug flex-1 min-w-0">
          {entry.title}
        </h3>
        <Badge
          variant={entryTypeBadgeVariant(entry.entry_type)}
          className={cn(
            "shrink-0",
            entry.entry_type === "promoted" &&
              "bg-blue-500/20 text-blue-400 border-transparent"
          )}
        >
          {entry.entry_type}
        </Badge>
      </div>

      {/* Body */}
      <p className="text-xs text-[hsl(var(--muted-foreground))] leading-relaxed whitespace-pre-wrap break-words">
        {expanded ? entry.body : preview}
      </p>

      {/* Expand / collapse */}
      {entry.body.length > 160 && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="flex items-center gap-1 text-xs text-[hsl(var(--primary))] hover:opacity-80 transition-opacity"
        >
          {expanded ? (
            <>
              <ChevronUp className="h-3 w-3" /> Show less
            </>
          ) : (
            <>
              <ChevronDown className="h-3 w-3" /> Show more
            </>
          )}
        </button>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between gap-3 pt-1">
        <div className="flex items-center flex-wrap gap-1.5">
          <span className="text-xs text-[hsl(var(--muted-foreground))] font-mono">
            {entry.agent_slug}
          </span>
          {entry.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-1.5 py-0.5 rounded bg-[hsl(var(--muted))]/40 text-[hsl(var(--muted-foreground))]"
            >
              {tag}
            </span>
          ))}
        </div>
        <span className="text-xs text-[hsl(var(--muted-foreground))] shrink-0">
          {formatDistanceToNow(new Date(entry.created_at), { addSuffix: true })}
        </span>
      </div>
    </div>
  )
}

// ---- Page -----------------------------------------------------------------

export default function MemoryPage() {
  const [selectedAgent, setSelectedAgent] = useState<string>("")
  const [search, setSearch] = useState("")
  const [inputValue, setInputValue] = useState("")
  const [page, setPage] = useState(1)

  const { data: agentsData, isLoading: agentsLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
  })

  const { data: memoryData, isLoading: memoryLoading } = useQuery({
    queryKey: ["memory", selectedAgent, search, page],
    queryFn: () => fetchMemory(selectedAgent, search, page),
  })

  const agents = agentsData?.items ?? []
  const entries = memoryData?.items ?? []
  const total = memoryData?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / 30))

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setSearch(inputValue)
    setPage(1)
  }

  function selectAgent(slug: string) {
    setSelectedAgent(slug === selectedAgent ? "" : slug)
    setPage(1)
  }

  return (
    <AppLayout>
      <div className="flex gap-6 min-h-0">
        {/* Sidebar */}
        <aside className="w-52 shrink-0 flex flex-col gap-1">
          <p className="text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wide px-2 mb-1">
            Filter by agent
          </p>
          <button
            onClick={() => selectAgent("")}
            className={cn(
              "text-left px-3 py-2 rounded-lg text-sm transition-colors",
              selectedAgent === ""
                ? "bg-[hsl(var(--primary))]/15 text-[hsl(var(--primary))]"
                : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/30 hover:text-[hsl(var(--foreground))]"
            )}
          >
            Global (all)
          </button>
          {agentsLoading
            ? Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-9 w-full rounded-lg" />
              ))
            : agents.map((agent) => (
                <button
                  key={agent.slug}
                  onClick={() => selectAgent(agent.slug)}
                  className={cn(
                    "flex items-center gap-2.5 text-left px-3 py-2 rounded-lg text-sm transition-colors",
                    selectedAgent === agent.slug
                      ? "bg-[hsl(var(--primary))]/15 text-[hsl(var(--primary))]"
                      : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/30 hover:text-[hsl(var(--foreground))]"
                  )}
                >
                  <AgentAvatar
                    slug={agent.slug}
                    displayName={agent.display_name}
                    size="sm"
                  />
                  <span className="truncate">{agent.display_name}</span>
                </button>
              ))}
        </aside>

        {/* Main content */}
        <div className="flex-1 min-w-0 flex flex-col gap-5">
          {/* Header */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
                Memory
              </h1>
              <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
                {memoryLoading
                  ? "Loading…"
                  : `${total} entr${total !== 1 ? "ies" : "y"}${
                      selectedAgent ? ` for ${selectedAgent}` : ""
                    }`}
              </p>
            </div>

            <form onSubmit={handleSearch} className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[hsl(var(--muted-foreground))]" />
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Search memory…"
                  className="pl-8 pr-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))] w-56"
                />
              </div>
              <button
                type="submit"
                className="px-3 py-1.5 text-sm rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 transition-opacity"
              >
                Search
              </button>
            </form>
          </div>

          {/* Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {memoryLoading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <MemoryCardSkeleton key={i} />
              ))
            ) : entries.length === 0 ? (
              <div className="col-span-full flex flex-col items-center justify-center py-20 gap-3">
                <div className="h-12 w-12 rounded-full bg-[hsl(var(--muted))] flex items-center justify-center">
                  <Search className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
                </div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  No memory entries found
                </p>
              </div>
            ) : (
              entries.map((entry) => (
                <MemoryCard key={entry.id} entry={entry} />
              ))
            )}
          </div>

          {/* Pagination */}
          {!memoryLoading && totalPages > 1 && (
            <div className="flex items-center justify-between text-sm text-[hsl(var(--muted-foreground))]">
              <span>{total} entries total</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="px-3 py-1 rounded-lg border border-[hsl(var(--border))] disabled:opacity-40 hover:bg-[hsl(var(--muted))]/30 transition-colors"
                >
                  Previous
                </button>
                <span>
                  {page} / {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="px-3 py-1 rounded-lg border border-[hsl(var(--border))] disabled:opacity-40 hover:bg-[hsl(var(--muted))]/30 transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  )
}
