# Palette's Journal - Critical UX/Accessibility Learnings

## 2026-05-22 - Localization of Relative Dates in Portuguese
**Learning:** For a consistent `pt-BR` experience in a project where `lang="pt-BR"` is set at the layout level, dynamic date strings from `date-fns` must be explicitly passed the `ptBR` locale. Otherwise, they default to English (e.g., "5 minutes ago" instead of "há 5 minutos").
**Action:** Always import `ptBR` from `date-fns/locale` and use it in `formatDistanceToNow` or `format` in the frontend.

## 2026-05-22 - Visual Feedback for Real-time Status
**Learning:** Static color dots for statuses like "working" can feel "stuck" in a real-time dashboard. Adding a subtle animation (`animate-pulse`) provides a "living" feel to the interface, signaling active background work.
**Action:** Use `animate-pulse` on status indicators for active, long-running processes to enhance perceived responsiveness.

## 2026-05-22 - Keyboard Accessibility for Card Links
**Learning:** Large card links (like agent cards) often lack visible focus indicators by default in many UI libraries, making them difficult for keyboard users to navigate.
**Action:** Explicitly add `focus-visible:ring-2` and `focus-visible:outline-none` to all `Link` or `button` cards to ensure a clearly visible focus state.
