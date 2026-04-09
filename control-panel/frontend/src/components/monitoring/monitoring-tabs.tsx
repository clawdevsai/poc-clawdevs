import { cn } from "@/lib/utils"

const TABS = ["Sessions", "Tasks", "Agents", "Metrics"] as const

export type MonitoringTab = (typeof TABS)[number]

interface MonitoringTabsProps {
  active: MonitoringTab
  onChange: (tab: MonitoringTab) => void
}

export function MonitoringTabs({ active, onChange }: MonitoringTabsProps) {
  return (
    <div className="flex flex-wrap gap-2 rounded-xl border border-[#1b1b1b] bg-[#0f0f0f] p-2">
      {TABS.map((tab) => (
        <button
          key={tab}
          onClick={() => onChange(tab)}
          className={cn(
            "px-3 py-1.5 text-sm font-medium rounded-lg transition-colors",
            active === tab
              ? "bg-[#00bfff] text-black"
              : "text-[hsl(var(--muted-foreground))] hover:text-white"
          )}
        >
          {tab}
        </button>
      ))}
    </div>
  )
}
