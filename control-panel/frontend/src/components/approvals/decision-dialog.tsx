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
import * as Dialog from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Badge } from "@/components/ui/badge"
import { customInstance } from "@/lib/axios-instance"
import type { Approval } from "./types"

interface DecideBody {
  decision: "approved" | "rejected"
  justification?: string
}

const postDecision = (id: string, body: DecideBody) =>
  customInstance<void>({
    url: `/approvals/${id}/decide`,
    method: "POST",
    data: body,
  })

interface DecisionDialogProps {
  approval: Approval | null
  decision: "approved" | "rejected"
  open: boolean
  onClose: () => void
}

export function DecisionDialog({
  approval,
  decision,
  open,
  onClose,
}: DecisionDialogProps) {
  const queryClient = useQueryClient()
  const [justification, setJustification] = useState("")
  const [error, setError] = useState<string | null>(null)

  const isReject = decision === "rejected"

  const mutation = useMutation({
    mutationFn: () =>
      postDecision(approval!.id, {
        decision,
        justification: justification.trim() || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["approvals"] })
      queryClient.invalidateQueries({ queryKey: ["approvals-stats"] })
      queryClient.invalidateQueries({ queryKey: ["approvals-pending-count"] })
      setJustification("")
      setError(null)
      onClose()
    },
    onError: () => {
      setError("Falha ao enviar decisão. Por favor, tente novamente.")
    },
  })

  function handleConfirm() {
    if (!approval) return
    if (isReject && !justification.trim()) {
      setError("A justificativa é obrigatória ao rejeitar.")
      return
    }
    setError(null)
    mutation.mutate()
  }

  function resetAndClose() {
    setJustification("")
    setError(null)
    onClose()
  }

  function handleOpenChange(open: boolean) {
    if (!open) resetAndClose()
  }

  if (!approval) return null

  const description =
    approval.payload?.description ??
    approval.payload?.action_type ??
    "Sem descrição"

  const rubricEntries = approval.rubric_scores
    ? Object.entries(approval.rubric_scores)
    : []

  return (
    <Dialog.Root open={open} onOpenChange={handleOpenChange}>
      <Dialog.Portal>
        {/* Overlay */}
        <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" />

        {/* Content */}
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 shadow-2xl focus:outline-none">
          {/* Close */}
          <Dialog.Close asChild>
            <button
              onClick={resetAndClose}
              className="absolute right-4 top-4 rounded-sm opacity-70 hover:opacity-100 transition-opacity"
              aria-label="Fechar"
            >
              <X className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
            </button>
          </Dialog.Close>

          {/* Title */}
          <Dialog.Title className="text-base font-semibold text-[hsl(var(--foreground))] mb-1">
            {isReject ? "Rejeitar Solicitação" : "Aprovar Solicitação"}
          </Dialog.Title>

          <Dialog.Description className="text-xs text-[hsl(var(--muted-foreground))] mb-4">
            Agente:{" "}
            <span className="text-[hsl(var(--foreground))] font-mono">
              {approval.agent_id}
            </span>
          </Dialog.Description>

          {/* Request description */}
          <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] p-3 mb-4">
            <p className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider mb-1">
              Solicitação
            </p>
            <p className="text-sm text-[hsl(var(--foreground))]">
              {description}
            </p>
          </div>

          {/* Rubric scores */}
          {rubricEntries.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider mb-2">
                Critérios de Avaliação
              </p>
              <div className="flex flex-wrap gap-1.5">
                {rubricEntries.map(([key, value]) => (
                  <Badge key={key} variant="outline" className="text-xs gap-1">
                    <span className="text-[hsl(var(--muted-foreground))]">
                      {key}
                    </span>
                    <span
                      className={
                        typeof value === "number" && value >= 0.7
                          ? "text-green-400"
                          : typeof value === "number" && value >= 0.4
                          ? "text-yellow-400"
                          : "text-red-400"
                      }
                    >
                      {typeof value === "number"
                        ? (value * 100).toFixed(0) + "%"
                        : String(value)}
                    </span>
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Justification textarea */}
          <div className="mb-4">
            <label className="block text-xs font-medium text-[hsl(var(--muted-foreground))] uppercase tracking-wider mb-1.5">
              Justificativa{isReject && <span className="text-red-400 ml-1">*</span>}
            </label>
            <textarea
              value={justification}
              onChange={(e) => {
                setJustification(e.target.value)
                if (error) setError(null)
              }}
              placeholder={
                isReject
                  ? "Explique por que esta solicitação está sendo rejeitada…"
                  : "Opcional: adicione uma observação sobre esta aprovação…"
              }
              rows={3}
              aria-required={isReject}
              className="w-full rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2 text-sm text-[hsl(var(--foreground))] placeholder:text-[hsl(var(--muted-foreground))] outline-none focus:border-[hsl(var(--primary))] resize-none transition-colors"
            />
            {error && (
              <p className="mt-1 text-xs text-red-400">{error}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-2 justify-end">
            <button
              onClick={resetAndClose}
              disabled={mutation.isPending}
              className="px-4 py-2 rounded-lg text-sm border border-[hsl(var(--border))] text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:border-[hsl(var(--foreground)/0.3)] transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleConfirm}
              disabled={mutation.isPending}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50 ${
                isReject
                  ? "bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30"
                  : "bg-[#00FF9C]/20 text-[#00FF9C] border border-[#00FF9C]/30 hover:bg-[#00FF9C]/30"
              }`}
            >
              {mutation.isPending
                ? "Enviando…"
                : isReject
                ? "Confirmar Rejeição"
                : "Confirmar Aprovação"}
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
