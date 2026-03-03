"use client";

import React from "react";
import { MoreHorizontal, FileText, Bookmark, Layout as LayoutIcon } from "lucide-react";

interface TaskCardProps {
    id: string;
    type: "task" | "story" | "epic";
    title: string;
    summary: string;
    created_by: string;
    state: string;
    tags?: string[];
    priority?: string;
}

export default function TaskCard({
    type = "task",
    title,
    summary,
    created_by = "AI",
    tags = [],
    priority = "medium"
}: TaskCardProps) {
    const agentName = created_by || "AI";
    const initials = agentName.substring(0, 2).toUpperCase();

    const getPriorityColor = () => {
        switch (priority) {
            case "high": return "bg-status-new";
            case "medium": return "bg-status-shortlisted";
            default: return "bg-status-interviewed";
        }
    };

    const getTypeStyle = () => {
        switch (type) {
            case "epic": return { icon: LayoutIcon, color: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/20", label: "Epic" };
            case "story": return { icon: Bookmark, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", label: "Story" };
            default: return { icon: FileText, color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20", label: "Task" };
        }
    };

    const typeConfig = getTypeStyle();
    const TypeIcon = typeConfig.icon;

    return (
        <div className="group bg-card border border-white/5 rounded-xl p-4 transition-all duration-300 hover:border-white/20 hover:bg-card-hover hover:-translate-y-1 cursor-grab active:cursor-grabbing shadow-sm hover:shadow-xl">
            <div className="flex items-center gap-2 mb-3">
                <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md border ${typeConfig.bg} ${typeConfig.border}`}>
                    <TypeIcon className={`w-3 h-3 ${typeConfig.color}`} />
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${typeConfig.color}`}>{typeConfig.label}</span>
                </div>
            </div>

            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-white/10 to-white/5 border border-white/10 flex items-center justify-center text-[10px] font-bold ring-2 ring-transparent group-hover:ring-status-new transition-all">
                        {initials}
                    </div>
                    <div className="overflow-hidden">
                        <h4 className="text-sm font-bold text-white truncate leading-tight">{title}</h4>
                        <p className="text-[11px] text-foreground-muted truncate mt-0.5">{summary}</p>
                    </div>
                </div>
                <button className="text-foreground-muted hover:text-white transition-colors p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreHorizontal className="w-4 h-4" />
                </button>
            </div>

            <div className="flex items-center justify-between mt-4">
                <div className="flex flex-wrap gap-1.5">
                    {tags && tags.length > 0 ? tags.map((tag, i) => (
                        <span
                            key={i}
                            className="px-2 py-0.5 bg-white/5 border border-white/5 rounded text-[9px] font-bold text-foreground-muted uppercase tracking-wider"
                        >
                            {tag}
                        </span>
                    )) : (
                        <span className="text-[9px] font-medium text-foreground-muted/40 italic">No tags</span>
                    )}
                </div>
                <div className={`w-2 h-2 rounded-full ${getPriorityColor()} shadow-[0_0_8px_rgba(255,255,255,0.2)]`} title={`Priority: ${priority}`} />
            </div>
        </div>
    );
}
