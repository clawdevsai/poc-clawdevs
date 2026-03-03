"use client";

import React from "react";
import TaskCard from "./TaskCard";

// Column accent colors by state
const COLUMN_ACCENTS: Record<string, string> = {
    Backlog: "border-t-slate-500",
    Refinamento: "border-t-blue-500",
    Ready: "border-t-cyan-500",
    InProgress: "border-t-indigo-500",
    InReview: "border-t-violet-500",
    Approved: "border-t-emerald-500",
    Merged: "border-t-green-500",
    Deployed: "border-t-teal-500",
    Monitoring: "border-t-amber-500",
    Done: "border-t-gray-500",
};

const COLUMN_DOT_COLORS: Record<string, string> = {
    Backlog: "bg-slate-400",
    Refinamento: "bg-blue-400",
    Ready: "bg-cyan-400",
    InProgress: "bg-indigo-400",
    InReview: "bg-violet-400",
    Approved: "bg-emerald-400",
    Merged: "bg-green-400",
    Deployed: "bg-teal-400",
    Monitoring: "bg-amber-400",
    Done: "bg-gray-400",
};

const COLUMN_LABELS: Record<string, string> = {
    Backlog: "Backlog",
    Refinamento: "Refinamento",
    Ready: "Ready",
    InProgress: "In Progress",
    InReview: "In Review",
    Approved: "Approved",
    Merged: "Merged",
    Deployed: "Deployed",
    Monitoring: "Monitoring",
    Done: "Done",
};

interface Issue {
    id: string;
    title: string;
    summary: string;
    state: string;
    priority: string;
    created_by: string;
    created_at: string;
}

interface KanbanColumnProps {
    state: string;
    issues: Issue[];
    recentIds?: Set<string>;
}

export default function KanbanColumn({
    state,
    issues,
    recentIds = new Set(),
}: KanbanColumnProps) {
    const accent = COLUMN_ACCENTS[state] || "border-t-gray-500";
    const dotColor = COLUMN_DOT_COLORS[state] || "bg-gray-400";
    const label = COLUMN_LABELS[state] || state;

    return (
        <div
            className={`glass-column border-t-2 ${accent} flex flex-col min-w-[260px] max-w-[300px] h-full`}
        >
            {/* Column header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
                <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${dotColor}`} />
                    <h2 className="text-sm font-semibold text-gray-200 tracking-tight">
                        {label}
                    </h2>
                </div>
                <span className="text-xs font-medium text-gray-500 bg-white/5 px-2 py-0.5 rounded-full">
                    {issues.length}
                </span>
            </div>

            {/* Cards */}
            <div className="flex-1 overflow-y-auto px-3 py-3 space-y-0">
                {issues.length === 0 ? (
                    <div className="flex items-center justify-center h-20">
                        <p className="text-xs text-gray-600 italic">Sem tarefas</p>
                    </div>
                ) : (
                    issues.map((issue) => (
                        <TaskCard
                            key={issue.id}
                            issue={issue}
                            isNew={recentIds.has(issue.id)}
                        />
                    ))
                )}
            </div>
        </div>
    );
}
