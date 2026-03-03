"use client";

import React from "react";
import { Search, Plus, Trash2, Edit2, UserPlus, Bell } from "lucide-react";

export default function Header() {
    return (
        <header className="flex items-center justify-between px-8 py-6 border-b border-white/5 bg-background sticky top-0 z-10">
            <div className="space-y-1">
                <div className="flex items-center gap-4">
                    <h2 className="text-2xl font-extrabold text-white tracking-tight">
                        Senior Java Developer
                    </h2>
                    <div className="flex items-center gap-2">
                        <button className="p-2 text-foreground-muted hover:text-white transition-colors">
                            <Trash2 className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-foreground-muted hover:text-white transition-colors">
                            <Edit2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                <nav className="flex items-center gap-6">
                    <div className="text-sm font-bold border-b-2 border-status-new pb-1 -mb-[26px]">
                        Kanban board
                    </div>
                    <div className="text-sm font-bold text-foreground-muted hover:text-white transition-colors pb-1 cursor-pointer">
                        Job info
                    </div>
                </nav>
            </div>

            <div className="flex items-center gap-4">
                <div className="relative">
                    <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-foreground-muted" />
                    <input
                        type="text"
                        placeholder="Search"
                        className="bg-white/5 border border-white/5 rounded-xl pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-status-new transition-all w-64"
                    />
                </div>

                <button className="flex items-center gap-2 px-4 py-2 bg-status-new hover:bg-opacity-90 transition-all rounded-xl text-white text-sm font-bold shadow-lg shadow-status-new/20">
                    <UserPlus className="w-4 h-4" />
                    Invite candidate
                </button>

                <div className="w-px h-6 bg-white/10 mx-2" />

                <button className="p-2 text-foreground-muted hover:text-white transition-colors relative">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-status-shortlisted rounded-full border border-background" />
                </button>
            </div>
        </header>
    );
}
