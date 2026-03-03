import React from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import KanbanBoard from "../components/KanbanBoard";

export default function Home() {
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        <main className="flex-1 overflow-hidden p-8">
          <KanbanBoard />
        </main>
      </div>
    </div>
  );
}
