import React from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import KanbanBoard from "../components/KanbanBoard";
import ActivityFeed from "../components/ActivityFeed";

export default function Home() {
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <div className="flex-1 flex overflow-hidden">
          <main className="flex-1 overflow-hidden p-8">
            <KanbanBoard />
          </main>

          <aside className="w-80 border-l border-white/5 bg-white/[0.01] pt-8">
            <ActivityFeed />
          </aside>
        </div>
      </div>
    </div>
  );
}
