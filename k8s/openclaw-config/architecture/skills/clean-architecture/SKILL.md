# Clean Architecture

Use this skill when defining service structure with clear separation between domain and delivery/infrastructure layers.

Guidelines:
- Keep domain entities independent from frameworks.
- Use use-cases/application services for orchestration.
- Place adapters at the outer layers.
- Enforce dependency direction toward the domain core.
- Define stable ports for external systems.

Checklist:
1. Define entities, use cases, and interface adapters.
2. Ensure infra depends on application/domain, never inverse.
3. Keep DTO mapping explicit at boundaries.
4. Validate architecture with unit and integration tests.
