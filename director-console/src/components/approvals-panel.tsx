"use client";

import { useEffect, useMemo, useState, useTransition } from "react";

import type { ApprovalItem } from "@/lib/server/types";

type ApprovalsPanelProps = {
  pendingItems: ApprovalItem[];
  onChanged?: () => void;
};

type ActionState = {
  message: string | null;
  isPending: boolean;
};

export function ApprovalsPanel({ pendingItems, onChanged }: ApprovalsPanelProps) {
  const [pending, setPending] = useState(pendingItems);
  const [actionState, setActionState] = useState<ActionState>({ message: null, isPending: false });
  const [isTransitionPending, startTransition] = useTransition();

  const isBusy = actionState.isPending || isTransitionPending;

  const grouped = useMemo(() => pending, [pending]);

  useEffect(() => {
    setPending(pendingItems);
  }, [pendingItems]);

  const refresh = async () => {
    const response = await fetch("/api/approvals");
    const payload = (await response.json()) as { pending?: ApprovalItem[]; error?: string };
    if (!response.ok) {
      setActionState({ message: payload.error ?? "approvals_error", isPending: false });
      return;
    }
    setPending(payload.pending ?? []);
    setActionState({ message: null, isPending: false });
    onChanged?.();
  };

  const runAction = (action: "approve" | "deny", key: string) => {
    setActionState({ message: null, isPending: true });
    startTransition(async () => {
      const response = await fetch("/api/approvals", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ action, key })
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) {
        setActionState({ message: payload.error ?? "approvals_action_error", isPending: false });
        return;
      }
      await refresh();
    });
  };

  return (
    <div className="panel panel-strong rounded-3xl p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-white">Aprovacoes pendentes</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Itens aguardando autorizacao humana (UI e Telegram).
        </p>
      </div>
      {grouped.length === 0 ? (
        <p className="text-sm text-[var(--muted)]">Sem aprovacoes pendentes no momento.</p>
      ) : (
        <div className="space-y-3">
          {grouped.map((item) => (
            <div key={item.key} className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3">
              <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-[var(--muted)]">
                <span>{item.requestedAt}</span>
                <span className="rounded-full border border-white/10 px-2 py-1">{item.source}</span>
              </div>
              <div className="mt-2 text-sm text-white">{item.issueId}</div>
              <div className="mt-2 text-xs text-[var(--muted)] whitespace-pre-wrap">{item.directive}</div>
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  type="button"
                  disabled={isBusy}
                  onClick={() => runAction("approve", item.key)}
                  className="rounded-full bg-cyan-300 px-4 py-1 text-xs font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Aprovar
                </button>
                <button
                  type="button"
                  disabled={isBusy}
                  onClick={() => runAction("deny", item.key)}
                  className="rounded-full border border-white/20 px-4 py-1 text-xs font-semibold text-white transition hover:border-white/40 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Recusar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="mt-4 text-xs text-[var(--muted)]">
        {isBusy ? "Processando..." : actionState.message ?? "Aprovacoes disparam cmd:strategy."}
      </div>
    </div>
  );
}
