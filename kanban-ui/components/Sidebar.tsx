"use client";

import React from "react";
import {
    Briefcase,
    Users,
    Layout,
    BookOpen,
    Gamepad2,
    Music,
    Globe,
    Settings,
    Bell
} from "lucide-react";

const navItems = [
    { icon: Layout, label: "Explorar", active: true },
    { icon: Briefcase, label: "Criação" },
    { icon: Users, label: "Trabalho" },
    { icon: BookOpen, label: "Educação" },
    { icon: Gamepad2, label: "Jogos" },
    { icon: Music, label: "Áudio e Vídeo" },
    { icon: Globe, label: "Rede e Internet" },
    { icon: Settings, label: "Util Requisitos" },
    { icon: Bell, label: "Notificações" },
];

const jobs = [
    { label: "Manager", count: "2000$" },
    { label: "UI/UX Designer", count: "3500$" },
    { label: "Senior Java Developer", count: "3000$ - 4000$", active: true },
    { label: "Graphic Designer", count: "1500-2500$" },
];

export default function Sidebar() {
    return (
        <aside className="w-64 bg-sidebar border-r border-white/5 flex flex-col h-screen shrink-0 overflow-y-auto">
            <div className="p-6">
                <div className="flex items-center gap-3 mb-10">
                    <div className="w-8 h-8 rounded-lg bg-status-new flex items-center justify-center">
                        <Layout className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-bold text-lg tracking-tight">ClawDevs</span>
                </div>

                <nav className="space-y-1 mb-8">
                    {navItems.map((item, i) => (
                        <div
                            key={i}
                            className={`sidebar-item ${item.active ? 'sidebar-item-active' : 'text-foreground-muted'}`}
                        >
                            <item.icon className="w-5 h-5" />
                            <span className="text-sm font-medium">{item.label}</span>
                        </div>
                    ))}
                </nav>

                <div className="mt-10">
                    <h3 className="px-4 text-[11px] font-bold text-foreground-muted uppercase tracking-widest mb-4">
                        Jobs / Agentes
                    </h3>
                    <div className="space-y-1">
                        {jobs.map((job, i) => (
                            <div
                                key={i}
                                className={`flex flex-col px-4 py-3 rounded-lg transition-colors cursor-pointer ${job.active ? 'bg-white/5 border border-white/5' : 'hover:bg-white/5'
                                    }`}
                            >
                                <span className={`text-sm font-semibold ${job.active ? 'text-white' : 'text-foreground-muted'}`}>
                                    {job.label}
                                </span>
                                <span className="text-[11px] text-foreground-muted/60 mt-1">
                                    {job.count}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="mt-auto p-6 border-t border-white/5">
                <div className="flex items-center gap-3 px-4 py-3 bg-white/5 rounded-xl cursor-pointer hover:bg-white/10 transition-colors">
                    <div className="w-8 h-8 rounded-full bg-status-interviewed flex-shrink-0" />
                    <div className="overflow-hidden">
                        <p className="text-sm font-bold truncate">Diretor Luke</p>
                        <p className="text-[11px] text-foreground-muted truncate">Admin Plane</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}
