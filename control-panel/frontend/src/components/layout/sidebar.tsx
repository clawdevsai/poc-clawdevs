"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { cn } from "@/lib/utils";
import { customInstance } from "@/lib/axios-instance";
import { wsManager } from "@/lib/ws";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import {
  LayoutDashboard,
  Bot,
  MessageSquare,
  MessagesSquare,
  ShieldCheck,
  CheckSquare,
  FileText,
  Brain,
  Clock,
  Server,
  Settings,
  BarChart3,
  PanelLeftClose,
  PanelLeftOpen,
  X,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/monitoring", label: "Monitoramento", icon: BarChart3 },
  { href: "/agents", label: "Agentes", icon: Bot },
  { href: "/chat", label: "Chat", icon: MessagesSquare },
  { href: "/sessions", label: "Sessões", icon: MessageSquare },
  { href: "/approvals", label: "Aprovações", icon: ShieldCheck, badge: "approvals" },
  { href: "/tasks", label: "Tarefas", icon: CheckSquare },
  { href: "/sdd", label: "SDD", icon: FileText },
  { href: "/memory", label: "Memória", icon: Brain },
  { href: "/crons", label: "Crons", icon: Clock },
  { href: "/cluster", label: "Cluster", icon: Server },
  { href: "/settings", label: "Configurações", icon: Settings },
];

type SidebarProps = {
  collapsed: boolean;
  onCollapsedChange: (value: boolean) => void;
  mobileOpen: boolean;
  onMobileOpenChange: (value: boolean) => void;
};

export function Sidebar({
  collapsed,
  onCollapsedChange,
  mobileOpen,
  onMobileOpenChange,
}: SidebarProps) {
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const compactDesktop = collapsed && !mobileOpen;

  const { data: statsData } = useQuery({
    queryKey: ["approvals-stats"],
    queryFn: () => customInstance<{ pending: number; approved_today: number; rejected_today: number }>({ url: "/approvals/stats", method: "GET" }),
    refetchInterval: 60_000,
  });

  const pendingCount = statsData?.pending ?? 0;

  useEffect(() => {
    const unsub = wsManager?.subscribe("approvals", () => {
      queryClient.invalidateQueries({ queryKey: ["approvals-stats"] });
    });
    return () => unsub?.();
  }, [queryClient]);

  return (
    <aside
      className={cn(
        "shrink-0 h-screen flex flex-col border-r border-[hsl(var(--border))] bg-[hsl(var(--card))] transition-all duration-200",
        collapsed ? "w-14" : "w-56"
      )}
    >
      {/* Logo */}
      <div className="p-4 border-b border-[hsl(var(--border))] flex items-center justify-between min-h-[57px]">
        {!collapsed && (
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[hsl(var(--primary))] font-bold text-lg">ClawDevs</span>
              <span className="text-[hsl(var(--muted-foreground))] text-xs">AI</span>
            </div>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">Painel de Controle</p>
          </div>
        )}
      >
        <div className="flex h-14 items-center gap-2 border-b border-[hsl(var(--border))] px-3">
          <div className="min-w-0 flex-1 overflow-hidden">
            {compactDesktop ? (
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-[hsl(var(--border))] text-xs font-semibold text-[hsl(var(--primary))]">
                CD
              </span>
            ) : (
              <div>
                <div className="flex items-center gap-2 truncate">
                  <span className="truncate text-base font-semibold tracking-tight text-[hsl(var(--primary))]">
                    ClawDevs
                  </span>
                  <span className="rounded bg-[hsl(var(--primary))/0.14] px-1.5 py-0.5 text-[10px] font-semibold uppercase text-[hsl(var(--primary))]">
                    AI
                  </span>
                </div>
                <p className="truncate text-[11px] text-[hsl(var(--muted-foreground))]">
                  Control Panel
                </p>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => onMobileOpenChange(false)}
            className="inline-flex h-8 w-8 items-center justify-center rounded-md text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/40 hover:text-[hsl(var(--foreground))] md:hidden"
            aria-label="Fechar menu"
          >
            <X className="h-4 w-4" />
          </button>

          <button
            type="button"
            onClick={() => onCollapsedChange(!collapsed)}
            className="hidden h-8 w-8 items-center justify-center rounded-md text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/40 hover:text-[hsl(var(--foreground))] md:inline-flex"
            aria-label={collapsed ? "Expandir menu" : "Colapsar menu"}
          >
            {collapsed ? (
              <PanelLeftOpen className="h-4 w-4" />
            ) : (
              <PanelLeftClose className="h-4 w-4" />
            )}
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-2">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const badge =
              item.badge === "approvals" && pendingCount > 0 ? pendingCount : null;

            const linkNode = (
              <Link
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                onClick={() => onMobileOpenChange(false)}
                className={cn(
                  "group flex h-10 items-center gap-2.5 rounded-lg px-2.5 text-sm transition-colors",
                  compactDesktop ? "justify-center px-0" : "",
                  isActive
                    ? "bg-[hsl(var(--primary))/0.14] text-[hsl(var(--primary))]"
                    : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]/50 hover:text-[hsl(var(--foreground))]"
                )}
              >
                <span className="relative inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-md">
                  <Icon className="h-4 w-4" />
                  {badge !== null && compactDesktop && (
                    <span className="absolute -right-0.5 -top-0.5 inline-flex h-3.5 min-w-3.5 items-center justify-center rounded-full bg-[hsl(var(--primary))] px-1 text-[9px] font-semibold text-[hsl(var(--primary-foreground))]">
                      {badge > 9 ? "9+" : badge}
                    </span>
                  )}
                </span>

                {!compactDesktop && (
                  <>
                    <span className="flex-1 truncate">{item.label}</span>
                    {badge !== null && (
                      <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-[hsl(var(--primary))/0.18] px-1.5 text-[10px] font-semibold text-[hsl(var(--primary))]">
                        {badge > 99 ? "99+" : badge}
                      </span>
                    )}
                  </>
                )}
              </Link>
            );

            if (compactDesktop) {
              return (
                <Tooltip key={item.href} delayDuration={0}>
                  <TooltipTrigger asChild>{linkNode}</TooltipTrigger>
                  <TooltipContent side="right">{item.label}</TooltipContent>
                </Tooltip>
              );
            }

            return <div key={item.href}>{linkNode}</div>;
          })}
        </nav>
      </aside>
    </>
  );
}
