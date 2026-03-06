"use client";
import React, { useState } from "react";
import TopBar from "../components/shared/TopBar";
import AgentGrid from "../components/agents/AgentGrid";
import TokenPanel from "../components/tokens/TokenPanel";
import MissionBoard from "../components/tasks/MissionBoard";
import ActivityFeed from "../components/shared/ActivityFeed";
import { useSSE } from "../lib/useSSE";

type View = "dashboard" | "board" | "tokens";

export default function MissionControlPage() {
  const [view, setView] = useState<View>("dashboard");
  const { connected } = useSSE(() => {});

  return (
    <div className="flex flex-col h-screen bg-[#0a0c10] text-slate-100 overflow-hidden">
      <TopBar view={view} setView={setView} connected={connected} />

      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6 min-w-0">
          {view === "dashboard" && (
            <div className="space-y-8 max-w-6xl mx-auto">
              <AgentGrid />
              <div className="grid grid-cols-2 gap-6">
                <TokenPanel />
                <div>
                  <h2 className="text-base font-bold text-slate-100 mb-4">
                    Resumo de Tarefas
                  </h2>
                  <QuickStats />
                </div>
              </div>
            </div>
          )}

          {view === "board" && (
            <div className="h-full flex flex-col">
              <MissionBoard />
            </div>
          )}

          {view === "tokens" && (
            <div className="max-w-3xl mx-auto">
              <TokenPanel />
            </div>
          )}
        </main>

        {/* Activity feed sidebar */}
        <aside className="w-72 border-l border-[#232838] bg-[#0d1117] overflow-hidden flex flex-col">
          <ActivityFeed />
        </aside>
      </div>
    </div>
  );
}

// ── Quick Stats widget (inline, usado na Dashboard) ───────────────────────────
function QuickStats() {
  const [stats] = useState({
    backlog: 0,
    progress: 0,
    review: 0,
    done: 0,
  });

  const ITEMS = [
    { label: "Backlog", value: stats.backlog, color: "#6366f1" },
    { label: "Em Andamento", value: stats.progress, color: "#3b82f6" },
    { label: "Em Revisão", value: stats.review, color: "#f59e0b" },
    { label: "Concluído", value: stats.done, color: "#22c55e" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {ITEMS.map((item) => (
        <div
          key={item.label}
          className="bg-[#161a22] border border-[#232838] rounded-xl p-4 hover:border-[#344055] transition-all"
        >
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-xl font-black mb-2"
            style={{ background: `${item.color}18`, color: item.color }}
          >
            {item.value}
          </div>
          <p className="text-[11px] text-slate-500 font-medium">{item.label}</p>
        </div>
      ))}
    </div>
  );
}
