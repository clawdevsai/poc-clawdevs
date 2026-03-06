"use client";
import React from "react";
import { Terminal } from "lucide-react";

interface Props {
  view: "dashboard" | "board" | "tokens";
  setView: (v: "dashboard" | "board" | "tokens") => void;
  connected: boolean;
}

const TABS = [
  { id: "dashboard" as const, label: "Dashboard" },
  { id: "board" as const, label: "Central de Missões" },
  { id: "tokens" as const, label: "FinOps / Tokens" },
];

export default function TopBar({ view, setView, connected }: Props) {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-[#232838] bg-[#0a0c10] flex-shrink-0">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-brand/10 border border-brand/20 flex items-center justify-center">
          <Terminal className="w-4 h-4 text-brand" />
        </div>
        <div>
          <p className="text-sm font-black text-slate-100 leading-none tracking-tight">
            Mission Control
          </p>
          <p className="text-[10px] text-slate-600 leading-none mt-0.5">
            ClawDevs AI
          </p>
        </div>
      </div>

      {/* Tabs */}
      <nav className="flex items-center gap-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setView(tab.id)}
            className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
              view === tab.id
                ? "bg-brand/10 text-brand border border-brand/20"
                : "text-slate-500 hover:text-slate-300 hover:bg-white/5"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Status */}
      <div className="flex items-center gap-2">
        <div
          className={`flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest ${
            connected ? "text-green-400" : "text-amber-400"
          }`}
        >
          <div
            className={`w-1.5 h-1.5 rounded-full ${
              connected ? "bg-green-400 animate-pulse" : "bg-amber-400"
            }`}
          />
          {connected ? "Pipeline ao vivo" : "Reconectando..."}
        </div>
        <div className="w-px h-4 bg-[#232838] mx-1" />
        <div className="w-7 h-7 rounded-full bg-brand/20 border border-brand/30 flex items-center justify-center">
          <span className="text-xs font-black text-brand">D</span>
        </div>
        <div>
          <p className="text-xs font-bold text-slate-200 leading-none">
            Diretor
          </p>
          <p className="text-[9px] text-slate-600 leading-none mt-0.5">
            Admin
          </p>
        </div>
      </div>
    </header>
  );
}
