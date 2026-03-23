"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { Search } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { customInstance } from "@/lib/axios-instance"

// ---- Types -----------------------------------------------------------------

interface Session {
  id: string
  openclaw_session_id: string
  agent_slug: string
  channel_type: string
  message_count: number
  token_count: number
  started_at: string
  ended_at?: string
  status: string
}

interface SessionsResponse {
  items: Session[]
  total: number
}

// ---- Fetcher ----------------------------------------------------------------

const fetchSessions = (page: number, pageSize: number, search: string) =>
  customInstance<SessionsResponse>({
    url: "/sessions",
    method: "GET",
    params: { page, page_size: pageSize, ...(search ? { search } : {}) },
  })

// ---- Helpers ----------------------------------------------------------------

function statusVariant(status: string): "success" | "warning" | "error" | "secondary" {
  if (status === "active") return "success"
  if (status === "ended") return "secondary"
  if (status === "error") return "error"
  return "secondary"
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

// ---- Skeleton rows ----------------------------------------------------------

function RowSkeleton() {
  return (
    <tr className="border-b border-[hsl(var(--border))]">
      {Array.from({ length: 7 }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  )
}

// ---- Page ------------------------------------------------------------------

const PAGE_SIZE = 20

export default function SessionsPage() {
  const router = useRouter()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [inputValue, setInputValue] = useState("")

  const { data, isLoading } = useQuery({
    queryKey: ["sessions", page, PAGE_SIZE, search],
    queryFn: () => fetchSessions(page, PAGE_SIZE, search),
  })

  const sessions = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setSearch(inputValue)
    setPage(1)
  }

  return (
    <AppLayout>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
              Sessions
            </h1>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
              Browse OpenClaw agent sessions
            </p>
          </div>

          {/* Search */}
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[hsl(var(--muted-foreground))]" />
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Search by session ID or agent…"
                className="pl-8 pr-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))] w-64"
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

        {/* Table */}
        <div className="rounded-xl border border-[hsl(var(--border))] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30">
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                    Session ID
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                    Channel
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                    Agent
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                    Messages
                  </th>
                  <th className="px-4 py-2.5 text-right text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                    Tokens
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                    Started
                  </th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  Array.from({ length: 8 }).map((_, i) => <RowSkeleton key={i} />)
                ) : sessions.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="px-4 py-12 text-center text-sm text-[hsl(var(--muted-foreground))]"
                    >
                      No sessions found.
                    </td>
                  </tr>
                ) : (
                  sessions.map((session) => (
                    <tr
                      key={session.id}
                      onClick={() => router.push(`/sessions/${session.id}`)}
                      className="border-b border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/20 cursor-pointer transition-colors"
                    >
                      <td className="px-4 py-3 font-mono text-xs text-[hsl(var(--foreground))]">
                        {(session.openclaw_session_id ?? session.id).slice(0, 16)}…
                      </td>
                      <td className="px-4 py-3 text-[hsl(var(--foreground))]">
                        {session.channel_type}
                      </td>
                      <td className="px-4 py-3 text-[hsl(var(--foreground))]">
                        {session.agent_slug}
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums text-[hsl(var(--foreground))]">
                        {session.message_count ?? 0}
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums text-[hsl(var(--foreground))]">
                        {(session.token_count ?? 0).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))]">
                        {formatDate(session.started_at)}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={statusVariant(session.status)}>
                          {session.status}
                        </Badge>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between text-sm text-[hsl(var(--muted-foreground))]">
          <span>
            {isLoading ? "Loading…" : `${total} session${total !== 1 ? "s" : ""} total`}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || isLoading}
              className="px-3 py-1 rounded-lg border border-[hsl(var(--border))] disabled:opacity-40 hover:bg-[hsl(var(--muted))]/30 transition-colors"
            >
              Previous
            </button>
            <span>
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || isLoading}
              className="px-3 py-1 rounded-lg border border-[hsl(var(--border))] disabled:opacity-40 hover:bg-[hsl(var(--muted))]/30 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
