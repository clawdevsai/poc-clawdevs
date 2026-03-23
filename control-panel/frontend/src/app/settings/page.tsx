"use client"

import { useState } from "react"
import { useQuery, useMutation } from "@tanstack/react-query"
import { CheckCircle, XCircle, RefreshCw, Shield } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { customInstance } from "@/lib/axios-instance"

// ---- Types ----------------------------------------------------------------

interface SettingsInfo {
  gateway_url: string
  cluster_namespace: string
  k8s_version: string
}

interface ClusterInfo {
  cluster_name?: string
  namespace: string
  k8s_version: string
}

interface GatewayHealth {
  status: string
}

// ---- Fetchers / Mutators --------------------------------------------------

const fetchSettingsInfo = () =>
  customInstance<SettingsInfo>({ url: "/settings/info", method: "GET" })

const fetchClusterInfo = () =>
  customInstance<ClusterInfo>({ url: "/cluster/info", method: "GET" })

const checkGatewayHealth = () =>
  customInstance<GatewayHealth>({
    url: "/settings/gateway-health",
    method: "GET",
  })

const changePassword = (body: {
  current_password: string
  new_password: string
}) =>
  customInstance<unknown>({
    url: "/auth/change-password",
    method: "POST",
    data: body,
  })

// ---- Helpers --------------------------------------------------------------

function decodeJwtPayload(
  token: string
): { sub?: string; role?: string; exp?: number } | null {
  try {
    const parts = token.split(".")
    if (parts.length < 2) return null
    const payload = atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"))
    return JSON.parse(payload)
  } catch {
    return null
  }
}

function SectionDivider({ title }: { title: string }) {
  return (
    <div className="flex items-center gap-3 py-2">
      <span className="text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wide whitespace-nowrap">
        {title}
      </span>
      <div className="flex-1 h-px bg-[hsl(var(--border))]" />
    </div>
  )
}

function FieldRow({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-4">
      <span className="text-sm text-[hsl(var(--muted-foreground))] sm:w-44 shrink-0">
        {label}
      </span>
      <div className="flex-1">{children}</div>
    </div>
  )
}

function ReadOnlyValue({ value }: { value: string }) {
  return (
    <span className="font-mono text-sm text-[hsl(var(--foreground))] break-all">
      {value}
    </span>
  )
}

// ---- Page -----------------------------------------------------------------

export default function SettingsPage() {
  // JWT payload for account section
  const [jwtPayload] = useState(() => {
    if (typeof window === "undefined") return null
    const token = localStorage.getItem("panel_token")
    return token ? decodeJwtPayload(token) : null
  })

  // Change password form
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [pwFeedback, setPwFeedback] = useState<{
    type: "success" | "error"
    message: string
  } | null>(null)

  // Gateway health state
  const [gatewayStatus, setGatewayStatus] = useState<
    "idle" | "checking" | "ok" | "error"
  >("idle")

  const { data: settingsInfo, isLoading: settingsLoading } = useQuery({
    queryKey: ["settings-info"],
    queryFn: fetchSettingsInfo,
  })

  const { data: clusterInfo, isLoading: clusterLoading } = useQuery({
    queryKey: ["cluster-info"],
    queryFn: fetchClusterInfo,
  })

  const pwMutation = useMutation({
    mutationFn: changePassword,
    onSuccess: () => {
      setPwFeedback({ type: "success", message: "Password changed successfully." })
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
    },
    onError: (err: unknown) => {
      const msg =
        err instanceof Error ? err.message : "Failed to change password."
      setPwFeedback({ type: "error", message: msg })
    },
  })

  function handleChangePassword(e: React.FormEvent) {
    e.preventDefault()
    setPwFeedback(null)
    if (newPassword !== confirmPassword) {
      setPwFeedback({ type: "error", message: "New passwords do not match." })
      return
    }
    if (newPassword.length < 6) {
      setPwFeedback({
        type: "error",
        message: "New password must be at least 6 characters.",
      })
      return
    }
    pwMutation.mutate({
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  async function handleGatewayTest() {
    setGatewayStatus("checking")
    try {
      await checkGatewayHealth()
      setGatewayStatus("ok")
    } catch {
      setGatewayStatus("error")
    }
  }

  const tokenExpiry = jwtPayload?.exp
    ? new Date(jwtPayload.exp * 1000).toLocaleString()
    : null

  const inputClass =
    "w-full px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))] transition-colors"

  return (
    <AppLayout>
      <div className="max-w-2xl flex flex-col gap-8">
        {/* Header */}
        <div>
          <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
            Settings
          </h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
            System configuration and account management
          </p>
        </div>

        {/* ── Account ─────────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4">
          <SectionDivider title="Account" />

          <FieldRow label="Username">
            <ReadOnlyValue value={jwtPayload?.sub ?? "—"} />
          </FieldRow>

          <FieldRow label="Role">
            {jwtPayload?.role ? (
              <Badge variant="default" className="w-fit">
                <Shield className="h-3 w-3 mr-1" />
                {jwtPayload.role}
              </Badge>
            ) : (
              <span className="text-sm text-[hsl(var(--muted-foreground))]">
                —
              </span>
            )}
          </FieldRow>

          {/* Change password form */}
          <div className="pt-2">
            <p className="text-sm font-medium text-[hsl(var(--foreground))] mb-3">
              Change Password
            </p>
            <form
              onSubmit={handleChangePassword}
              className="flex flex-col gap-3"
            >
              <input
                type="password"
                placeholder="Current password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className={inputClass}
                required
              />
              <input
                type="password"
                placeholder="New password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className={inputClass}
                required
              />
              <input
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={inputClass}
                required
              />

              {pwFeedback && (
                <div
                  className={`flex items-center gap-2 text-sm px-3 py-2 rounded-lg ${
                    pwFeedback.type === "success"
                      ? "bg-green-500/10 text-green-400"
                      : "bg-red-500/10 text-red-400"
                  }`}
                >
                  {pwFeedback.type === "success" ? (
                    <CheckCircle className="h-4 w-4 shrink-0" />
                  ) : (
                    <XCircle className="h-4 w-4 shrink-0" />
                  )}
                  {pwFeedback.message}
                </div>
              )}

              <button
                type="submit"
                disabled={pwMutation.isPending}
                className="self-start px-4 py-2 text-sm rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50 transition-opacity"
              >
                {pwMutation.isPending ? "Saving…" : "Update Password"}
              </button>
            </form>
          </div>
        </div>

        {/* ── Gateway ─────────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4">
          <SectionDivider title="Gateway" />

          <FieldRow label="Gateway URL">
            {settingsLoading ? (
              <Skeleton className="h-4 w-64" />
            ) : (
              <ReadOnlyValue value={settingsInfo?.gateway_url ?? "—"} />
            )}
          </FieldRow>

          <FieldRow label="Connection">
            <div className="flex items-center gap-3">
              <button
                onClick={handleGatewayTest}
                disabled={gatewayStatus === "checking"}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border border-[hsl(var(--border))] text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]/30 disabled:opacity-50 transition-colors"
              >
                {gatewayStatus === "checking" ? (
                  <RefreshCw className="h-3 w-3 animate-spin" />
                ) : (
                  <RefreshCw className="h-3 w-3" />
                )}
                Test Connection
              </button>
              {gatewayStatus === "ok" && (
                <span className="flex items-center gap-1.5 text-xs text-green-400">
                  <CheckCircle className="h-3.5 w-3.5" /> Healthy
                </span>
              )}
              {gatewayStatus === "error" && (
                <span className="flex items-center gap-1.5 text-xs text-red-400">
                  <XCircle className="h-3.5 w-3.5" /> Unreachable
                </span>
              )}
            </div>
          </FieldRow>
        </div>

        {/* ── Cluster Info ─────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4">
          <SectionDivider title="Cluster Info" />

          {clusterLoading ? (
            <div className="flex flex-col gap-3">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-4 w-36" />
              <Skeleton className="h-4 w-32" />
            </div>
          ) : (
            <>
              {clusterInfo?.cluster_name && (
                <FieldRow label="Cluster Name">
                  <ReadOnlyValue value={clusterInfo.cluster_name} />
                </FieldRow>
              )}
              <FieldRow label="Namespace">
                <ReadOnlyValue
                  value={
                    clusterInfo?.namespace ??
                    settingsInfo?.cluster_namespace ??
                    "—"
                  }
                />
              </FieldRow>
              <FieldRow label="Kubernetes Version">
                <ReadOnlyValue
                  value={
                    clusterInfo?.k8s_version ??
                    settingsInfo?.k8s_version ??
                    "—"
                  }
                />
              </FieldRow>
            </>
          )}
        </div>

        {/* ── Tokens ───────────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4">
          <SectionDivider title="Tokens" />

          <FieldRow label="JWT Expiry">
            <ReadOnlyValue value={tokenExpiry ?? "—"} />
          </FieldRow>

          <FieldRow label="Subject (sub)">
            <ReadOnlyValue value={jwtPayload?.sub ?? "—"} />
          </FieldRow>

          <FieldRow label="Token">
            <button
              onClick={() => {
                if (typeof window !== "undefined") {
                  localStorage.removeItem("panel_token")
                  window.location.href = "/login"
                }
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors"
            >
              <XCircle className="h-3.5 w-3.5" />
              Revoke &amp; Sign Out
            </button>
          </FieldRow>
        </div>
      </div>
    </AppLayout>
  )
}
