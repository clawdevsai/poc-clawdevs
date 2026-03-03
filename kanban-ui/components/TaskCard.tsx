"use client";

import React from "react";

// Agent color mapping for visual distinction
const AGENT_COLORS: Record<string, string> = {
    director: "from-indigo-500 to-purple-600",
    ceo: "from-amber-500 to-orange-600",
    po: "from-blue-500 to-cyan-600",
    architect: "from-emerald-500 to-teal-600",
    developer: "from-violet-500 to-indigo-600",
    qa: "from-rose-500 to-pink-600",
    cybersec: "from-red-500 to-orange-600",
    dba: "from-slate-500 to-zinc-600",
    devops: "from-green-500 to-emerald-600",
    ux: "from-pink-500 to-rose-600",
    api: "from-gray-500 to-slate-600",
    unknown: "from-gray-500 to-slate-600",
};

const AGENT_INITIALS: Record<string, string> = {
    director: "DR",
    ceo: "CE",
    po: "PO",
    architect: "AR",
    developer: "DV",
    qa: "QA",
    cybersec: "CS",
    dba: "DB",
    devops: "DO",
    ux: "UX",
    api: "AP",
    unknown: "??",
};

const PRIORITY_COLORS: Record<string, string> = {
    high: "bg-rose-500/20 text-rose-400 border-rose-500/30",
    medium: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    low: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
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

interface TaskCardProps {
    issue: Issue;
    isNew?: boolean;
}

export default function TaskCard({ issue, isNew = false }: TaskCardProps) {
    const agent = (issue.created_by || "unknown").toLowerCase();
    const agentGradient = AGENT_COLORS[agent] || AGENT_COLORS.unknown;
    const agentInitials = AGENT_INITIALS[agent] || "??";
    const priority = (issue.priority || "medium").toLowerCase();
    const priorityClass = PRIORITY_COLORS[priority] || PRIORITY_COLORS.medium;

    const timeAgo = issue.created_at
        ? formatTimeAgo(parseInt(issue.created_at))
        : "";

    return (
        <div
            className={`glass-card p-4 mb-3 cursor-pointer group ${isNew ? "animate-slide-in ring-1 ring-indigo-500/40" : ""
                }`}
        >
            {/* Header: priority + agent */}
            <div className="flex items-center justify-between mb-3">
                <span
                    className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full border ${priorityClass}`}
                >
                    {priority}
                </span>
                <div
                    className={`w-7 h-7 rounded-full bg-gradient-to-br ${agentGradient} flex items-center justify-center shadow-lg`}
                    title={issue.created_by}
                >
                    <span className="text-[9px] font-bold text-white">
                        {agentInitials}
                    </span>
                </div>
            </div>

            {/* Title */}
            <h3 className="text-sm font-semibold text-gray-100 mb-1 leading-snug group-hover:text-white transition-colors line-clamp-2">
                {issue.title || `Issue #${issue.id}`}
            </h3>

            {/* Summary */}
            {issue.summary && (
                <p className="text-xs text-gray-400 mb-3 line-clamp-2 leading-relaxed">
                    {issue.summary}
                </p>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between pt-2 border-t border-white/5">
                <span className="text-[10px] text-gray-500 font-mono">
                    #{issue.id}
                </span>
                {timeAgo && (
                    <span className="text-[10px] text-gray-500">{timeAgo}</span>
                )}
            </div>
        </div>
    );
}

function formatTimeAgo(timestamp: number): string {
    const now = Date.now();
    const diff = now - timestamp;
    if (diff < 0) return "agora";
    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}d`;
}
