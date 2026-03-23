"use client";

import { usePathname, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { LogOut, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { customInstance } from "@/lib/axios-instance";

const BREADCRUMBS: Record<string, string> = {
  "/": "Dashboard",
  "/agents": "Agentes",
  "/sessions": "Sessões",
  "/approvals": "Aprovações",
  "/tasks": "Tarefas",
  "/sdd": "SDD",
  "/memory": "Memória",
  "/crons": "Crons",
  "/cluster": "Cluster",
  "/settings": "Settings",
};

export function Header() {
  const pathname = usePathname();
  const router = useRouter();

  const title =
    Object.entries(BREADCRUMBS)
      .filter(([key]) => key !== "/" && pathname.startsWith(key))
      .sort((a, b) => b[0].length - a[0].length)[0]?.[1] ??
    BREADCRUMBS[pathname] ??
    "ClawDevs AI";

  const { data: stats } = useQuery({
    queryKey: ["approvals-stats"],
    queryFn: () =>
      customInstance<{ pending: number; approved_today: number; rejected_today: number }>({
        url: "/approvals/stats",
        method: "GET",
      }),
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

  const pending = stats?.pending ?? 0;

  function logout() {
    localStorage.removeItem("panel_token");
    router.push("/login");
  }

  return (
    <header className="h-12 flex items-center justify-between px-4 border-b border-[hsl(var(--border))] bg-[hsl(var(--card))]">
      <h1 className="text-sm font-medium text-[hsl(var(--foreground))]">{title}</h1>

      <div className="flex items-center gap-3">
        {pending > 0 && (
          <Link
            href="/approvals"
            className="flex items-center gap-1.5 text-xs text-yellow-400 hover:text-yellow-300 transition-colors"
            title={`${pending} aprovação${pending !== 1 ? "ões" : ""} pendente${pending !== 1 ? "s" : ""}`}
          >
            <ShieldAlert size={14} />
            <span className="font-semibold">{pending > 99 ? "99+" : pending}</span>
          </Link>
        )}

        <button
          onClick={logout}
          className="flex items-center gap-1.5 text-xs text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
        >
          <LogOut size={14} />
          Sair
        </button>
      </div>
    </header>
  );
}
