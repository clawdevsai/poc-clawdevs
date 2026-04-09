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

import { useEffect, useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { CheckCircle, XCircle, RefreshCw, Shield } from "lucide-react"
import { AppLayout } from "@/components/layout/app-layout"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { customInstance } from "@/lib/axios-instance"
import { cn } from "@/lib/utils"
import {
  getRuntimeSettings,
  updateRuntimeSettings,
} from "@/lib/monitoring-api"

// ---- Types ----------------------------------------------------------------

interface SettingsInfo {
  gateway_url: string
  cluster_namespace: string
  container_version: string
}

interface ClusterInfo {
  cluster_name?: string
  namespace: string
  version: string
}

interface GatewayHealth {
  status: string
}

interface Repository {
  id: string
  name: string
  full_name: string
  description?: string
  default_branch: string
  is_active: boolean
}

interface RepositoriesResponse {
  items: Repository[]
  total: number
}

interface CreateRepoPayload {
  name: string
  full_name: string
  description?: string
  default_branch: string
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

const fetchRepositories = () =>
  customInstance<RepositoriesResponse>({
    url: "/repositories?include_inactive=true",
    method: "GET",
  })

const createRepository = (body: CreateRepoPayload) =>
  customInstance<Repository>({ url: "/repositories", method: "POST", data: body })

const updateRepository = (id: string, body: Partial<Repository>) =>
  customInstance<Repository>({ url: `/repositories/${id}`, method: "PATCH", data: body })

const deleteRepository = (id: string) =>
  customInstance<void>({ url: `/repositories/${id}`, method: "DELETE" })

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

function SectionDivider({ title, description }: { title: string; description?: string }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wide whitespace-nowrap">
          {title}
        </span>
        <div className="flex-1 h-px bg-[hsl(var(--border))]" />
      </div>
      {description && (
        <p className="text-xs text-[hsl(var(--muted-foreground))]">
          {description}
        </p>
      )}
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

function RepositoriesSection() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: "", full_name: "", description: "", default_branch: "main" })
  const [formError, setFormError] = useState("")

  const { data, isLoading } = useQuery({
    queryKey: ["repositories"],
    queryFn: fetchRepositories,
  })

  const createMutation = useMutation({
    mutationFn: createRepository,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["repositories"] })
      setShowForm(false)
      setForm({ name: "", full_name: "", description: "", default_branch: "main" })
      setFormError("")
    },
    onError: () => setFormError("Falha ao criar repositório."),
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      updateRepository(id, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["repositories"] }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteRepository,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["repositories"] }),
  })

  const repos = data?.items ?? []

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-[hsl(var(--foreground))]">Repositórios cadastrados</span>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="px-3 py-1.5 text-xs rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 transition-opacity"
        >
          + Adicionar repositório
        </button>
      </div>

      {showForm && (
        <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 flex flex-col gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs text-[hsl(var(--muted-foreground))]">Nome *</label>
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="ClawDevs API"
                className="px-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-[hsl(var(--muted-foreground))]">org/repo *</label>
              <input
                value={form.full_name}
                onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
                placeholder="myorg/myrepo"
                className="px-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-[hsl(var(--muted-foreground))]">Branch default</label>
              <input
                value={form.default_branch}
                onChange={(e) => setForm((f) => ({ ...f, default_branch: e.target.value }))}
                placeholder="main"
                className="px-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-xs text-[hsl(var(--muted-foreground))]">Descrição</label>
              <input
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="Opcional"
                className="px-3 py-1.5 text-sm rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-1 focus:ring-[hsl(var(--primary))]"
              />
            </div>
          </div>
          {formError && <p className="text-xs text-red-400">{formError}</p>}
          <div className="flex gap-2 justify-end">
            <button
              onClick={() => { setShowForm(false); setFormError("") }}
              className="px-3 py-1.5 text-xs rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--muted))]/30"
            >
              Cancelar
            </button>
            <button
              onClick={() => {
                if (!form.name.trim() || !form.full_name.trim()) {
                  setFormError("Nome e org/repo são obrigatórios.")
                  return
                }
                createMutation.mutate({
                  name: form.name.trim(),
                  full_name: form.full_name.trim(),
                  description: form.description.trim() || undefined,
                  default_branch: form.default_branch.trim() || "main",
                })
              }}
              disabled={createMutation.isPending}
              className="px-3 py-1.5 text-xs rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50"
            >
              {createMutation.isPending ? "Salvando…" : "Salvar"}
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="text-xs text-[hsl(var(--muted-foreground))]">Carregando…</div>
      ) : repos.length === 0 ? (
        <div className="text-xs text-[hsl(var(--muted-foreground))]">Nenhum repositório cadastrado.</div>
      ) : (
        <div className="flex flex-col gap-2">
          {repos.map((repo) => (
            <div
              key={repo.id}
              className="flex items-center justify-between rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-2.5"
            >
              <div className="flex flex-col">
                <span className="text-sm font-medium text-[hsl(var(--foreground))]">{repo.name}</span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {repo.full_name} · {repo.default_branch}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleMutation.mutate({ id: repo.id, is_active: !repo.is_active })}
                  className={`px-2 py-0.5 text-xs rounded-full transition-colors ${
                    repo.is_active
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      : "bg-[hsl(var(--muted))]/30 text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/50"
                  }`}
                >
                  {repo.is_active ? "Ativo" : "Inativo"}
                </button>
                <button
                  onClick={() => {
                    if (confirm(`Remover "${repo.name}"?`)) deleteMutation.mutate(repo.id)
                  }}
                  className="text-xs text-red-400 hover:text-red-300 transition-colors"
                >
                  Remover
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
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

  const { data: runtimeSettings, isLoading: runtimeLoading } = useQuery({
    queryKey: ["runtime-settings"],
    queryFn: getRuntimeSettings,
  })

  const [runtimeForm, setRuntimeForm] = useState({
    modelProvider: "",
    modelName: "",
    limitsJson: "",
    flagsJson: "",
    thresholdsJson: "",
    agentUpdatesJson: "",
    confirmText: "",
  })
  const [runtimeFeedback, setRuntimeFeedback] = useState<{
    type: "success" | "error"
    message: string
  } | null>(null)

  useEffect(() => {
    if (!runtimeSettings) return
    setRuntimeForm((prev) => ({
      ...prev,
      modelProvider: runtimeSettings.model_provider ?? "",
      modelName: runtimeSettings.model_name ?? "",
      limitsJson: JSON.stringify(runtimeSettings.limits ?? {}, null, 2),
      flagsJson: JSON.stringify(runtimeSettings.flags ?? {}, null, 2),
      thresholdsJson: JSON.stringify(runtimeSettings.thresholds ?? {}, null, 2),
      agentUpdatesJson: JSON.stringify(runtimeSettings.agent_updates ?? [], null, 2),
    }))
  }, [runtimeSettings])

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

  const runtimeMutation = useMutation({
    mutationFn: updateRuntimeSettings,
    onSuccess: () => {
      setRuntimeFeedback({
        type: "success",
        message: "Runtime settings updated.",
      })
    },
    onError: (err: unknown) => {
      const msg =
        err instanceof Error ? err.message : "Failed to update runtime settings."
      setRuntimeFeedback({ type: "error", message: msg })
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

  function parseJsonInput(value: string, label: string) {
    const trimmed = value.trim()
    if (!trimmed) return undefined
    try {
      return JSON.parse(trimmed)
    } catch {
      throw new Error(`${label} JSON is invalid.`)
    }
  }

  function handleRuntimeSubmit(e: React.FormEvent) {
    e.preventDefault()
    setRuntimeFeedback(null)
    try {
      const payload = {
        model_provider: runtimeForm.modelProvider || undefined,
        model_name: runtimeForm.modelName || undefined,
        limits: parseJsonInput(runtimeForm.limitsJson, "Limits"),
        flags: parseJsonInput(runtimeForm.flagsJson, "Flags"),
        thresholds: parseJsonInput(runtimeForm.thresholdsJson, "Thresholds"),
        agent_updates: parseJsonInput(
          runtimeForm.agentUpdatesJson,
          "Agent updates"
        ),
        confirm_text: runtimeForm.confirmText || undefined,
      }
      runtimeMutation.mutate(payload)
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Invalid runtime payload."
      setRuntimeFeedback({ type: "error", message: msg })
    }
  }

  return (
    <AppLayout>
      <div className="max-w-5xl w-full mx-auto flex flex-col gap-8">
        {/* Header */}
        <div>
          <h1 className="text-xl font-semibold text-[hsl(var(--foreground))]">
            Configurações
          </h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-0.5">
            Gerencie conta, conexão com gateway, cluster e repositórios.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4">
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">Conta e Segurança</p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">Atualize sua senha e valide dados do seu acesso atual.</p>
          </div>
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4">
            <p className="text-sm font-medium text-[hsl(var(--foreground))]">Gateway e Cluster</p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">Verifique conectividade e os metadados do Kubernetes em uso.</p>
          </div>
        </div>

        {/* ── Account ─────────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <SectionDivider
            title="Conta"
            description="Informações do usuário autenticado e troca de senha."
          />

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
              Alterar senha
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mb-3">
              Recomendado trocar periodicamente para manter seu acesso seguro.
            </p>
            <form
              onSubmit={handleChangePassword}
              className="flex flex-col gap-3"
            >
              <input
                type="password"
                placeholder="Senha atual"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className={inputClass}
                required
              />
              <input
                type="password"
                placeholder="Nova senha"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className={inputClass}
                required
              />
              <input
                type="password"
                placeholder="Confirmar nova senha"
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
                {pwMutation.isPending ? "Salvando…" : "Atualizar senha"}
              </button>
            </form>
          </div>
        </div>

        {/* ── Gateway ─────────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <SectionDivider
            title="Gateway"
            description="Endpoint usado para comunicação com o OpenClaw."
          />

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
                Testar conexão
              </button>
              {gatewayStatus === "ok" && (
                <span className="flex items-center gap-1.5 text-xs text-green-400">
                  <CheckCircle className="h-3.5 w-3.5" /> Conectado
                </span>
              )}
              {gatewayStatus === "error" && (
                <span className="flex items-center gap-1.5 text-xs text-red-400">
                  <XCircle className="h-3.5 w-3.5" /> Indisponível
                </span>
              )}
            </div>
          </FieldRow>
        </div>

        {/* ── Cluster Info ─────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <SectionDivider
            title="Cluster Info"
            description="Metadados do cluster e namespace usados pelo painel."
          />

          {clusterLoading ? (
            <div className="flex flex-col gap-3">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-4 w-36" />
              <Skeleton className="h-4 w-32" />
            </div>
          ) : (
            <>
              {clusterInfo?.cluster_name && (
                <FieldRow label="Nome do cluster">
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
              <FieldRow label="Versão Kubernetes">
                <ReadOnlyValue
                  value={
                    clusterInfo?.version ??
                    settingsInfo?.container_version ??
                    "—"
                  }
                />
              </FieldRow>
            </>
          )}
        </div>

        {/* ── Runtime Settings ─────────────────────────────────────────── */}
        <div className="flex flex-col gap-4 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <SectionDivider
            title="Runtime Settings"
            description="Atualize limites, flags e modelos com confirmações obrigatórias."
          />
          <form onSubmit={handleRuntimeSubmit} className="flex flex-col gap-4">
            <FieldRow label="Model Provider">
              {runtimeLoading ? (
                <Skeleton className="h-4 w-40" />
              ) : (
                <input
                  className={inputClass}
                  value={runtimeForm.modelProvider}
                  onChange={(e) =>
                    setRuntimeForm((prev) => ({
                      ...prev,
                      modelProvider: e.target.value,
                    }))
                  }
                  placeholder="ollama"
                />
              )}
            </FieldRow>

            <FieldRow label="Model Name">
              <input
                className={inputClass}
                value={runtimeForm.modelName}
                onChange={(e) =>
                  setRuntimeForm((prev) => ({
                    ...prev,
                    modelName: e.target.value,
                  }))
                }
                placeholder="phi4-mini-reasoning:latest"
              />
            </FieldRow>

            <FieldRow label="Limits (JSON)">
              <textarea
                className={`${inputClass} min-h-[120px] font-mono`}
                value={runtimeForm.limitsJson}
                onChange={(e) =>
                  setRuntimeForm((prev) => ({
                    ...prev,
                    limitsJson: e.target.value,
                  }))
                }
              />
            </FieldRow>

            <FieldRow label="Flags (JSON)">
              <textarea
                className={`${inputClass} min-h-[120px] font-mono`}
                value={runtimeForm.flagsJson}
                onChange={(e) =>
                  setRuntimeForm((prev) => ({
                    ...prev,
                    flagsJson: e.target.value,
                  }))
                }
              />
            </FieldRow>

            <FieldRow label="Thresholds (JSON)">
              <textarea
                className={`${inputClass} min-h-[120px] font-mono`}
                value={runtimeForm.thresholdsJson}
                onChange={(e) =>
                  setRuntimeForm((prev) => ({
                    ...prev,
                    thresholdsJson: e.target.value,
                  }))
                }
              />
            </FieldRow>

            <FieldRow label="Agent Updates (JSON)">
              <textarea
                className={`${inputClass} min-h-[120px] font-mono`}
                value={runtimeForm.agentUpdatesJson}
                onChange={(e) =>
                  setRuntimeForm((prev) => ({
                    ...prev,
                    agentUpdatesJson: e.target.value,
                  }))
                }
              />
            </FieldRow>

            <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--muted))]/10 p-3 text-sm text-[hsl(var(--muted-foreground))] space-y-2">
              <p>
                This will switch inference provider for all agents. Type CONFIRM
                to proceed.
              </p>
              <p>
                This will remove the agent from active scheduling. Type DISABLE
                to proceed.
              </p>
              <p>
                This may affect runtime stability. Type CONFIRM to proceed.
              </p>
            </div>

            <FieldRow label="Confirm Text">
              <input
                className={inputClass}
                value={runtimeForm.confirmText}
                onChange={(e) =>
                  setRuntimeForm((prev) => ({
                    ...prev,
                    confirmText: e.target.value,
                  }))
                }
                placeholder="CONFIRM or DISABLE"
              />
            </FieldRow>

            {runtimeFeedback && (
              <div
                className={cn(
                  "text-sm",
                  runtimeFeedback.type === "success"
                    ? "text-green-400"
                    : "text-red-400"
                )}
              >
                {runtimeFeedback.message}
              </div>
            )}

            <button
              type="submit"
              className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-[hsl(var(--primary))] text-sm font-semibold text-white hover:bg-[hsl(var(--primary))]/90 transition-colors"
            >
              Apply Runtime Settings
            </button>
          </form>
        </div>

        {/* ── Tokens ───────────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <SectionDivider
            title="Sessão e Token"
            description="Dados da sessão autenticada e ação de logout seguro."
          />

          <FieldRow label="Expiração do JWT">
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
              Revogar e sair
            </button>
          </FieldRow>
        </div>

        {/* ── Repositories ─────────────────────────────────────────────── */}
        <div className="flex flex-col gap-4 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <SectionDivider
            title="Repositórios"
            description="Cadastre repositórios para habilitar operações dos agentes."
          />
          <RepositoriesSection />
        </div>
      </div>
    </AppLayout>
  )
}
