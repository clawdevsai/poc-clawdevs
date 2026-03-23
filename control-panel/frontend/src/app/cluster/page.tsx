"use client"

import { useQuery } from "@tanstack/react-query"
import { formatDistanceToNow } from "date-fns"
import { RefreshCw } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { customInstance } from "@/lib/axios-instance"

// ---- Types ----------------------------------------------------------------

interface Pod {
  name: string
  namespace: string
  status: string
  ready: string
  restarts: number
  age: string
}

interface PVC {
  name: string
  namespace: string
  status: string
  capacity: string
  storage_class: string
  age: string
}

interface K8sEvent {
  type: string
  reason: string
  message: string
  object: string
  last_seen: string
}

interface PodsResponse {
  items: Pod[]
}

interface PVCsResponse {
  items: PVC[]
}

interface EventsResponse {
  items: K8sEvent[]
}

// ---- Fetchers -------------------------------------------------------------

const fetchPods = () =>
  customInstance<PodsResponse>({ url: "/cluster/pods", method: "GET" })

const fetchPVCs = () =>
  customInstance<PVCsResponse>({ url: "/cluster/pvcs", method: "GET" })

const fetchEvents = () =>
  customInstance<EventsResponse>({ url: "/cluster/events", method: "GET" })

// ---- Helpers --------------------------------------------------------------

function podStatusVariant(
  status: string
): "success" | "warning" | "error" | "secondary" {
  switch (status) {
    case "Running":
      return "success"
    case "Pending":
      return "warning"
    case "Failed":
      return "error"
    default:
      return "secondary"
  }
}

function pvcStatusVariant(status: string): "success" | "warning" | "secondary" {
  switch (status) {
    case "Bound":
      return "success"
    case "Pending":
      return "warning"
    default:
      return "secondary"
  }
}

function eventTypeVariant(type: string): "warning" | "secondary" {
  return type === "Warning" ? "warning" : "secondary"
}

// ---- Sub-components -------------------------------------------------------

function TableSkeleton({
  cols,
  rows = 4,
}: {
  cols: number
  rows?: number
}) {
  return (
    <>
      {Array.from({ length: rows }).map((_, i) => (
        <tr key={i} className="border-b border-[hsl(var(--border))]">
          {Array.from({ length: cols }).map((_, j) => (
            <td key={j} className="px-4 py-3">
              <Skeleton className="h-4 w-full" />
            </td>
          ))}
        </tr>
      ))}
    </>
  )
}

function SectionHeader({
  title,
  count,
  isLoading,
  lastUpdated,
}: {
  title: string
  count?: number
  isLoading: boolean
  lastUpdated?: Date
}) {
  return (
    <div className="flex items-center justify-between">
      <h2 className="text-base font-semibold text-[hsl(var(--foreground))]">
        {title}
        {!isLoading && count !== undefined && (
          <span className="ml-2 text-sm font-normal text-[hsl(var(--muted-foreground))]">
            ({count})
          </span>
        )}
      </h2>
      {lastUpdated && (
        <span className="flex items-center gap-1.5 text-xs text-[hsl(var(--muted-foreground))]">
          <RefreshCw className="h-3 w-3" />
          Updated{" "}
          {formatDistanceToNow(lastUpdated, { addSuffix: true })}
        </span>
      )}
    </div>
  )
}

// ---- Page -----------------------------------------------------------------

const REFETCH_INTERVAL = 30_000

export default function ClusterPage() {
  const {
    data: podsData,
    isLoading: podsLoading,
    dataUpdatedAt: podsUpdated,
  } = useQuery({
    queryKey: ["cluster-pods"],
    queryFn: fetchPods,
    refetchInterval: REFETCH_INTERVAL,
  })

  const {
    data: pvcsData,
    isLoading: pvcsLoading,
    dataUpdatedAt: pvcsUpdated,
  } = useQuery({
    queryKey: ["cluster-pvcs"],
    queryFn: fetchPVCs,
    refetchInterval: REFETCH_INTERVAL,
  })

  const {
    data: eventsData,
    isLoading: eventsLoading,
    dataUpdatedAt: eventsUpdated,
  } = useQuery({
    queryKey: ["cluster-events"],
    queryFn: fetchEvents,
    refetchInterval: REFETCH_INTERVAL,
  })

  const pods = podsData?.items ?? []
  const pvcs = pvcsData?.items ?? []
  const events = eventsData?.items ?? []

  return (
    <AppLayout>
      <div className="flex flex-col gap-8">
        {/* Header */}
        <div>
          <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
            Cluster Status
          </h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
            Kubernetes resources — auto-refreshes every 30s
          </p>
        </div>

        {/* Pods table */}
        <div className="flex flex-col gap-3">
          <SectionHeader
            title="Pods"
            count={pods.length}
            isLoading={podsLoading}
            lastUpdated={podsUpdated ? new Date(podsUpdated) : undefined}
          />
          <div className="rounded-xl border border-[hsl(var(--border))] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30">
                    {["Name", "Namespace", "Status", "Ready", "Restarts", "Age"].map(
                      (h) => (
                        <th
                          key={h}
                          className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide"
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {podsLoading ? (
                    <TableSkeleton cols={6} />
                  ) : pods.length === 0 ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="px-4 py-10 text-center text-sm text-[hsl(var(--muted-foreground))]"
                      >
                        No pods found.
                      </td>
                    </tr>
                  ) : (
                    pods.map((pod) => (
                      <tr
                        key={pod.name}
                        className="border-b border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/10 transition-colors"
                      >
                        <td className="px-4 py-3 font-mono text-xs text-[hsl(var(--foreground))] max-w-[240px] truncate">
                          {pod.name}
                        </td>
                        <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))]">
                          {pod.namespace}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={podStatusVariant(pod.status)}>
                            {pod.status}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-xs tabular-nums text-[hsl(var(--foreground))]">
                          {pod.ready}
                        </td>
                        <td className="px-4 py-3 text-xs tabular-nums text-[hsl(var(--foreground))]">
                          {pod.restarts}
                        </td>
                        <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))]">
                          {pod.age}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* PVCs table */}
        <div className="flex flex-col gap-3">
          <SectionHeader
            title="Persistent Volume Claims"
            count={pvcs.length}
            isLoading={pvcsLoading}
            lastUpdated={pvcsUpdated ? new Date(pvcsUpdated) : undefined}
          />
          <div className="rounded-xl border border-[hsl(var(--border))] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30">
                    {["Name", "Namespace", "Status", "Capacity", "Storage Class", "Age"].map(
                      (h) => (
                        <th
                          key={h}
                          className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide"
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {pvcsLoading ? (
                    <TableSkeleton cols={6} />
                  ) : pvcs.length === 0 ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="px-4 py-10 text-center text-sm text-[hsl(var(--muted-foreground))]"
                      >
                        No PVCs found.
                      </td>
                    </tr>
                  ) : (
                    pvcs.map((pvc) => (
                      <tr
                        key={pvc.name}
                        className="border-b border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/10 transition-colors"
                      >
                        <td className="px-4 py-3 font-mono text-xs text-[hsl(var(--foreground))] max-w-[200px] truncate">
                          {pvc.name}
                        </td>
                        <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))]">
                          {pvc.namespace}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={pvcStatusVariant(pvc.status)}>
                            {pvc.status}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-xs tabular-nums text-[hsl(var(--foreground))]">
                          {pvc.capacity}
                        </td>
                        <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))]">
                          {pvc.storage_class}
                        </td>
                        <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))]">
                          {pvc.age}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Events table */}
        <div className="flex flex-col gap-3">
          <SectionHeader
            title="Recent Events"
            count={events.length}
            isLoading={eventsLoading}
            lastUpdated={eventsUpdated ? new Date(eventsUpdated) : undefined}
          />
          <div className="rounded-xl border border-[hsl(var(--border))] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[hsl(var(--border))] bg-[hsl(var(--muted))]/30">
                    {["Type", "Reason", "Object", "Message", "Last Seen"].map(
                      (h) => (
                        <th
                          key={h}
                          className="px-4 py-2.5 text-left text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wide"
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {eventsLoading ? (
                    <TableSkeleton cols={5} rows={3} />
                  ) : events.length === 0 ? (
                    <tr>
                      <td
                        colSpan={5}
                        className="px-4 py-10 text-center text-sm text-[hsl(var(--muted-foreground))]"
                      >
                        No events found.
                      </td>
                    </tr>
                  ) : (
                    events.map((event, i) => (
                      <tr
                        key={i}
                        className="border-b border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/10 transition-colors"
                      >
                        <td className="px-4 py-3">
                          <Badge variant={eventTypeVariant(event.type)}>
                            {event.type}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-xs font-medium text-[hsl(var(--foreground))]">
                          {event.reason}
                        </td>
                        <td className="px-4 py-3 font-mono text-xs text-[hsl(var(--muted-foreground))] max-w-[160px] truncate">
                          {event.object}
                        </td>
                        <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))] max-w-[320px]">
                          {event.message}
                        </td>
                        <td className="px-4 py-3 text-xs text-[hsl(var(--muted-foreground))] whitespace-nowrap">
                          {event.last_seen}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
