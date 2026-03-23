"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { LayoutGrid, List, Plus, X, ExternalLink } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { customInstance } from "@/lib/axios-instance"

// ---- Types -----------------------------------------------------------------

interface Task {
  id: string
  title: string
  description?: string
  status: "inbox" | "in_progress" | "done" | "cancelled"
  priority?: "critical" | "high" | "medium" | "low"
  assigned_agent_slug?: string
  github_issue_number?: number
  created_at: string
}

interface TasksResponse {
  items: Task[]
  total: number
}

interface CreateTaskPayload {
  title: string
  description?: string
  priority?: string
  assigned_agent_slug?: string
}

// ---- Fetchers ---------------------------------------------------------------

const STATUSES = ["inbox", "in_progress", "done", "cancelled"] as const

const fetchTasks = (status?: string, page = 1, pageSize = 50) =>
  customInstance<TasksResponse>({
    url: "/tasks",
    method: "GET",
    params: { ...(status ? { status } : {}), page, page_size: pageSize },
  })

const createTask = (payload: CreateTaskPayload) =>
  customInstance<Task>({ url: "/tasks", method: "POST", data: payload })

// ---- Badge helpers ----------------------------------------------------------

function priorityVariant(p?: string): "error" | "warning" | "secondary" | "outline" | "default" {
  if (p === "critical") return "error"
  if (p === "high") return "warning"
  if (p === "medium") return "secondary"
  return "outline"
}

function statusColor(status: string) {
  const map: Record<string, string> = {
    inbox: "#60A5FA",
    in_progress: "#FBBF24",
    done: "#34D399",
    cancelled: "#9CA3AF",
  }
  return map[status] ?? "#9CA3AF"
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    inbox: "Inbox",
    in_progress: "In Progress",
    done: "Done",
    cancelled: "Cancelled",
  }
  return map[status] ?? status
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

// ---- Task Card (board) ------------------------------------------------------

function TaskCard({ task }: { task: Task }) {
  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-3 flex flex-col gap-2">
      <p className="text-sm font-medium text-[hsl(var(--foreground))] leading-snug">
        {task.title}
      </p>
      <div className="flex items-center gap-1.5 flex-wrap">
        {task.priority && (
          <Badge variant={priorityVariant(task.priority)} className="text-[10px] px-1.5 py-0">
            {task.priority}
          </Badge>
        )}
        {task.assigned_agent_slug && (
          <span className="text-[11px] text-[hsl(var(--muted-foreground))]">
            @{task.assigned_agent_slug}
          </span>
        )}
      </div>
      <div className="flex items-center justify-between mt-auto">
        <span className="text-[11px] text-[hsl(var(--muted-foreground))]">
          {formatDate(task.created_at)}
        </span>
        {task.github_issue_number && (
          <a
            href={`https://github.com/issues/${task.github_issue_number}`}
            target="_blank"
            rel="noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300"
          >
            #{task.github_issue_number}
            <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>
    </div>
  )
}

// ---- Board column -----------------------------------------------------------

function BoardColumn({ status, tasks, loading }: { status: string; tasks: Task[]; loading: boolean }) {
  const color = statusColor(status)
  return (
    <div className="flex flex-col min-w-0 flex-1 min-w-[200px]">
      <div className="flex items-center gap-2 mb-3">
        <h3 className="text-sm font-semibold" style={{ color }}>
          {statusLabel(status)}
        </h3>
        {!loading && (
          <span
            className="inline-flex items-center justify-center rounded-full px-2 py-0.5 text-xs font-medium"
            style={{
              backgroundColor: `${color}1A`,
              color,
              border: `1px solid ${color}33`,
            }}
          >
            {tasks.length}
          </span>
        )}
      </div>
      <div className="flex flex-col gap-2 overflow-y-auto max-h-[calc(100vh-280px)] pr-0.5">
        {loading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-3 flex flex-col gap-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-3 w-20" />
            </div>
          ))
        ) : tasks.length === 0 ? (
          <div className="flex items-center justify-center py-10">
            <p className="text-xs text-[hsl(var(--muted-foreground))]">Empty</p>
          </div>
        ) : (
          tasks.map((t) => <TaskCard key={t.id} task={t} />)
        )}
      </div>
    </div>
  )
}

// ---- Create Task Dialog -----------------------------------------------------

function CreateTaskDialog({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [error, setError] = useState("")

  const mutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      onSuccess()
      onClose()
    },
    onError: () => {
      setError("Failed to create task. Please try again.")
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) {
      setError("Title is required.")
      return
    }
    setError("")
    mutation.mutate({ title: title.trim(), description: description.trim() || undefined })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-[hsl(var(--foreground))]">
            Create Task
          </h2>
          <button
            onClick={onClose}
            className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">
              Title <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Task title…"
              className="px-3 py-2 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description…"
              rows={4}
              className="px-3 py-2 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))] resize-none"
            />
          </div>
          {error && (
            <p className="text-xs text-red-400">{error}</p>
          )}
          <div className="flex items-center justify-end gap-2 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-lg border border-[hsl(var(--border))] text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/30 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="px-4 py-2 text-sm rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {mutation.isPending ? "Creating…" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ---- List view row skeleton -------------------------------------------------

function ListRowSkeleton() {
  return (
    <tr className="border-b border-[hsl(var(--border))]">
      {Array.from({ length: 6 }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  )
}

// ---- Page ------------------------------------------------------------------

const PAGE_SIZE = 50

export default function TasksPage() {
  const queryClient = useQueryClient()
  const [view, setView] = useState<"board" | "list">("board")
  const [showCreate, setShowCreate] = useState(false)
  const [listPage, setListPage] = useState(1)

  // Board: fetch all statuses (four separate hooks — no conditional/loop hooks)
  const inboxQuery = useQuery({
    queryKey: ["tasks", "inbox"],
    queryFn: () => fetchTasks("inbox"),
  })
  const inProgressQuery = useQuery({
    queryKey: ["tasks", "in_progress"],
    queryFn: () => fetchTasks("in_progress"),
  })
  const doneQuery = useQuery({
    queryKey: ["tasks", "done"],
    queryFn: () => fetchTasks("done"),
  })
  const cancelledQuery = useQuery({
    queryKey: ["tasks", "cancelled"],
    queryFn: () => fetchTasks("cancelled"),
  })

  const boardQueries: Record<string, { data?: TasksResponse; isLoading: boolean }> = {
    inbox: inboxQuery,
    in_progress: inProgressQuery,
    done: doneQuery,
    cancelled: cancelledQuery,
  }

  // List: fetch all tasks, no status filter
  const { data: listData, isLoading: listLoading } = useQuery({
    queryKey: ["tasks", "all", listPage],
    queryFn: () => fetchTasks(undefined, listPage, PAGE_SIZE),
    enabled: view === "list",
  })

  const listItems = listData?.items ?? []
  const listTotal = listData?.total ?? 0
  const listTotalPages = Math.max(1, Math.ceil(listTotal / PAGE_SIZE))

  function invalidateAll() {
    queryClient.invalidateQueries({ queryKey: ["tasks"] })
  }

  return (
    <AppLayout>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">Tasks</h1>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
              Manage and track agent tasks
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* View toggle */}
            <div className="flex rounded-lg border border-[hsl(var(--border))] overflow-hidden">
              <button
                onClick={() => setView("board")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-sm transition-colors ${
                  view === "board"
                    ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                    : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/30"
                }`}
              >
                <LayoutGrid className="h-3.5 w-3.5" />
                Board
              </button>
              <button
                onClick={() => setView("list")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-sm transition-colors ${
                  view === "list"
                    ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                    : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/30"
                }`}
              >
                <List className="h-3.5 w-3.5" />
                List
              </button>
            </div>

            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 transition-opacity"
            >
              <Plus className="h-3.5 w-3.5" />
              Create Task
            </button>
          </div>
        </div>

        {/* Board view */}
        {view === "board" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {STATUSES.map((status) => (
              <BoardColumn
                key={status}
                status={status}
                tasks={boardQueries[status].data?.items ?? []}
                loading={boardQueries[status].isLoading}
              />
            ))}
          </div>
        )}

        {/* List view */}
        {view === "list" && (
          <>
            <div className="rounded-xl border border-[hsl(var(--border))] overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30">
                      <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                        Title
                      </th>
                      <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                        Status
                      </th>
                      <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                        Priority
                      </th>
                      <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                        Agent
                      </th>
                      <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                        Issue
                      </th>
                      <th className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                        Created
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {listLoading ? (
                      Array.from({ length: 8 }).map((_, i) => <ListRowSkeleton key={i} />)
                    ) : listItems.length === 0 ? (
                      <tr>
                        <td
                          colSpan={6}
                          className="px-4 py-12 text-center text-sm text-[hsl(var(--muted-foreground))]"
                        >
                          No tasks found.
                        </td>
                      </tr>
                    ) : (
                      listItems.map((task) => (
                        <tr
                          key={task.id}
                          className="border-b border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/20 transition-colors"
                        >
                          <td className="px-4 py-3 font-medium text-[hsl(var(--foreground))] max-w-xs truncate">
                            {task.title}
                          </td>
                          <td className="px-4 py-3">
                            <span
                              className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                              style={{
                                backgroundColor: `${statusColor(task.status)}1A`,
                                color: statusColor(task.status),
                                border: `1px solid ${statusColor(task.status)}33`,
                              }}
                            >
                              {statusLabel(task.status)}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            {task.priority ? (
                              <Badge variant={priorityVariant(task.priority)}>
                                {task.priority}
                              </Badge>
                            ) : (
                              <span className="text-[hsl(var(--muted-foreground))] text-xs">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-[hsl(var(--muted-foreground))] text-xs">
                            {task.assigned_agent_slug ?? "—"}
                          </td>
                          <td className="px-4 py-3">
                            {task.github_issue_number ? (
                              <a
                                href={`https://github.com/issues/${task.github_issue_number}`}
                                target="_blank"
                                rel="noreferrer"
                                className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                              >
                                #{task.github_issue_number}
                                <ExternalLink className="h-3 w-3" />
                              </a>
                            ) : (
                              <span className="text-[hsl(var(--muted-foreground))] text-xs">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))]">
                            {formatDate(task.created_at)}
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
                {listLoading ? "Loading…" : `${listTotal} task${listTotal !== 1 ? "s" : ""} total`}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setListPage((p) => Math.max(1, p - 1))}
                  disabled={listPage <= 1 || listLoading}
                  className="px-3 py-1 rounded-lg border border-[hsl(var(--border))] disabled:opacity-40 hover:bg-[hsl(var(--muted))]/30 transition-colors"
                >
                  Previous
                </button>
                <span>
                  {listPage} / {listTotalPages}
                </span>
                <button
                  onClick={() => setListPage((p) => Math.min(listTotalPages, p + 1))}
                  disabled={listPage >= listTotalPages || listLoading}
                  className="px-3 py-1 rounded-lg border border-[hsl(var(--border))] disabled:opacity-40 hover:bg-[hsl(var(--muted))]/30 transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {showCreate && (
        <CreateTaskDialog
          onClose={() => setShowCreate(false)}
          onSuccess={invalidateAll}
        />
      )}
    </AppLayout>
  )
}
