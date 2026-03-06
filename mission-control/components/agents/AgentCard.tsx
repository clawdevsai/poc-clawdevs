"use client";
import React from "react";
import { Cpu } from "lucide-react";
import type { Agent } from "../../lib/api";
import { AGENT_META } from "../../lib/constants";
import StatusDot from "../shared/StatusDot";

interface Props {
  agent: Agent;
  tokenCost?: number;
}

function formatTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

function formatTime(ts: number | null): string {
  if (!ts) return "—";
  const diff = Math.floor(Date.now() / 1000 - ts);
  if (diff < 60) return `${diff}s atrás`;
  if (diff < 3600) return `${Math.floor(diff / 60)}min atrás`;
  return `${Math.floor(diff / 3600)}h atrás`;
}

export default function AgentCard({ agent, tokenCost = 0 }: Props) {
  const meta = AGENT_META[agent.id] ?? {
    label: agent.id,
    emoji: "🤖",
    color: "#64748b",
    description: "",
  };

  return (
    <div
      className="relative bg-[#161a22] border border-[#232838] rounded-2xl p-4 hover:border-[#344055] transition-all group overflow-hidden"
      style={{ "--agent-color": meta.color } as React.CSSProperties}
    >
      {/* Color accent bar */}
      <div
        className="absolute top-0 left-0 right-0 h-[2px] rounded-t-2xl opacity-80"
        style={{ background: meta.color }}
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
            style={{ background: `${meta.color}18` }}
          >
            {meta.emoji}
          </div>
          <div>
            <p className="text-sm font-bold text-slate-100 leading-none">
              {meta.label}
            </p>
            <p className="text-[10px] text-slate-500 mt-0.5 leading-none">
              {agent.id}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <StatusDot status={agent.status} size="sm" />
          <span
            className={`text-[10px] font-semibold uppercase tracking-wider ${
              agent.status === "active"
                ? "text-green-400"
                : agent.status === "idle"
                ? "text-amber-400"
                : "text-slate-500"
            }`}
          >
            {agent.status === "active"
              ? "Ativo"
              : agent.status === "idle"
              ? "Inativo"
              : "Offline"}
          </span>
        </div>
      </div>

      {/* Current task */}
      <div className="bg-[#0d1117] rounded-lg px-3 py-2 mb-3 min-h-[40px]">
        {agent.current_task ? (
          <p className="text-[11px] text-slate-300 leading-relaxed truncate">
            {agent.current_task}
          </p>
        ) : (
          <p className="text-[11px] text-slate-600 italic">Sem tarefa ativa</p>
        )}
      </div>

      {/* Metrics footer */}
      <div className="flex items-center justify-between text-[10px] text-slate-500">
        <div className="flex items-center gap-1">
          <Cpu className="w-3 h-3" />
          <span>{formatTokens(agent.tokens_total)} tokens</span>
        </div>
        <span>
          {agent.last_heartbeat
            ? formatTime(agent.last_heartbeat)
            : "Nunca visto"}
        </span>
      </div>

      {tokenCost > 0 && (
        <div className="mt-2 pt-2 border-t border-[#232838] flex items-center justify-between text-[10px]">
          <span className="text-slate-500">Custo estimado</span>
          <span className="font-mono text-slate-400">
            ${tokenCost.toFixed(4)}
          </span>
        </div>
      )}
    </div>
  );
}
