"use client";
import React, { useState } from "react";
import { X, Send } from "lucide-react";
import type { Task, InterventionAction } from "../../lib/api";
import { postIntervention, moveTask } from "../../lib/api";
import { INTERVENTION_ACTIONS, TASK_STATES, AGENT_META } from "../../lib/constants";

interface Props {
  task: Task;
  onClose: () => void;
  onRefresh: () => void;
}

export default function InterventionModal({ task, onClose, onRefresh }: Props) {
  const [action, setAction] = useState<InterventionAction>("reassign");
  const [targetAgent, setTargetAgent] = useState("");
  const [note, setNote] = useState("");
  const [newState, setNewState] = useState(task.state);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      // Move task state if changed
      if (newState !== task.state) {
        await moveTask(task.id, newState, "director");
      }
      // Record intervention
      await postIntervention({
        issue_id: task.id,
        action,
        target_agent: targetAgent || undefined,
        note: note || undefined,
      });
      setDone(true);
      setTimeout(() => {
        onRefresh();
        onClose();
      }, 800);
    } catch (err) {
      console.error("Intervention failed:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#161a22] border border-[#344055] rounded-2xl w-[480px] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#232838]">
          <div>
            <p className="text-xs font-bold text-brand uppercase tracking-widest">
              Intervenção do Diretor
            </p>
            <p className="text-sm font-semibold text-slate-100 mt-0.5 truncate">
              #{task.id} — {task.title}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {done ? (
          <div className="p-6 text-center">
            <div className="text-3xl mb-2">✅</div>
            <p className="text-sm text-slate-300 font-medium">
              Intervenção registrada com sucesso
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-5 space-y-4">
            {/* Move state */}
            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                Mover para estado
              </label>
              <select
                value={newState}
                onChange={(e) => setNewState(e.target.value)}
                className="w-full bg-[#0d1117] border border-[#232838] rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand"
              >
                {TASK_STATES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            {/* Action */}
            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                Ação
              </label>
              <div className="grid grid-cols-2 gap-2">
                {INTERVENTION_ACTIONS.map((a) => (
                  <button
                    key={a.value}
                    type="button"
                    onClick={() => setAction(a.value as InterventionAction)}
                    className={`text-xs px-3 py-2 rounded-lg border transition-all text-left ${
                      action === a.value
                        ? "border-brand bg-brand/10 text-slate-100"
                        : "border-[#232838] text-slate-500 hover:border-[#344055] hover:text-slate-300"
                    }`}
                  >
                    {a.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Target agent (for reassign) */}
            {action === "reassign" && (
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                  Reatribuir para
                </label>
                <select
                  value={targetAgent}
                  onChange={(e) => setTargetAgent(e.target.value)}
                  className="w-full bg-[#0d1117] border border-[#232838] rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand"
                >
                  <option value="">Selecionar agente...</option>
                  {Object.entries(AGENT_META).map(([id, meta]) => (
                    <option key={id} value={id}>
                      {meta.emoji} {meta.label}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Note */}
            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                Observação (opcional)
              </label>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                rows={2}
                placeholder="Contexto da intervenção..."
                className="w-full bg-[#0d1117] border border-[#232838] rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-brand resize-none"
              />
            </div>

            {/* Submit */}
            <div className="flex gap-2 pt-1">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 text-sm text-slate-400 border border-[#232838] rounded-lg hover:border-[#344055] hover:text-slate-300 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-brand hover:bg-blue-500 text-white text-sm font-bold rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Send className="w-3.5 h-3.5" />
                )}
                Confirmar
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
