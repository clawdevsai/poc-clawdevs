# Principles

## SOLID

**Single Responsibility**: Each module has one reason to change
**Open/Closed**: Extensible via hooks, not modification
**Liskov Substitution**: Implementations are interchangeable
**Interface Segregation**: Focused, minimal interfaces
**Dependency Inversion**: Depend on abstractions, not implementations

## KISS (Keep It Simple, Stupid)

- Clear and direct logic
- No over-engineering
- Understandable to future developers

## YAGNI (You Ain't Gonna Need It)

- Remove unused features
- Don't add "for the future"
- Implement what's needed now

## DRY (Don't Repeat Yourself)

- Shared logic in utils/
- Reusable schemas in schemas/
- Matrix centralized in decisions/

## DDD (Domain-Driven Design)

- Ubiquitous language (requirements, recommendations, patterns)
- Bounded contexts per agent
- Entity-centric design

## TDD (Test-Driven Development)

- Write tests before implementation
- Minimum 80% coverage
- Unit and integration tests

## Clean Code

- Descriptive names
- Small functions
- Explicit error handling
- Self-documenting code
