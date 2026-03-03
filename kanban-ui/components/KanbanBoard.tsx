"use client";

import React, { useEffect, useState, useCallback } from "react";
import Column from "./Column";
import { fetchBoard, BoardData, KanbanEvent } from "../lib/api";
import { useSSE } from "../lib/useSSE";
import { Star, CheckSquare, Users, AlertCircle, RefreshCw } from "lucide-react";

const COLUMN_CONFIG: Record<string, { title: string; color: string; icon: any }> = {
    "New": { title: "New", color: "blue", icon: Star },
    "Shortlisted": { title: "Shortlisted", color: "orange", icon: CheckSquare },
    "Interviewed": { title: "Interviewed", color: "teal", icon: Users },
};

export default function KanbanBoard() {
    const [data, setData] = useState<BoardData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [mounted, setMounted] = useState(false);

    // Prevent hydration mismatch
    useEffect(() => {
        setMounted(true);
    }, []);

    const loadBoard = useCallback(async () => {
        try {
            setLoading(true);
            const boardData = await fetchBoard();
            setData(boardData);
            setError(null);
        } catch (err: any) {
            setError("Unable to connect to the agent pipeline. Please ensure the backend is running.");
            console.error("Board fetch error:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    const { connected } = useSSE(() => {
        loadBoard();
    });

    useEffect(() => {
        if (mounted) {
            loadBoard();
        }
    }, [mounted, loadBoard]);

    if (!mounted) return null;

    if (loading && !data) {
        return (
            <div className="flex flex-col items-center justify-center h-full">
                <div className="w-10 h-10 border-2 border-status-new/20 border-t-status-new rounded-full animate-spin mb-4" />
                <p className="text-foreground-muted text-sm font-medium animate-pulse">Syncing with agents...</p>
            </div>
        );
    }

    if (error && !data) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-center px-8">
                <div className="w-16 h-16 bg-status-shortlisted/10 rounded-2xl flex items-center justify-center mb-6">
                    <AlertCircle className="w-8 h-8 text-status-shortlisted" />
                </div>
                <h3 className="text-xl font-extrabold text-white mb-2 tracking-tight">Backend Connection Error</h3>
                <p className="text-foreground-muted text-sm mb-8 max-w-sm leading-relaxed">{error}</p>
                <button
                    onClick={loadBoard}
                    className="flex items-center gap-2 px-6 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-xl font-bold text-sm transition-all"
                >
                    <RefreshCw className="w-4 h-4" />
                    Try Again
                </button>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="flex flex-col h-full">
            <div className="flex items-center gap-3 mb-8">
                <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/5">
                    <div className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-500' : 'bg-status-shortlisted'}`} />
                    <span className="text-[10px] font-black text-foreground-muted uppercase tracking-widest leading-none">
                        {connected ? 'Pipeline Live' : 'Reconnecting'}
                    </span>
                </div>
            </div>

            <div className="flex-1 overflow-x-auto pb-8 -mx-8 px-8 flex gap-8">
                {data.columns.map((state) => {
                    const config = COLUMN_CONFIG[state] || { title: state, color: "gray", icon: Star };
                    const items = data.board[state] || [];
                    return (
                        <Column
                            key={state}
                            title={config.title}
                            color={config.color}
                            icon={config.icon}
                            count={`${items.length}/${items.length + 5}`}
                            items={items}
                        />
                    );
                })}
            </div>
        </div>
    );
}
