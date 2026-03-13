# SOLID

Use this skill when defining or reviewing code architecture to keep modules maintainable and extensible.

Guidelines:
- Apply single responsibility per module/class.
- Design for extension, not fragile modification.
- Keep subtype behavior compatible with contracts.
- Prefer small, focused interfaces.
- Depend on abstractions and inject concrete implementations.

Checklist:
1. Identify responsibilities mixed in the same unit.
2. Extract interfaces at stable boundaries.
3. Separate policy (domain) from mechanism (infra).
4. Validate testability after refactor.
