"use client";

import type { ActivityItem } from "@/lib/server/types";

type ActivityFeedProps = {
  items: ActivityItem[];
};

export function ActivityFeed({ items }: ActivityFeedProps) {
  return (
    <div className="panel panel-strong rounded-3xl p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-white">Feed de atividade</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">Eventos combinados dos streams principais e orquestracao.</p>
      </div>
      <div className="space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-[var(--muted)]">Nenhum evento recente encontrado.</p>
        ) : (
          items.map((item) => (
            <div key={`${item.stream}-${item.id}`} className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3">
              <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-[var(--muted)]">
                <span>{item.timestamp}</span>
                <span className="rounded-full border border-white/10 px-2 py-1">{item.agent}</span>
              </div>
              <div className="mt-2 text-sm text-white">{item.eventName}</div>
              <div className="mt-1 text-xs text-[var(--muted)]">
                Stream: {item.stream}
                {item.issueId ? ` · Issue: ${item.issueId}` : ""}
              </div>
              {item.summary ? <div className="mt-2 text-xs text-[var(--muted)]">{item.summary}</div> : null}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
