## 2026-04-04 - [Tooltips for Icon-only Buttons]
**Learning:** Icon-only buttons (like Attach, Mic, Export) can be ambiguous even with good iconography. Adding tooltips improves discoverability without cluttering the UI. Removing the native `title` attribute is essential to prevent double-tooltips when using custom components like Radix UI Tooltip.
**Action:** Always wrap icon-only buttons with the `Tooltip` component and ensure `TooltipTrigger` has `asChild` to preserve styling.
