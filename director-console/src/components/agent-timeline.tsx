"use client";

import type { TimelineBucket } from "@/lib/server/types";

type AgentTimelineProps = {
  buckets: TimelineBucket[];
};

export function AgentTimeline({ buckets }: AgentTimelineProps) {
  return (
    <div className="panel panel-strong rounded-3xl p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-white">Timeline por agente</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">Ultimos eventos destacados por origem do stream.</p>
      </div>
      {buckets.length === 0 ? (
        <p className="text-sm text-[var(--muted)]">Nenhuma timeline disponivel.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {buckets.map((bucket) => (
            <div key={bucket.agent} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <div className="text-sm font-semibold text-white">{bucket.agent}</div>
              <div className="mt-3 space-y-2 text-xs text-[var(--muted)]">
                {bucket.items.length === 0 ? (
                  <div>Nenhum evento recente.</div>
                ) : (
                  bucket.items.map((item) => (
                    <div key={`${bucket.agent}-${item.stream}-${item.id}`} className="border-b border-white/5 pb-2">
                      <div className="text-[var(--muted)]">{item.timestamp}</div>
                      <div className="text-white">{item.eventName}</div>
                      {item.issueId ? <div>Issue: {item.issueId}</div> : null}
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
