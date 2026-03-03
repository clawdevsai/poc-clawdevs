"use client";

import React from "react";
import { MoreHorizontal } from "lucide-react";

interface TaskCardProps {
    id: string;
    title: string;
    summary: string;
    agent: string;
    state: string;
    tags?: string[];
    avatarColor?: string;
}

export default function TaskCard({ title, summary, agent, tags = ["Java", "Developer", ".NET"] }: TaskCardProps) {
    return (
        <div className="group bg-card border border-white/5 rounded-xl p-4 transition-all duration-300 hover:border-white/20 hover:bg-card-hover hover:-translate-y-1 cursor-grab active:cursor-grabbing">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-white/10 to-white/5 border border-white/10 flex items-center justify-center text-xs font-bold ring-2 ring-transparent group-hover:ring-status-new transition-all">
                        {agent.substring(0, 2).toUpperCase()}
                    </div>
                    <div className="overflow-hidden">
                        <h4 className="text-sm font-bold text-white truncate leading-tight">{agent}</h4>
                        <p className="text-[11px] text-foreground-muted truncate mt-0.5">{title}</p>
                    </div>
                </div>
                <button className="text-foreground-muted hover:text-white transition-colors p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreHorizontal className="w-4 h-4" />
                </button>
            </div>

            <div className="flex flex-wrap gap-1.5 mt-4">
                {tags.map((tag, i) => (
                    <span
                        key={i}
                        className="px-2 py-0.5 bg-white/5 border border-white/5 rounded text-[9px] font-bold text-foreground-muted uppercase tracking-wider"
                    >
                        {tag}
                    </span>
                ))}
            </div>
        </div>
    );
}
