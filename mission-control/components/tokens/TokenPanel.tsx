"use client";
import React, { useCallback, useEffect, useState } from "react";
import { Zap, TrendingUp, AlertTriangle } from "lucide-react";
import { fetchTokens, type TokenData } from "../../lib/api";
import { AGENT_META } from "../../lib/constants";

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

export default function TokenPanel() {
  const [data, setData] = useState<TokenData | null>(null);

  const load = useCallback(async () => {
    try {
      const d = await fetchTokens();
      setData(d);
    } catch {
      // silent
    }
  }, []);

  useEffect(() => {
    load();
    const iv = setInterval(load, 30_000);
    return () => clearInterval(iv);
  }, [load]);

  if (!data) {
    return (
      <section>
        <h2 className="text-base font-bold text-slate-100 mb-4">
          Uso de Tokens
        </h2>
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-8 bg-[#161a22] rounded-lg animate-pulse" />
          ))}
        </div>
      </section>
    );
  }

  const totalCost = Object.values(data.by_agent).reduce(
    (acc, a) => acc + a.cost_usd,
    0
  );
  const capPercent = Math.min(
    100,
    Math.round((totalCost / data.daily_cap_usd) * 100)
  );
  const isNearCap = capPercent >= 80;

  const sorted = Object.entries(data.by_agent)
    .filter(([, v]) => v.tokens > 0)
    .sort(([, a], [, b]) => b.tokens - a.tokens);

  const maxTokens = sorted[0]?.[1]?.tokens ?? 1;

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-bold text-slate-100">Uso de Tokens</h2>
        <div className="flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-xs font-mono text-slate-300">
            {formatNum(data.total_tokens)}
          </span>
        </div>
      </div>

      {/* Daily cap bar */}
      <div className="bg-[#161a22] border border-[#232838] rounded-xl p-3 mb-4">
        <div className="flex items-center justify-between text-[11px] mb-2">
          <div className="flex items-center gap-1.5">
            {isNearCap ? (
              <AlertTriangle className="w-3 h-3 text-amber-400" />
            ) : (
              <TrendingUp className="w-3 h-3 text-slate-500" />
            )}
            <span className={isNearCap ? "text-amber-400" : "text-slate-400"}>
              Teto diário FinOps
            </span>
          </div>
          <span className="font-mono text-slate-300">
            ${totalCost.toFixed(3)} / ${data.daily_cap_usd.toFixed(2)}
          </span>
        </div>
        <div className="h-1.5 bg-[#0d1117] rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              isNearCap ? "bg-amber-400" : "bg-brand"
            }`}
            style={{ width: `${capPercent}%` }}
          />
        </div>
        <p className="text-[10px] text-slate-600 mt-1 text-right">
          {capPercent}% utilizado
        </p>
      </div>

      {/* Per-agent breakdown */}
      <div className="space-y-2">
        {sorted.length === 0 && (
          <p className="text-[11px] text-slate-600 text-center py-3">
            Nenhum token registrado ainda
          </p>
        )}
        {sorted.map(([agentId, usage]) => {
          const meta = AGENT_META[agentId];
          const pct = Math.round((usage.tokens / maxTokens) * 100);
          return (
            <div key={agentId} className="group">
              <div className="flex items-center justify-between text-[11px] mb-1">
                <div className="flex items-center gap-1.5">
                  <span>{meta?.emoji ?? "🤖"}</span>
                  <span className="text-slate-300 font-medium">
                    {meta?.label ?? agentId}
                  </span>
                </div>
                <div className="flex items-center gap-2 font-mono text-slate-500">
                  <span>{formatNum(usage.tokens)}</span>
                  <span className="text-slate-600">${usage.cost_usd.toFixed(4)}</span>
                </div>
              </div>
              <div className="h-1 bg-[#1c2030] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${pct}%`,
                    background: meta?.color ?? "#4f8ef7",
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
