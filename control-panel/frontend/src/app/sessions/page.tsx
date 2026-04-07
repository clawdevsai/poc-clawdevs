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

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { Search } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
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
    <TableRow className="hover:bg-transparent">
      {Array.from({ length: 7 }).map((_, i) => (
        <TableCell key={i}>
          <Skeleton className="h-4 w-full" />
        </TableCell>
      ))}
    </TableRow>
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
              <Input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Search by session ID or agent…"
                className="h-9 w-64 pl-8"
              />
            </div>
            <Button type="submit" size="sm">
              Search
            </Button>
          </form>
        </div>

        {/* Table */}
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="bg-[hsl(var(--muted))]/30 hover:bg-[hsl(var(--muted))]/30">
                  <TableHead>
                    Session ID
                  </TableHead>
                  <TableHead>
                    Channel
                  </TableHead>
                  <TableHead>
                    Agent
                  </TableHead>
                  <TableHead className="text-right">
                    Messages
                  </TableHead>
                  <TableHead className="text-right">
                    Tokens
                  </TableHead>
                  <TableHead>
                    Started
                  </TableHead>
                  <TableHead>
                    Status
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 8 }).map((_, i) => <RowSkeleton key={i} />)
                ) : sessions.length === 0 ? (
                  <TableRow className="hover:bg-transparent">
                    <TableCell
                      colSpan={7}
                      className="py-12 text-center text-sm text-[hsl(var(--muted-foreground))]"
                    >
                      No sessions found.
                    </TableCell>
                  </TableRow>
                ) : (
                  sessions.map((session) => (
                    <TableRow
                      key={session.id}
                      onClick={() => router.push(`/sessions/${session.id}`)}
                      className="cursor-pointer"
                    >
                      <TableCell className="font-mono text-xs text-[hsl(var(--foreground))]">
                        {(session.openclaw_session_id ?? session.id).slice(0, 16)}…
                      </TableCell>
                      <TableCell className="text-[hsl(var(--foreground))]">
                        {session.channel_type}
                      </TableCell>
                      <TableCell className="text-[hsl(var(--foreground))]">
                        {session.agent_slug}
                      </TableCell>
                      <TableCell className="text-right tabular-nums text-[hsl(var(--foreground))]">
                        {session.message_count ?? 0}
                      </TableCell>
                      <TableCell className="text-right tabular-nums text-[hsl(var(--foreground))]">
                        {(session.token_count ?? 0).toLocaleString()}
                      </TableCell>
                      <TableCell className="text-xs text-[hsl(var(--muted-foreground))]">
                        {formatDate(session.started_at)}
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusVariant(session.status)}>
                          {session.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Pagination */}
        <div className="flex items-center justify-between text-sm text-[hsl(var(--muted-foreground))]">
          <span>
            {isLoading ? "Loading…" : `${total} session${total !== 1 ? "s" : ""} total`}
          </span>
          <div className="flex items-center gap-2">
            <Button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || isLoading}
              variant="outline"
              size="sm"
            >
              Previous
            </Button>
            <span>
              {page} / {totalPages}
            </span>
            <Button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || isLoading}
              variant="outline"
              size="sm"
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
