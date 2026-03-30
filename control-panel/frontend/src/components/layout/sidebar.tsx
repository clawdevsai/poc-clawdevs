"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
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
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/agents", label: "Agentes", icon: Bot },
  { href: "/chat", label: "Chat", icon: MessagesSquare },
  { href: "/sessions", label: "Sessões", icon: MessageSquare },
  { href: "/approvals", label: "Aprovações", icon: ShieldCheck, badge: "approvals" },
  { href: "/tasks", label: "Tarefas", icon: CheckSquare },
  { href: "/sdd", label: "SDD", icon: FileText },
  { href: "/memory", label: "Memória", icon: Brain },
  { href: "/crons", label: "Crons", icon: Clock },
  { href: "/cluster", label: "Cluster", icon: Server },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const [collapsed, setCollapsed] = useState(false);

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
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">Control Panel</p>
          </div>
        )}
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              onClick={() => setCollapsed((c) => !c)}
              className="ml-auto text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
              aria-label={collapsed ? "Expandir menu" : "Colapsar menu"}
            >
              {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>
          </TooltipTrigger>
          <TooltipContent side="right">
            {collapsed ? "Expandir" : "Colapsar"}
          </TooltipContent>
        </Tooltip>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          const badge = item.badge === "approvals" && pendingCount > 0 ? pendingCount : null;

          return (
            <Tooltip key={item.href} delayDuration={0} disableHoverableContent={!collapsed}>
              <TooltipTrigger asChild>
                <Link
                  href={item.href}
                  className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors relative",
                collapsed ? "justify-center" : "",
                isActive
                  ? "bg-[hsl(var(--primary)/0.15)] text-[hsl(var(--primary))] font-medium"
                  : "text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--secondary))]"
              )}
            >
              <span className="relative shrink-0">
                <Icon size={16} />
                {badge !== null && collapsed && (
                  <span className="absolute -top-1.5 -right-1.5 w-3.5 h-3.5 rounded-full bg-[hsl(var(--primary))] text-black text-[9px] font-bold flex items-center justify-center">
                    {badge > 9 ? "9+" : badge}
                  </span>
                )}
              </span>
                  {!collapsed && (
                    <>
                      <span className="flex-1">{item.label}</span>
                      {badge !== null && (
                        <span className="ml-auto rounded-full bg-[hsl(var(--primary))] text-black text-[10px] font-bold min-w-[18px] h-[18px] flex items-center justify-center px-1">
                          {badge > 99 ? "99+" : badge}
                        </span>
                      )}
                    </>
                  )}
                </Link>
              </TooltipTrigger>
              {collapsed && (
                <TooltipContent side="right">
                  {item.label}
                </TooltipContent>
              )}
            </Tooltip>
          );
        })}
      </nav>
    </aside>
  );
}
