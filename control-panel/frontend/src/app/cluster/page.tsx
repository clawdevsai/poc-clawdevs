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

import { useQuery } from "@tanstack/react-query"
import { useEffect, useMemo, useState } from "react"
import { formatDistanceToNow } from "date-fns"
import { RefreshCw } from "lucide-react"
import type { AxiosError } from "axios"
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

interface ApiErrorResponse {
  detail?: string
}

interface ApiPod {
  name?: string
  namespace?: string
  status?: string
  ready?: boolean
  restarts?: number
  age?: string
}

interface ApiPVC {
  name?: string
  namespace?: string
  status?: string
  capacity?: string
  storage_class?: string
  age?: string
}

interface ApiEvent {
  type?: string
  reason?: string
  message?: string
  object?: string
  involved_object?: string
  last_seen?: string
  last_timestamp?: string
}

// ---- Fetchers -------------------------------------------------------------

const fetchPods = async (): Promise<Pod[]> => {
  const data = await customInstance<ApiPod[] | { items?: ApiPod[] }>({
    url: "/cluster/pods",
    method: "GET",
  })
  const items = Array.isArray(data) ? data : (data.items ?? [])
  return items.map((p) => ({
    name: p.name ?? "—",
    namespace: p.namespace ?? "—",
    status: p.status ?? "Unknown",
    ready: p.ready === undefined ? "—" : p.ready ? "Ready" : "Not Ready",
    restarts: p.restarts ?? 0,
    age: p.age ?? "—",
  }))
}

const fetchPVCs = async (): Promise<PVC[]> => {
  const data = await customInstance<ApiPVC[] | { items?: ApiPVC[] }>({
    url: "/cluster/pvcs",
    method: "GET",
  })
  const items = Array.isArray(data) ? data : (data.items ?? [])
  return items.map((p) => ({
    name: p.name ?? "—",
    namespace: p.namespace ?? "default",
    status: p.status ?? "Unknown",
    capacity: p.capacity ?? "—",
    storage_class: p.storage_class ?? "—",
    age: p.age ?? "—",
  }))
}

const fetchEvents = async (): Promise<K8sEvent[]> => {
  const data = await customInstance<ApiEvent[] | { items?: ApiEvent[] }>({
    url: "/cluster/events",
    method: "GET",
  })
  const items = Array.isArray(data) ? data : (data.items ?? [])
  return items.map((e) => ({
    type: e.type ?? "Normal",
    reason: e.reason ?? "—",
    message: e.message ?? "—",
    object: e.object ?? e.involved_object ?? "—",
    last_seen: e.last_seen ?? e.last_timestamp ?? "—",
  }))
}

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

function getErrorMessage(error: unknown): string {
  const axiosError = error as AxiosError<ApiErrorResponse>
  const detail = axiosError?.response?.data?.detail
  if (detail) return detail
  if (axiosError?.message) return axiosError.message
  return "Unable to load Kubernetes data."
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
const EVENTS_PER_PAGE = 10

export default function ClusterPage() {
  const [eventsPage, setEventsPage] = useState(1)

  const {
    data: podsData,
    isLoading: podsLoading,
    isError: podsIsError,
    error: podsError,
    dataUpdatedAt: podsUpdated,
  } = useQuery({
    queryKey: ["cluster-pods"],
    queryFn: fetchPods,
    refetchInterval: REFETCH_INTERVAL,
  })

  const {
    data: pvcsData,
    isLoading: pvcsLoading,
    isError: pvcsIsError,
    error: pvcsError,
    dataUpdatedAt: pvcsUpdated,
  } = useQuery({
    queryKey: ["cluster-pvcs"],
    queryFn: fetchPVCs,
    refetchInterval: REFETCH_INTERVAL,
  })

  const {
    data: eventsData,
    isLoading: eventsLoading,
    isError: eventsIsError,
    error: eventsError,
    dataUpdatedAt: eventsUpdated,
  } = useQuery({
    queryKey: ["cluster-events"],
    queryFn: fetchEvents,
    refetchInterval: REFETCH_INTERVAL,
  })

  const pods = podsData ?? []
  const pvcs = pvcsData ?? []
  const events = eventsData ?? []
  const totalEventPages = Math.max(1, Math.ceil(events.length / EVENTS_PER_PAGE))

  useEffect(() => {
    if (eventsPage > totalEventPages) {
      setEventsPage(totalEventPages)
    }
  }, [eventsPage, totalEventPages])

  const pagedEvents = useMemo(() => {
    const start = (eventsPage - 1) * EVENTS_PER_PAGE
    return events.slice(start, start + EVENTS_PER_PAGE)
  }, [events, eventsPage])

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
                  ) : podsIsError ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="px-4 py-10 text-center text-sm text-red-400"
                      >
                        {getErrorMessage(podsError)}
                      </td>
                    </tr>
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
                  ) : pvcsIsError ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="px-4 py-10 text-center text-sm text-red-400"
                      >
                        {getErrorMessage(pvcsError)}
                      </td>
                    </tr>
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
                  ) : eventsIsError ? (
                    <tr>
                      <td
                        colSpan={5}
                        className="px-4 py-10 text-center text-sm text-red-400"
                      >
                        {getErrorMessage(eventsError)}
                      </td>
                    </tr>
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
                    pagedEvents.map((event, i) => (
                      <tr
                        key={`${eventsPage}-${i}-${event.reason}-${event.last_seen}`}
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
            {!eventsLoading && !eventsIsError && events.length > 0 && (
              <div className="flex items-center justify-between border-t border-[hsl(var(--border))] px-4 py-3">
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  Showing {(eventsPage - 1) * EVENTS_PER_PAGE + 1}-
                  {Math.min(eventsPage * EVENTS_PER_PAGE, events.length)} of {events.length}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setEventsPage((p) => Math.max(1, p - 1))}
                    disabled={eventsPage <= 1}
                    className="px-2.5 py-1 text-xs rounded-md border border-[hsl(var(--border))] text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/30 disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-xs text-[hsl(var(--muted-foreground))]">
                    Page {eventsPage} of {totalEventPages}
                  </span>
                  <button
                    type="button"
                    onClick={() => setEventsPage((p) => Math.min(totalEventPages, p + 1))}
                    disabled={eventsPage >= totalEventPages}
                    className="px-2.5 py-1 text-xs rounded-md border border-[hsl(var(--border))] text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/30 disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
