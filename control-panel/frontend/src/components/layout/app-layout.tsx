"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Sidebar } from "./sidebar";
import { Header } from "./header";

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

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
