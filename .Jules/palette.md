## 2026-04-08 - Tooltip implementation on buttons
**Learning:** When using Radix UI Tooltips with buttons, the `TooltipTrigger` should wrap the `button` using `asChild`. Placing the trigger inside the button (e.g., around only the icon) is an anti-pattern that reduces the trigger area to just the icon and, crucially, breaks keyboard accessibility because focusing the button via Tab won't activate the tooltip.
**Action:** Always wrap the interactive element (button, link) with `TooltipTrigger asChild` to ensure consistent hover and focus behavior.
