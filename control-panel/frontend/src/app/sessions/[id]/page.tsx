"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useParams, useRouter } from "next/navigation"
import ReactMarkdown from "react-markdown"
import { ChevronDown, ChevronRight, ArrowLeft, Wrench } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { customInstance } from "@/lib/axios-instance"

// ---- Types -----------------------------------------------------------------

interface ToolCall {
  id?: string
  name?: string
  tool?: string
  result?: string
  input?: unknown
}

interface Message {
  role: "user" | "assistant" | "system" | "tool"
  content: string
  tool_calls?: ToolCall[]
}

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
  messages?: Message[]
}

// ---- Fetcher ----------------------------------------------------------------

const fetchSession = (id: string) =>
  customInstance<Session>({ url: `/sessions/${id}`, method: "GET" })

// ---- Helpers ----------------------------------------------------------------

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function statusVariant(status: string): "success" | "warning" | "error" | "secondary" {
  if (status === "active") return "success"
  if (status === "ended") return "secondary"
  if (status === "error") return "error"
  return "secondary"
}

// ---- Tool call collapsible -------------------------------------------------

function ToolCallItem({ call }: { call: ToolCall }) {
  const [open, setOpen] = useState(false)
  const name = call.name ?? call.tool ?? "tool_call"
  const resultText =
    typeof call.result === "string"
      ? call.result.slice(0, 200) + (call.result.length > 200 ? "…" : "")
      : call.result
        ? JSON.stringify(call.result).slice(0, 200)
        : "—"

  return (
    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--muted))]/10 text-sm">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 w-full px-3 py-2 text-left hover:bg-[hsl(var(--muted))]/20 transition-colors rounded-lg"
      >
        <Wrench className="h-3.5 w-3.5 text-[hsl(var(--muted-foreground))] shrink-0" />
        <span className="font-mono text-xs text-[hsl(var(--foreground))] flex-1 truncate">
          {name}
        </span>
        {open ? (
          <ChevronDown className="h-3.5 w-3.5 text-[hsl(var(--muted-foreground))]" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5 text-[hsl(var(--muted-foreground))]" />
        )}
      </button>
      {open && (
        <div className="px-3 pb-3 flex flex-col gap-2">
          {call.input !== undefined && (
            <div>
              <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1 font-medium uppercase tracking-wide">
                Input
              </p>
              <pre className="text-xs text-[hsl(var(--foreground))] bg-[hsl(var(--muted))]/30 rounded p-2 overflow-x-auto whitespace-pre-wrap break-all">
                {typeof call.input === "string"
                  ? call.input
                  : JSON.stringify(call.input, null, 2)}
              </pre>
            </div>
          )}
          <div>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1 font-medium uppercase tracking-wide">
              Result
            </p>
            <pre className="text-xs text-[hsl(var(--foreground))] bg-[hsl(var(--muted))]/30 rounded p-2 overflow-x-auto whitespace-pre-wrap break-all">
              {resultText}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

// ---- Message bubble --------------------------------------------------------

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user"
  const isSystem = message.role === "system"

  const roleColor = isUser
    ? "#60A5FA"
    : isSystem
      ? "#9CA3AF"
      : "#A78BFA"

  const roleLabel = message.role.charAt(0).toUpperCase() + message.role.slice(1)

  return (
    <div className="flex flex-col gap-2">
      <span
        className="text-xs font-semibold uppercase tracking-wide"
        style={{ color: roleColor }}
      >
        {roleLabel}
      </span>
      {message.content && (
        <div className="prose prose-invert prose-sm max-w-none text-[hsl(var(--foreground))]">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
      )}
      {message.tool_calls && message.tool_calls.length > 0 && (
        <div className="flex flex-col gap-1.5 mt-1">
          {message.tool_calls.map((call, i) => (
            <ToolCallItem key={call.id ?? i} call={call} />
          ))}
        </div>
      )}
    </div>
  )
}

// ---- Page ------------------------------------------------------------------

export default function SessionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()

  const { data: session, isLoading } = useQuery({
    queryKey: ["session", id],
    queryFn: () => fetchSession(id),
    enabled: !!id,
  })

  return (
    <AppLayout>
      <div className="flex flex-col gap-6 max-w-4xl">
        {/* Back */}
        <button
          onClick={() => router.push("/sessions")}
          className="flex items-center gap-1.5 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors w-fit"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Sessions
        </button>

        {/* Metadata header */}
        {isLoading ? (
          <div className="flex flex-col gap-3">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-72" />
          </div>
        ) : session ? (
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 flex flex-col gap-4">
            <div className="flex items-start justify-between flex-wrap gap-3">
              <div>
                <p className="font-mono text-xs text-[hsl(var(--muted-foreground))] mb-1">
                  Session
                </p>
                <h1 className="text-base font-semibold text-[hsl(var(--foreground))] font-mono break-all">
                  {session.openclaw_session_id ?? session.id}
                </h1>
              </div>
              <Badge variant={statusVariant(session.status)}>{session.status}</Badge>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Agent</p>
                <p className="font-medium text-[hsl(var(--foreground))]">
                  {session.agent_slug}
                </p>
              </div>
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Channel</p>
                <p className="font-medium text-[hsl(var(--foreground))]">
                  {session.channel_type}
                </p>
              </div>
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Messages</p>
                <p className="font-medium text-[hsl(var(--foreground))]">
                  {session.message_count ?? 0}
                </p>
              </div>
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Tokens</p>
                <p className="font-medium text-[hsl(var(--foreground))]">
                  {(session.token_count ?? 0).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Started</p>
                <p className="text-xs text-[hsl(var(--foreground))]">
                  {formatDate(session.started_at)}
                </p>
              </div>
              {session.ended_at && (
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Ended</p>
                  <p className="text-xs text-[hsl(var(--foreground))]">
                    {formatDate(session.ended_at)}
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Session not found.</p>
        )}

        {/* Conversation */}
        {!isLoading && session && (
          <div className="flex flex-col gap-1">
            <h2 className="text-sm font-semibold text-[hsl(var(--foreground))] mb-3">
              Conversation
            </h2>
            {(session.messages ?? []).length === 0 ? (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                No messages recorded for this session.
              </p>
            ) : (
              <div className="flex flex-col gap-5">
                {(session.messages ?? []).map((msg, i) => (
                  <div
                    key={i}
                    className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4"
                  >
                    <MessageBubble message={msg} />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
