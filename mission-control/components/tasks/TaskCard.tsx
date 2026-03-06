"use client";
import React, { useState } from "react";
import { MoreHorizontal, Zap } from "lucide-react";
import type { Task } from "../../lib/api";
import { PRIORITY_COLORS, PRIORITY_LABELS, AGENT_META } from "../../lib/constants";

interface Props {
  task: Task;
  onMove: (id: string, newState: string) => void;
  onIntervene: (task: Task) => void;
}

export default function TaskCard({ task, onIntervene }: Props) {
  const [menuOpen, setMenuOpen] = useState(false);
  const pColor = PRIORITY_COLORS[task.priority] ?? "#64748b";
  const pLabel = PRIORITY_LABELS[task.priority] ?? task.priority;
  const agentMeta = AGENT_META[task.created_by];

  return (
    <div className="bg-[#0d1117] border border-[#232838] rounded-xl p-3 hover:border-[#344055] transition-all group">
      {/* Priority badge */}
      <div className="flex items-center justify-between mb-2">
        <span
          className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full"
          style={{ background: `${pColor}20`, color: pColor }}
        >
          {pLabel}
        </span>
        <div className="flex items-center gap-1">
          {agentMeta && (
            <span title={agentMeta.label} className="text-xs">
              {agentMeta.emoji}
            </span>
          )}
          <button
            onClick={() => {
              setMenuOpen(!menuOpen);
              onIntervene(task);
            }}
            className="p-0.5 rounded text-slate-600 hover:text-slate-300 opacity-0 group-hover:opacity-100 transition-all"
          >
            <MoreHorizontal className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Title */}
      <p className="text-sm font-semibold text-slate-200 leading-snug mb-1.5 line-clamp-2">
        {task.title}
      </p>

      {/* Summary */}
      {task.summary && (
        <p className="text-[11px] text-slate-500 leading-relaxed line-clamp-2 mb-2">
          {task.summary}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between mt-2 pt-2 border-t border-[#1c2030]">
        <span className="text-[10px] font-mono text-slate-600">#{task.id}</span>
        <span
          className={`text-[10px] font-medium capitalize px-1.5 py-0.5 rounded ${
            task.type === "epic"
              ? "bg-purple-500/10 text-purple-400"
              : task.type === "story"
              ? "bg-blue-500/10 text-blue-400"
              : "bg-slate-500/10 text-slate-400"
          }`}
        >
          {task.type}
        </span>
      </div>
    </div>
  );
}
