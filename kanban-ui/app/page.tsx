import React from "react";
import Header from "../components/Header";
import KanbanBoard from "../components/KanbanBoard";

export default function Home() {
  return (
    <main className="container mx-auto px-4 md:px-6 h-screen flex flex-col overflow-hidden">
      <Header />

      <section className="flex-1 min-h-0 relative">
        {/* Board component handles its own fetching and real-time updates */}
        <KanbanBoard />

        {/* Soft background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-indigo-600/5 blur-[120px] rounded-full pointer-events-none -z-10" />
      </section>

      <footer className="py-4 border-t border-white/5 text-[10px] text-gray-600 font-mono tracking-widest flex justify-between items-center shrink-0">
        <div>CLAWDEVS AGENT PIPELINE MONITOR • V1.0.0</div>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 uppercase">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/50" />
            Minikube Cluster Ready
          </span>
          <span className="flex items-center gap-1.5 uppercase">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500/50" />
            OpenClaw Gateway Connected
          </span>
        </div>
      </footer>
    </main>
  );
}
