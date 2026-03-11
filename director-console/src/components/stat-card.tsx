"use client";

type StatCardProps = {
  label: string;
  value: string | number;
  tone?: "default" | "accent" | "success" | "warning";
};

const tones = {
  default: "text-white",
  accent: "text-cyan-300",
  success: "text-emerald-300",
  warning: "text-amber-300"
};

export function StatCard({ label, value, tone = "default" }: StatCardProps) {
  return (
    <div className="panel rounded-2xl p-5">
      <div className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">{label}</div>
      <div className={`mt-3 text-3xl font-semibold ${tones[tone]}`}>{value}</div>
    </div>
  );
}
