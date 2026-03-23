"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { AppLayout } from "@/components/layout/app-layout"
import { Skeleton } from "@/components/ui/skeleton"
import { customInstance } from "@/lib/axios-instance"

// ---- Types -----------------------------------------------------------------

type ArtifactType = "BRIEF" | "SPEC" | "CLARIFY" | "PLAN" | "TASK" | "VALIDATE"
type ArtifactStatus = "draft" | "active" | "archived"

interface SddArtifact {
  id: string
  artifact_type: ArtifactType
  title: string
  status: ArtifactStatus
  file_path?: string
  content?: string
  created_at: string
  updated_at?: string
}

interface SddArtifactsResponse {
  items: SddArtifact[]
  total: number
}

// ---- Fetcher ----------------------------------------------------------------

const fetchArtifacts = (page: number, pageSize: number) =>
  customInstance<SddArtifactsResponse>({
    url: "/sdd-artifacts",
    method: "GET",
    params: { page, page_size: pageSize },
  })

// ---- Artifact type badge ---------------------------------------------------

const ARTIFACT_TYPE_STYLES: Record<ArtifactType, { bg: string; color: string }> = {
  BRIEF: { bg: "#3B82F61A", color: "#60A5FA" },
  SPEC: { bg: "#8B5CF61A", color: "#A78BFA" },
  CLARIFY: { bg: "#F973161A", color: "#FB923C" },
  PLAN: { bg: "#EAB3081A", color: "#FCD34D" },
  TASK: { bg: "#22C55E1A", color: "#4ADE80" },
  VALIDATE: { bg: "#14B8A61A", color: "#2DD4BF" },
}

function ArtifactTypeBadge({ type }: { type: ArtifactType }) {
  const style = ARTIFACT_TYPE_STYLES[type] ?? { bg: "#9CA3AF1A", color: "#9CA3AF" }
  return (
    <span
      className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold"
      style={{ backgroundColor: style.bg, color: style.color, border: `1px solid ${style.color}33` }}
    >
      {type}
    </span>
  )
}

// ---- Status badge ----------------------------------------------------------

function StatusBadge({ status }: { status: ArtifactStatus }) {
  const styles: Record<ArtifactStatus, { bg: string; color: string }> = {
    active: { bg: "#22C55E1A", color: "#4ADE80" },
    draft: { bg: "#9CA3AF1A", color: "#D1D5DB" },
    archived: { bg: "#6B72801A", color: "#9CA3AF" },
  }
  const s = styles[status] ?? styles.draft
  return (
    <span
      className="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium"
      style={{ backgroundColor: s.bg, color: s.color, border: `1px solid ${s.color}33` }}
    >
      {status}
    </span>
  )
}

// ---- Skeleton card ----------------------------------------------------------

function ArtifactSkeleton() {
  return (
    <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="h-5 w-12 rounded-full" />
      </div>
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-3 w-48" />
      <Skeleton className="h-3 w-32" />
    </div>
  )
}

// ---- Artifact row ----------------------------------------------------------

function ArtifactRow({
  artifact,
  onClick,
}: {
  artifact: SddArtifact
  onClick: () => void
}) {
  return (
    <div
      onClick={onClick}
      className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-2 cursor-pointer hover:bg-[hsl(var(--muted))]/20 transition-colors"
    >
      <div className="flex items-center gap-2 flex-wrap">
        <ArtifactTypeBadge type={artifact.artifact_type} />
        <StatusBadge status={artifact.status} />
        <span className="text-[11px] text-[hsl(var(--muted-foreground))] ml-auto">
          {new Date(artifact.created_at).toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </span>
      </div>
      <p className="text-sm font-medium text-[hsl(var(--foreground))] leading-snug">
        {artifact.title}
      </p>
      {artifact.file_path && (
        <p className="text-xs text-[hsl(var(--muted-foreground))] font-mono truncate">
          {artifact.file_path}
        </p>
      )}
    </div>
  )
}

// ---- Page ------------------------------------------------------------------

const PAGE_SIZE = 50

export default function SddPage() {
  const router = useRouter()
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ["sdd-artifacts", page],
    queryFn: () => fetchArtifacts(page, PAGE_SIZE),
  })

  const artifacts = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <AppLayout>
      <div className="flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
              SDD Artifacts
            </h1>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
              Subagent-Driven Development artifacts
            </p>
          </div>

          {/* Type legend */}
          <div className="flex items-center gap-1.5 flex-wrap">
            {(Object.keys(ARTIFACT_TYPE_STYLES) as ArtifactType[]).map((t) => (
              <ArtifactTypeBadge key={t} type={t} />
            ))}
          </div>
        </div>

        {/* Artifacts list */}
        {isLoading ? (
          <div className="flex flex-col gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <ArtifactSkeleton key={i} />
            ))}
          </div>
        ) : artifacts.length === 0 ? (
          <div className="flex items-center justify-center py-20">
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              No SDD artifacts found.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {artifacts.map((artifact) => (
              <ArtifactRow
                key={artifact.id}
                artifact={artifact}
                onClick={() => router.push(`/sdd/${artifact.id}`)}
              />
            ))}
          </div>
        )}

        {/* Pagination */}
        {!isLoading && total > 0 && (
          <div className="flex items-center justify-between text-sm text-[hsl(var(--muted-foreground))]">
            <span>
              {total} artifact{total !== 1 ? "s" : ""} total
            </span>
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
    </AppLayout>
  )
}
