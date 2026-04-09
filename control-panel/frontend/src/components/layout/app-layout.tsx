"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { cn } from "@/lib/utils";

function parseJwtPayload(token: string): { exp?: number } | null {
  try {
    const parts = token.split(".");
    if (parts.length < 2) return null;
    const payload = atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(payload);
  } catch {
    return null;
  }
}

export function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("panel_token");
    if (!token && pathname !== "/login") {
      router.replace("/login");
      return;
    }

    if (!token) return;

    const payload = parseJwtPayload(token);
    const exp = payload?.exp;
    if (typeof exp === "number") {
      const now = Math.floor(Date.now() / 1000);
      if (exp <= now) {
        localStorage.removeItem("panel_token");
        router.replace("/login");
      }
    }
  }, [pathname, router]);

  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [pathname]);

  return (
    <div className="min-h-screen bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
      <div className="relative flex min-h-screen overflow-hidden">
        <Sidebar
          collapsed={sidebarCollapsed}
          onCollapsedChange={setSidebarCollapsed}
          mobileOpen={mobileSidebarOpen}
          onMobileOpenChange={setMobileSidebarOpen}
        />
        <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
          <Header onOpenMobileNav={() => setMobileSidebarOpen(true)} />
          <main
            className={cn(
              "flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top,hsla(var(--primary),0.08),transparent_56%)] px-3 py-4 sm:px-5 sm:py-6 xl:py-8",
              sidebarCollapsed ? "xl:px-8" : "xl:px-10"
            )}
          >
            <div className="mx-auto w-full max-w-[1520px]">{children}</div>
          </main>
        </div>
      </div>
    </div>
  );
}
