"use client";

import { usePathname, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { LogOut, Menu, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { customInstance } from "@/lib/axios-instance";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const BREADCRUMBS: Record<string, string> = {
  "/": "Dashboard",
  "/monitoring": "Monitoramento",
  "/agents": "Agentes",
  "/chat": "Chat",
  "/sessions": "Sessões",
  "/approvals": "Aprovações",
  "/tasks": "Tarefas",
  "/sdd": "SDD",
  "/memory": "Memória",
  "/crons": "Crons",
  "/cluster": "Cluster",
  "/settings": "Settings",
};

type HeaderProps = {
  onOpenMobileNav: () => void;
};

export function Header({ onOpenMobileNav }: HeaderProps) {
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

  const subtitle =
    pathname === "/"
      ? "Mission control overview"
      : "ClawDevs AI Control Panel";

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-[hsl(var(--border))] bg-[hsl(var(--card))/0.92] px-3 backdrop-blur-sm sm:px-5">
      <div className="flex min-w-0 items-center gap-2.5">
        <button
          type="button"
          onClick={onOpenMobileNav}
          className="inline-flex h-8 w-8 items-center justify-center rounded-md text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/40 hover:text-[hsl(var(--foreground))] md:hidden"
          aria-label="Abrir menu"
        >
          <Menu className="h-4 w-4" />
        </button>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-[hsl(var(--foreground))]">
            {title}
          </p>
          <p className="truncate text-[11px] text-[hsl(var(--muted-foreground))]">
            {subtitle}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        {pending > 0 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Link
                href="/approvals"
                className="inline-flex items-center gap-1.5 rounded-md border border-amber-300/30 bg-amber-400/10 px-2 py-1 text-xs font-medium text-amber-300 transition-colors hover:bg-amber-400/15"
                aria-label={`${pending} aprovação${pending !== 1 ? "ões" : ""} pendente${pending !== 1 ? "s" : ""}`}
              >
                <ShieldAlert size={14} />
                <span className="font-semibold">{pending > 99 ? "99+" : pending}</span>
              </Link>
            </TooltipTrigger>
            <TooltipContent>
              {pending} aprovação{pending !== 1 ? "ões" : ""} pendente{pending !== 1 ? "s" : ""}
            </TooltipContent>
          </Tooltip>
        )}

        <button
          onClick={logout}
          className="inline-flex items-center gap-1.5 rounded-md border border-[hsl(var(--border))] px-2 py-1 text-xs text-[hsl(var(--muted-foreground))] transition-colors hover:bg-[hsl(var(--muted))]/45 hover:text-[hsl(var(--foreground))]"
          aria-label="Sair do sistema"
        >
          <LogOut size={14} />
          Sair
        </button>
      </div>
    </header>
  );
}
