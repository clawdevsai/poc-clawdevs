"use client"

import { useQuery } from "@tanstack/react-query"
import { useParams, useRouter } from "next/navigation"
import ReactMarkdown from "react-markdown"
import { ArrowLeft } from "lucide-react"
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

// ---- Fetcher ----------------------------------------------------------------

const fetchArtifact = (id: string) =>
  customInstance<SddArtifact>({ url: `/sdd-artifacts/${id}`, method: "GET" })

// ---- Artifact type badge ---------------------------------------------------

const ARTIFACT_TYPE_STYLES: Record<ArtifactType, { bg: string; color: string }> = {
  BRIEF: { bg: "#3B82F61A", color: "#60A5FA" },
  SPEC: { bg: "#8B5CF61A", color: "#A78BFA" },
  CLARIFY: { bg: "#F974161A", color: "#FB923C" },
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

function StatusBadge({ status }: { status: ArtifactStatus }) {
  const styles: Record<ArtifactStatus, { bg: string; color: string }> = {
    active: { bg: "#22C55E1A", color: "#4ADE80" },
    draft: { bg: "#9CA3AF1A", color: "#D1D5DB" },
    archived: { bg: "#6B72801A", color: "#9CA3AF" },
  }
  const s = styles[status] ?? styles.draft
  return (
    <span
      className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
      style={{ backgroundColor: s.bg, color: s.color, border: `1px solid ${s.color}33` }}
    >
      {status}
    </span>
  )
}

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

// ---- Page ------------------------------------------------------------------

export default function SddArtifactDetailPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()

  const { data: artifact, isLoading } = useQuery({
    queryKey: ["sdd-artifact", id],
    queryFn: () => fetchArtifact(id),
    enabled: !!id,
  })

  return (
    <AppLayout>
      <div className="flex flex-col gap-6 max-w-4xl">
        {/* Back */}
        <button
          onClick={() => router.push("/sdd")}
          className="flex items-center gap-1.5 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors w-fit"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to SDD
        </button>

        {/* Metadata */}
        {isLoading ? (
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 flex flex-col gap-4">
            <div className="flex items-center gap-2">
              <Skeleton className="h-5 w-16 rounded-full" />
              <Skeleton className="h-5 w-12 rounded-full" />
            </div>
            <Skeleton className="h-6 w-64" />
            <div className="grid grid-cols-2 gap-3">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
            </div>
          </div>
        ) : artifact ? (
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 flex flex-col gap-4">
            <div className="flex items-center gap-2 flex-wrap">
              <ArtifactTypeBadge type={artifact.artifact_type} />
              <StatusBadge status={artifact.status} />
            </div>
            <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">
              {artifact.title}
            </h1>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Type</p>
                <p className="font-medium text-[hsl(var(--foreground))]">
                  {artifact.artifact_type}
                </p>
              </div>
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Status</p>
                <p className="font-medium text-[hsl(var(--foreground))]">
                  {artifact.status}
                </p>
              </div>
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Created</p>
                <p className="text-xs text-[hsl(var(--foreground))]">
                  {formatDate(artifact.created_at)}
                </p>
              </div>
              {artifact.updated_at && (
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">Updated</p>
                  <p className="text-xs text-[hsl(var(--foreground))]">
                    {formatDate(artifact.updated_at)}
                  </p>
                </div>
              )}
              {artifact.file_path && (
                <div className="col-span-2 sm:col-span-4">
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mb-0.5">File Path</p>
                  <p className="text-xs font-mono text-[hsl(var(--foreground))] break-all">
                    {artifact.file_path}
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">Artifact not found.</p>
        )}

        {/* Content */}
        {!isLoading && artifact && (
          <div className="flex flex-col gap-3">
            <h2 className="text-sm font-semibold text-[hsl(var(--foreground))]">Content</h2>
            {artifact.content ? (
              <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
                <div className="prose prose-invert prose-sm max-w-none text-[hsl(var(--foreground))]">
                  <ReactMarkdown>{artifact.content}</ReactMarkdown>
                </div>
              </div>
            ) : (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">
                No content available for this artifact.
              </p>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
