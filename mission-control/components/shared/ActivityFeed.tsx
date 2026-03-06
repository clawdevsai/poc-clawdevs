"use client";
import React, { useCallback, useEffect, useState } from "react";
import { Activity } from "lucide-react";
import { fetchActivities, type Activity as ActivityItem } from "../../lib/api";
import { AGENT_META } from "../../lib/constants";

function formatTs(ts: number): string {
  const d = new Date(ts);
  return d.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ActivityFeed() {
  const [items, setItems] = useState<ActivityItem[]>([]);

  const load = useCallback(async () => {
    try {
      const data = await fetchActivities(40);
      setItems(data);
    } catch {
      // silent
    }
  }, []);

  useEffect(() => {
    load();
    const iv = setInterval(load, 10_000);
    return () => clearInterval(iv);
  }, [load]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-5 pt-1 pb-4 border-b border-[#232838]">
        <Activity className="w-4 h-4 text-slate-500" />
        <h3 className="text-sm font-bold text-slate-200">Feed de Atividades</h3>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
        {items.length === 0 && (
          <p className="text-[11px] text-slate-600 text-center py-6 italic">
            Nenhuma atividade registrada
          </p>
        )}
        {items.map((item) => {
          const meta = AGENT_META[item.agent];
          return (
            <div
              key={item.id}
              className="flex gap-2.5 py-2 border-b border-[#1c2030] last:border-0"
            >
              <div className="flex-shrink-0 mt-0.5">
                <div className="w-6 h-6 rounded-lg flex items-center justify-center text-sm"
                  style={{ background: meta ? `${meta.color}18` : "#232838" }}>
                  {meta?.emoji ?? "🤖"}
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 mb-0.5">
                  <span className="text-[11px] font-bold text-slate-300">
                    {meta?.label ?? item.agent}
                  </span>
                  {item.agent === "director" && (
                    <span className="text-[9px] font-black bg-brand/20 text-brand px-1.5 py-0.5 rounded-full uppercase tracking-wider">
                      Diretor
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  {item.message}
                </p>
              </div>
              <span className="text-[10px] text-slate-700 flex-shrink-0 mt-0.5">
                {formatTs(item.timestamp)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
