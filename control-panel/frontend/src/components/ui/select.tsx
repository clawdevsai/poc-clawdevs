import * as React from "react";
import { ChevronDown } from "lucide-react";

import { cn } from "@/lib/utils";

type SelectProps = React.ComponentProps<"select">;

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => (
    <div className="relative">
      <select
        ref={ref}
        data-slot="select"
        className={cn(
          "h-9 w-full appearance-none rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 pr-8 text-sm text-[hsl(var(--foreground))] outline-none transition-colors focus-visible:border-[hsl(var(--primary))] focus-visible:ring-2 focus-visible:ring-[hsl(var(--primary))/0.25] disabled:cursor-not-allowed disabled:opacity-55",
          className
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-[hsl(var(--muted-foreground))]" />
    </div>
  )
);
Select.displayName = "Select";

export { Select };
