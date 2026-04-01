## 2026-04-01 - [Tooltip pattern for icon-only buttons]
**Learning:** Icon-only buttons should always be accompanied by accessible tooltips (Radix UI) instead of native `title` attributes to ensure a consistent, stylable, and accessible UX across different browsers and themes.
**Action:** Replace all native `title` attributes with the `Tooltip` component and ensure all icon-only buttons have an `aria-label` and a corresponding tooltip.
