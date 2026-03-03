"use client";

import React from "react";
import { Star, CheckSquare, Users } from "lucide-react";
import TaskCard from "./TaskCard";

interface ColumnProps {
    title: string;
    count: string;
    color: string;
    icon: any;
    items: any[];
}

export default function Column({ title, count, color, icon: Icon, items }: ColumnProps) {
    const getHeaderColor = () => {
        switch (color) {
            case "blue": return "bg-status-new shadow-status-new/20";
            case "orange": return "bg-status-shortlisted shadow-status-shortlisted/20";
            case "teal": return "bg-status-interviewed shadow-status-interviewed/20";
            default: return "bg-white/10";
        }
    };

    return (
        <div className="flex flex-col w-80 shrink-0 h-full">
            <div className={`status-header ${getHeaderColor()} text-white mb-4 shadow-lg`}>
                <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4" />
                    <span>{title}</span>
                </div>
                <span className="bg-white/20 px-2 py-0.5 rounded text-[10px] font-black">
                    {count}
                </span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin">
                {items.length > 0 ? (
                    items.map((item) => (
                        <TaskCard key={item.id} {...item} />
                    ))
                ) : (
                    <div className="h-24 border-2 border-dashed border-white/5 rounded-xl flex items-center justify-center">
                        <span className="text-xs text-foreground-muted font-medium italic">Vazio</span>
                    </div>
                )}
            </div>
        </div>
    );
}
