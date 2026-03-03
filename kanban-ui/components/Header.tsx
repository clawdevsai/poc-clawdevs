"use client";

import React from "react";

export default function Header() {
    return (
        <header className="flex items-center justify-between py-6 mb-8 border-b border-white/5">
            <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
                    <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                    </svg>
                </div>
                <div>
                    <h1 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
                        ClawDevs <span className="text-indigo-500">Kanban</span>
                    </h1>
                    <p className="text-xs text-gray-500 font-medium">Monitoramento do Pipeline de Agentes</p>
                </div>
            </div>

            <div className="flex items-center gap-3">
                {/* Diretor simple indicator */}
                <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-lg border border-white/5">
                    <div className="w-2 h-2 rounded-full bg-indigo-500" />
                    <span className="text-xs font-bold text-gray-300">DIRETOR</span>
                </div>
            </div>
        </header>
    );
}
