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
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Clock3, LayoutGrid, List, Plus, Trash2, X } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
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

interface Task {
  id: string
  title: string
  description?: string
  status: "inbox" | "in_progress" | "done" | "cancelled"
  priority?: "critical" | "high" | "medium" | "low"
  assigned_agent_id?: string | null
  assigned_agent_slug?: string
  github_repo?: string
  github_issue_number?: number  // kept for backwards compat but not displayed
  label?: string
  workflow_state: string
  workflow_last_error?: string | null
  workflow_attempts: number
  created_at: string
}

interface TaskTimelineEvent {
  id: string
  event_type: string
  from_agent_slug?: string | null
  to_agent_slug?: string | null
  description: string
  created_at: string
  payload?: Record<string, unknown> | null
}

interface TaskTimelineResponse {
  items: TaskTimelineEvent[]
  total: number
}

interface Repository {
  id: string
  name: string
  full_name: string
  default_branch: string
  is_active: boolean
}

interface RepositoriesResponse {
  items: Repository[]
  total: number
}

interface TasksResponse {
  items: Task[]
  total: number
}

interface CreateTaskPayload {
  title: string
  description?: string
  priority?: string
  label?: string
  github_repo?: string
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

const deleteTask = (taskId: string) =>
  customInstance<void>({ url: `/tasks/${taskId}`, method: "DELETE" })

const fetchRepositories = () =>
  customInstance<RepositoriesResponse>({ url: "/repositories", method: "GET" })

const fetchTaskTimeline = (taskId: string) =>
  customInstance<TaskTimelineResponse>({ url: `/tasks/${taskId}/timeline`, method: "GET" })

// ---- Label constants --------------------------------------------------------

const LABELS = [
  { value: "", label: "(nenhum)" },
  { value: "back_end", label: "back_end" },
  { value: "front_end", label: "front_end" },
  { value: "mobile", label: "mobile" },
  { value: "tests", label: "tests" },
  { value: "devops", label: "devops" },
  { value: "dba", label: "dba" },
  { value: "security", label: "security" },
  { value: "ux", label: "ux" },
] as const

const LABEL_COLORS: Record<string, string> = {
  back_end: "#3B82F6",
  front_end: "#8B5CF6",
  mobile: "#EC4899",
  tests: "#10B981",
  devops: "#F59E0B",
  dba: "#6366F1",
  security: "#EF4444",
  ux: "#14B8A6",
}

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

function workflowLabel(workflowState: string) {
  const map: Record<string, string> = {
    queued_to_ceo: "Queued CEO",
    processing_by_ceo: "CEO Routing",
    forwarded_by_ceo: "Forwarded",
    completed: "Completed",
    failed: "Failed",
  }
  return map[workflowState] ?? workflowState
}

function workflowColor(workflowState: string) {
  const map: Record<string, string> = {
    queued_to_ceo: "#60A5FA",
    processing_by_ceo: "#FBBF24",
    forwarded_by_ceo: "#34D399",
    completed: "#34D399",
    failed: "#EF4444",
  }
  return map[workflowState] ?? "#9CA3AF"
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

// ---- Task Card (board) ------------------------------------------------------

function TaskCard({
  task,
  isDeleting,
  onDelete,
  onOpenTimeline,
}: {
  task: Task
  isDeleting: boolean
  onDelete: (task: Task) => void
  onOpenTimeline?: (task: Task) => void
}) {
  const wfColor = workflowColor(task.workflow_state)
  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-3 flex flex-col gap-2">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-medium text-[hsl(var(--foreground))] leading-snug">
          {task.title}
        </p>
        <button
          type="button"
          onClick={() => onDelete(task)}
          disabled={isDeleting}
          aria-label={`Delete task ${task.title}`}
          className="inline-flex h-6 w-6 items-center justify-center rounded-md text-red-400 hover:bg-red-500/10 hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
      {task.github_repo && (
        <p className="text-[10px] text-[hsl(var(--muted-foreground))] truncate">{task.github_repo}</p>
      )}
      <div className="flex items-center gap-1.5 flex-wrap">
        <span
          className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium"
          style={{
            backgroundColor: `${wfColor}1A`,
            color: wfColor,
            border: `1px solid ${wfColor}33`,
          }}
        >
          {workflowLabel(task.workflow_state)}
        </span>
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
        <div className="flex items-center gap-2">
          {task.label && (
            <span
              className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium"
              style={{
                backgroundColor: `${LABEL_COLORS[task.label] ?? "#9CA3AF"}1A`,
                color: LABEL_COLORS[task.label] ?? "#9CA3AF",
                border: `1px solid ${LABEL_COLORS[task.label] ?? "#9CA3AF"}33`,
              }}
            >
              {task.label}
            </span>
          )}
          <button
            type="button"
            onClick={() => onOpenTimeline?.(task)}
            disabled={!onOpenTimeline}
            className="inline-flex items-center gap-1 text-[10px] text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Clock3 className="h-3 w-3" />
            Timeline
          </button>
        </div>
      </div>
    </div>
  )
}

// ---- Board column -----------------------------------------------------------

function BoardColumn({
  status,
  tasks,
  loading,
  deletingTaskId,
  onDelete,
  onOpenTimeline,
}: {
  status: string
  tasks: Task[]
  loading: boolean
  deletingTaskId: string | null
  onDelete: (task: Task) => void
  onOpenTimeline?: (task: Task) => void
}) {
  const color = statusColor(status)
  return (
    <div className="flex flex-col flex-1 min-w-[200px]">
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
          tasks.map((t) => (
            <TaskCard
              key={t.id}
              task={t}
              isDeleting={deletingTaskId === t.id}
              onDelete={onDelete}
              onOpenTimeline={onOpenTimeline}
            />
          ))
        )}
      </div>
    </div>
  )
}

// ---- Create Task Dialog -----------------------------------------------------

function CreateTaskDialog({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [label, setLabel] = useState("")
  const [githubRepo, setGithubRepo] = useState("")
  const [error, setError] = useState("")

  const { data: reposData } = useQuery({
    queryKey: ["repositories"],
    queryFn: fetchRepositories,
  })
  const repos = reposData?.items ?? []

  const mutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => { onSuccess(); onClose() },
    onError: () => setError("Failed to create task. Please try again."),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) { setError("Title is required."); return }
    setError("")
    mutation.mutate({
      title: title.trim(),
      description: description.trim() || undefined,
      label: label || undefined,
      github_repo: githubRepo || undefined,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-[hsl(var(--foreground))]">Create Task</h2>
          <button onClick={onClose} className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]">
            <X className="h-4 w-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Title */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">
              Title <span className="text-red-400">*</span>
            </label>
            <Input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Task title…"
              className="h-10"
            />
          </div>

          {/* Label + Repo row */}
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Label / Track</label>
              <Select
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                className="h-10"
              >
                {LABELS.map((l) => (
                  <option key={l.value} value={l.value}>{l.label}</option>
                ))}
              </Select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Repositório</label>
              <Select
                value={githubRepo}
                onChange={(e) => setGithubRepo(e.target.value)}
                className="h-10"
              >
                <option value="">Selecionar…</option>
                {repos.map((r) => (
                  <option key={r.id} value={r.full_name}>{r.name}</option>
                ))}
              </Select>
            </div>
          </div>

          {/* Description */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description…"
              rows={4}
              className="px-3 py-2 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))] resize-none"
            />
          </div>

          {error && <p className="text-xs text-red-400">{error}</p>}
          <div className="flex items-center justify-end gap-2 mt-2">
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Creating…" : "Create"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function TimelineDialog({ task, onClose }: { task: Task; onClose: () => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ["task-timeline", task.id],
    queryFn: () => fetchTaskTimeline(task.id),
  })
  const events = data?.items ?? []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-2xl rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 shadow-xl max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-[hsl(var(--foreground))]">Task Timeline</h2>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">{task.title}</p>
          </div>
          <button onClick={onClose} className="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="overflow-y-auto pr-1">
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="rounded-lg border border-[hsl(var(--border))] p-3">
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="h-3 w-1/2 mt-2" />
                </div>
              ))}
            </div>
          ) : events.length === 0 ? (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">No timeline events found.</p>
          ) : (
            <div className="space-y-2">
              {events.map((event) => (
                <div key={event.id} className="rounded-lg border border-[hsl(var(--border))] p-3">
                  <div className="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))] mb-1">
                    <span>{event.event_type}</span>
                    <span>•</span>
                    <span>{new Date(event.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-sm text-[hsl(var(--foreground))]">{event.description}</p>
                  {(event.from_agent_slug || event.to_agent_slug) && (
                    <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
                      {event.from_agent_slug ? `@${event.from_agent_slug}` : "System"} →{" "}
                      {event.to_agent_slug ? `@${event.to_agent_slug}` : "System"}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ---- List view row skeleton -------------------------------------------------

function ListRowSkeleton() {
  return (
    <TableRow className="hover:bg-transparent">
      {Array.from({ length: 9 }).map((_, i) => (
        <TableCell key={i}>
          <Skeleton className="h-4 w-full" />
        </TableCell>
      ))}
    </TableRow>
  )
}

// ---- Page ------------------------------------------------------------------

const PAGE_SIZE = 50

export default function TasksPage() {
  const queryClient = useQueryClient()
  const [view, setView] = useState<"board" | "list">("board")
  const [showCreate, setShowCreate] = useState(false)
  const [listPage, setListPage] = useState(1)
  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null)
  const [timelineTask, setTimelineTask] = useState<Task | null>(null)

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

  const deleteMutation = useMutation({
    mutationFn: deleteTask,
    onMutate: (taskId) => setDeletingTaskId(taskId),
    onSettled: () => {
      setDeletingTaskId(null)
      invalidateAll()
    },
  })

  function handleDeleteTask(task: Task) {
    if (deleteMutation.isPending) return
    if (!confirm(`Excluir a task "${task.title}"?`)) return
    deleteMutation.mutate(task.id)
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
              <Button
                onClick={() => setView("board")}
                size="sm"
                variant={view === "board" ? "default" : "ghost"}
                className="rounded-none border-0"
              >
                <LayoutGrid className="h-3.5 w-3.5" />
                Board
              </Button>
              <Button
                onClick={() => setView("list")}
                size="sm"
                variant={view === "list" ? "default" : "ghost"}
                className="rounded-none border-0"
              >
                <List className="h-3.5 w-3.5" />
                List
              </Button>
            </div>

            <Button
              onClick={() => setShowCreate(true)}
              size="sm"
              className="h-9"
            >
              <Plus className="h-3.5 w-3.5" />
              Create Task
            </Button>
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
                deletingTaskId={deletingTaskId}
                onDelete={handleDeleteTask}
                onOpenTimeline={setTimelineTask}
              />
            ))}
          </div>
        )}

        {/* List view */}
        {view === "list" && (
          <>
            <Card className="overflow-hidden">
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-[hsl(var(--muted))]/30 hover:bg-[hsl(var(--muted))]/30">
                      <TableHead>
                        Title
                      </TableHead>
                      <TableHead>
                        Status
                      </TableHead>
                      <TableHead>
                        Priority
                      </TableHead>
                      <TableHead>
                        Agent
                      </TableHead>
                      <TableHead>
                        Workflow
                      </TableHead>
                      <TableHead>
                        Label
                      </TableHead>
                      <TableHead>
                        Repo
                      </TableHead>
                      <TableHead>
                        Created
                      </TableHead>
                      <TableHead>
                        Actions
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {listLoading ? (
                      Array.from({ length: 8 }).map((_, i) => <ListRowSkeleton key={i} />)
                    ) : listItems.length === 0 ? (
                      <TableRow className="hover:bg-transparent">
                        <TableCell
                          colSpan={9}
                          className="py-12 text-center text-sm text-[hsl(var(--muted-foreground))]"
                        >
                          No tasks found.
                        </TableCell>
                      </TableRow>
                    ) : (
                      listItems.map((task) => (
                        <TableRow
                          key={task.id}
                        >
                          <TableCell className="max-w-xs truncate font-medium text-[hsl(var(--foreground))]">
                            {task.title}
                          </TableCell>
                          <TableCell>
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
                          </TableCell>
                          <TableCell>
                            {task.priority ? (
                              <Badge variant={priorityVariant(task.priority)}>
                                {task.priority}
                              </Badge>
                            ) : (
                              <span className="text-[hsl(var(--muted-foreground))] text-xs">—</span>
                            )}
                          </TableCell>
                          <TableCell className="text-xs text-[hsl(var(--muted-foreground))]">
                            {task.assigned_agent_slug ?? "—"}
                          </TableCell>
                          <TableCell>
                            <div className="flex flex-col gap-1">
                              <span
                                className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium w-fit"
                                style={{
                                  backgroundColor: `${workflowColor(task.workflow_state)}1A`,
                                  color: workflowColor(task.workflow_state),
                                  border: `1px solid ${workflowColor(task.workflow_state)}33`,
                                }}
                              >
                                {workflowLabel(task.workflow_state)}
                              </span>
                              {task.workflow_last_error && (
                                <span className="text-[10px] text-red-400 truncate max-w-[180px]" title={task.workflow_last_error}>
                                  {task.workflow_last_error}
                                </span>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            {task.label ? (
                              <span
                                className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                                style={{
                                  backgroundColor: `${LABEL_COLORS[task.label] ?? "#9CA3AF"}1A`,
                                  color: LABEL_COLORS[task.label] ?? "#9CA3AF",
                                  border: `1px solid ${LABEL_COLORS[task.label] ?? "#9CA3AF"}33`,
                                }}
                              >
                                {task.label}
                              </span>
                            ) : (
                              <span className="text-[hsl(var(--muted-foreground))] text-xs">—</span>
                            )}
                          </TableCell>
                          <TableCell className="max-w-[120px] truncate text-xs text-[hsl(var(--muted-foreground))]">
                            {task.github_repo ?? "—"}
                          </TableCell>
                          <TableCell className="text-xs text-[hsl(var(--muted-foreground))]">
                            {formatDate(task.created_at)}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-3">
                              <button
                                type="button"
                                onClick={() => setTimelineTask(task)}
                                className="inline-flex items-center gap-1 text-xs text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
                              >
                                <Clock3 className="h-3.5 w-3.5" />
                                Timeline
                              </button>
                              <button
                                type="button"
                                onClick={() => handleDeleteTask(task)}
                                disabled={deleteMutation.isPending}
                                className="inline-flex items-center gap-1 text-xs text-red-400 hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                                {deletingTaskId === task.id ? "Excluindo..." : "Excluir"}
                              </button>
                            </div>
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
                {listLoading ? "Loading…" : `${listTotal} task${listTotal !== 1 ? "s" : ""} total`}
              </span>
              <div className="flex items-center gap-2">
                <Button
                  onClick={() => setListPage((p) => Math.max(1, p - 1))}
                  disabled={listPage <= 1 || listLoading}
                  variant="outline"
                  size="sm"
                >
                  Previous
                </Button>
                <span>
                  {listPage} / {listTotalPages}
                </span>
                <Button
                  onClick={() => setListPage((p) => Math.min(listTotalPages, p + 1))}
                  disabled={listPage >= listTotalPages || listLoading}
                  variant="outline"
                  size="sm"
                >
                  Next
                </Button>
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
      {timelineTask && (
        <TimelineDialog task={timelineTask} onClose={() => setTimelineTask(null)} />
      )}
    </AppLayout>
  )
}
