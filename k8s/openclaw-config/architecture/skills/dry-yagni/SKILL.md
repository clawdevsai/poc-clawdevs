# DRY and YAGNI

Use this skill to balance code reuse with pragmatic scope control.

Guidelines:
- Apply DRY to duplicated business rules and shared workflows.
- Avoid DRY for accidental similarity that may diverge soon.
- Apply YAGNI: implement only what current requirements need.
- Delay abstractions until at least two real use cases exist.
- Keep change cost low by refactoring incrementally.

Reference:
- https://scalastic.io/en/solid-dry-kiss/

Checklist:
1. Identify high-cost duplication and remove it.
2. Reject speculative features and premature extensibility.
3. Review abstractions and collapse unused layers.
4. Track simplicity and delivery speed as decision metrics.
