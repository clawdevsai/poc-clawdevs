"use client";
import React, { useCallback, useEffect, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import TaskCard from "./TaskCard";
import InterventionModal from "./InterventionModal";
import { fetchBoard, createTask, moveTask, type Task, type BoardData } from "../../lib/api";
import { TASK_STATES, STATE_COLORS } from "../../lib/constants";
import { useSSE } from "../../lib/useSSE";

export default function MissionBoard() {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newSummary, setNewSummary] = useState("");
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await fetchBoard();
      // Remap old hiring states to dev workflow if needed
      const remapped: BoardData = {
        ...data,
        columns: TASK_STATES as unknown as string[],
        board: TASK_STATES.reduce((acc, state) => {
          const legacyIssues = data.board[state] || [];
          acc[state] = legacyIssues;
          return acc;
        }, {} as Record<string, Task[]>),
      };
      // Merge any issues with unknown states into Backlog
      const allKnown = new Set(TASK_STATES as readonly string[]);
      Object.entries(data.board).forEach(([state, issues]) => {
        if (!allKnown.has(state)) {
          remapped.board["Backlog"] = [
            ...(remapped.board["Backlog"] || []),
            ...issues,
          ];
        }
      });
      setBoard(remapped);
    } catch {
      // keep stale
    } finally {
      setLoading(false);
    }
  }, []);

  const { connected } = useSSE(load);

  useEffect(() => {
    load();
  }, [load]);

  async function handleMove(id: string, newState: string) {
    await moveTask(id, newState, "director");
    await load();
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      await createTask({
        title: newTitle.trim(),
        summary: newSummary.trim(),
        state: "Backlog",
        agent: "director",
        type: "task",
      });
      setNewTitle("");
      setNewSummary("");
      setShowCreate(false);
      await load();
    } finally {
      setCreating(false);
    }
  }

  return (
    <section className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div className="flex items-center gap-3">
          <h2 className="text-base font-bold text-slate-100">
            Central de Missões
          </h2>
          <div
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border ${
              connected
                ? "border-green-500/30 bg-green-500/5"
                : "border-amber-500/30 bg-amber-500/5"
            }`}
          >
            <div
              className={`w-1.5 h-1.5 rounded-full ${
                connected ? "bg-green-400 animate-pulse" : "bg-amber-400"
              }`}
            />
            <span
              className={`text-[9px] font-black uppercase tracking-widest ${
                connected ? "text-green-400" : "text-amber-400"
              }`}
            >
              {connected ? "Ao vivo" : "Reconectando"}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-brand hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            Nova tarefa
          </button>
        </div>
      </div>

      {/* Create task form */}
      {showCreate && (
        <form
          onSubmit={handleCreate}
          className="mb-4 bg-[#161a22] border border-brand/30 rounded-xl p-4 space-y-3 flex-shrink-0"
        >
          <p className="text-xs font-bold text-brand uppercase tracking-widest">
            Nova tarefa para o time
          </p>
          <input
            autoFocus
            required
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Título da tarefa..."
            className="w-full bg-[#0d1117] border border-[#232838] rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-brand"
          />
          <textarea
            rows={2}
            value={newSummary}
            onChange={(e) => setNewSummary(e.target.value)}
            placeholder="Contexto / descrição (opcional)..."
            className="w-full bg-[#0d1117] border border-[#232838] rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-brand resize-none"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="flex-1 px-3 py-1.5 text-xs text-slate-400 border border-[#232838] rounded-lg hover:text-slate-300 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={creating}
              className="flex-1 px-3 py-1.5 text-xs font-bold bg-brand text-white rounded-lg hover:bg-blue-500 transition-colors disabled:opacity-50"
            >
              {creating ? "Criando..." : "Criar"}
            </button>
          </div>
        </form>
      )}

      {/* Board columns */}
      <div className="flex-1 overflow-x-auto min-h-0">
        <div className="flex gap-4 h-full min-w-max pb-2">
          {TASK_STATES.map((state) => {
            const color = STATE_COLORS[state];
            const items = board?.board[state] ?? [];
            return (
              <div
                key={state}
                className="flex flex-col w-56 bg-[#0d1117] rounded-xl border border-[#1c2030] overflow-hidden"
              >
                {/* Column header */}
                <div
                  className="flex items-center justify-between px-3 py-2.5 border-b border-[#1c2030]"
                  style={{ borderTopColor: color, borderTopWidth: 2 }}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className="w-1.5 h-1.5 rounded-full"
                      style={{ background: color }}
                    />
                    <span className="text-xs font-bold text-slate-300">
                      {state}
                    </span>
                  </div>
                  <span
                    className="text-[10px] font-black px-1.5 py-0.5 rounded-full"
                    style={{ background: `${color}20`, color }}
                  >
                    {items.length}
                  </span>
                </div>

                {/* Cards */}
                <div className="flex-1 overflow-y-auto p-2 space-y-2">
                  {items.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onMove={handleMove}
                      onIntervene={setSelectedTask}
                    />
                  ))}
                  {items.length === 0 && (
                    <p className="text-[10px] text-slate-700 text-center py-4 italic">
                      Vazio
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Intervention Modal */}
      {selectedTask && (
        <InterventionModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onRefresh={load}
        />
      )}
    </section>
  );
}
