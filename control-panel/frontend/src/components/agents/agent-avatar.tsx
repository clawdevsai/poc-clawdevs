import { cn } from "@/lib/utils"

// Deterministic color from slug string
function slugColor(slug: string): string {
  const colors = [
    "#00FF9C", // primary green
    "#00C2FF", // cyan
    "#A78BFA", // purple
    "#F472B6", // pink
    "#FB923C", // orange
    "#34D399", // emerald
    "#60A5FA", // blue
    "#FBBF24", // amber
    "#F87171", // red
    "#4ADE80", // green
    "#38BDF8", // sky
    "#C084FC", // violet
    "#E879F9", // fuchsia
  ]
  let hash = 0
  for (let i = 0; i < slug.length; i++) {
    hash = (hash * 31 + slug.charCodeAt(i)) >>> 0
  }
  return colors[hash % colors.length]
}

function getInitials(name: string): string {
  return name
    .split(/[\s_-]+/)
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

type AvatarSize = "sm" | "md" | "lg"

const sizeClasses: Record<AvatarSize, string> = {
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-xs",
  lg: "h-16 w-16 text-lg",
}

interface AgentAvatarProps {
  slug: string
  displayName: string
  size?: AvatarSize
  className?: string
}

export function AgentAvatar({
  slug,
  displayName,
  size = "md",
  className,
}: AgentAvatarProps) {
  const color = slugColor(slug)
  const initials = getInitials(displayName || slug)

  return (
    <div
      className={cn(
        "rounded-full flex items-center justify-center shrink-0 font-bold border",
        sizeClasses[size],
        className
      )}
      style={{
        backgroundColor: `${color}1A`, // ~10% opacity
        borderColor: `${color}4D`,     // ~30% opacity
        color,
      }}
      aria-label={displayName}
    >
      {initials}
    </div>
  )
}
