"use client";
import React from "react";
import type { AgentStatus } from "../../lib/api";

interface Props {
  status: AgentStatus;
  size?: "sm" | "md";
}

const LABELS: Record<AgentStatus, string> = {
  active: "Ativo",
  idle: "Inativo",
  offline: "Offline",
};

export default function StatusDot({ status, size = "md" }: Props) {
  const sz = size === "sm" ? "w-1.5 h-1.5" : "w-2 h-2";
  const cls =
    status === "active"
      ? `${sz} rounded-full bg-green-400 shadow-[0_0_6px_rgba(74,222,128,0.7)] animate-pulse`
      : status === "idle"
      ? `${sz} rounded-full bg-amber-400`
      : `${sz} rounded-full bg-slate-500`;
  return (
    <span title={LABELS[status]} className={cls} />
  );
}
