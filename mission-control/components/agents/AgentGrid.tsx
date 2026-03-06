"use client";
import React, { useCallback, useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import AgentCard from "./AgentCard";
import { fetchAgents, fetchTokens, type Agent, type TokenData } from "../../lib/api";

export default function AgentGrid() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tokens, setTokens] = useState<TokenData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const load = useCallback(async () => {
    try {
      const [ag, tk] = await Promise.all([fetchAgents(), fetchTokens()]);
      setAgents(ag);
      setTokens(tk);
      setLastUpdated(new Date());
    } catch {
      // silently keep stale data
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const iv = setInterval(load, 15_000); // refresh every 15s
    return () => clearInterval(iv);
  }, [load]);

  const activeCount = agents.filter((a) => a.status === "active").length;
  const idleCount = agents.filter((a) => a.status === "idle").length;

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-100">
            Time de Agentes
          </h2>
          {!loading && (
            <p className="text-[11px] text-slate-500 mt-0.5">
              {activeCount} ativos · {idleCount} inativos ·{" "}
              {agents.length - activeCount - idleCount} offline
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          {lastUpdated && (
            <span className="text-[10px] text-slate-600">
              {lastUpdated.toLocaleTimeString("pt-BR", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              })}
            </span>
          )}
          <button
            onClick={load}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
            title="Atualizar"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {loading && agents.length === 0 ? (
        <div className="grid grid-cols-3 gap-3">
          {Array.from({ length: 9 }).map((_, i) => (
            <div
              key={i}
              className="bg-[#161a22] border border-[#232838] rounded-2xl h-32 animate-pulse"
            />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-3">
          {agents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              tokenCost={tokens?.by_agent?.[agent.id]?.cost_usd ?? 0}
            />
          ))}
          {agents.length === 0 && (
            <div className="col-span-3 text-center py-8 text-slate-500 text-sm">
              Nenhum agente registrado. Aguardando heartbeat...
            </div>
          )}
        </div>
      )}
    </section>
  );
}
