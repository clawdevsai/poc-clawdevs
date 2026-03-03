"use client";

import React, { useEffect, useState, useCallback } from "react";
import KanbanColumn from "./KanbanColumn";
import { fetchBoard, BoardData, KanbanEvent } from "../lib/api";
import { useSSE } from "../lib/useSSE";

export default function KanbanBoard() {
    const [data, setData] = useState<BoardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [recentIds, setRecentIds] = useState<Set<string>>(new Set());

    const loadBoard = useCallback(async () => {
        try {
            setLoading(true);
            const boardData = await fetchBoard();
            setData(boardData);
            setError(null);
        } catch (err) {
            setError("Erro ao carregar o quadro. Verifique a conexão com a API.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Use SSE for real-time updates
    const { connected, lastEvent } = useSSE((event: KanbanEvent) => {
        // Optimistic or reactive update: refresh the whole board for simplicity
        // and to ensure consistency with Redis state.
        loadBoard();

        // Highlight the changed issue
        if (event.issue_id) {
            setRecentIds((prev) => {
                const next = new Set(prev);
                next.add(event.issue_id);
                return next;
            });

            // Remove highlight after 5 seconds
            setTimeout(() => {
                setRecentIds((prev) => {
                    const next = new Set(prev);
                    next.delete(event.issue_id);
                    return next;
                });
            }, 5000);
        }
    });

    useEffect(() => {
        loadBoard();
    }, [loadBoard]);

    if (loading && !data) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh]">
                <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mb-4" />
                <p className="text-gray-400 font-medium">Sincronizando com os agentes...</p>
            </div>
        );
    }

    if (error && !data) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4">
                <div className="w-16 h-16 bg-rose-500/10 rounded-full flex items-center justify-center mb-4">
                    <svg className="w-8 h-8 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Ops! Algo deu errado</h3>
                <p className="text-gray-400 mb-6 max-w-md">{error}</p>
                <button
                    onClick={loadBoard}
                    className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-semibold transition-colors"
                >
                    Tentar Novamente
                </button>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="flex flex-col h-full">
            {/* Connection indicator */}
            <div className="flex items-center gap-2 mb-6 ml-1">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-500 pulse-dot' : 'bg-rose-500'} shadow-sm`} />
                <span className="text-[11px] font-bold uppercase tracking-widest text-gray-500">
                    {connected ? 'LIVE FEED ACTIVE' : 'RECONNECTING TO AGENTS...'}
                </span>
            </div>

            {/* Columns container */}
            <div className="flex-1 overflow-x-auto pb-6 -mx-1 px-1 custom-scrollbar">
                <div className="flex flex-nowrap gap-4 h-full min-h-[500px]">
                    {data.columns.map((state) => (
                        <KanbanColumn
                            key={state}
                            state={state}
                            issues={data.board[state] || []}
                            recentIds={recentIds}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}
