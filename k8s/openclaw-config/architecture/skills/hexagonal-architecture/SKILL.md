# Hexagonal Architecture

Use this skill when you need to isolate business logic from databases, APIs, queues, and UI channels.

Guidelines:
- Keep domain logic inside the hexagon (core).
- Expose domain operations via input ports.
- Integrate external systems through output ports + adapters.
- Avoid leaking adapter details into domain code.
- Test the core with fake adapters.

Checklist:
1. Define inbound and outbound ports first.
2. Implement adapters per external technology.
3. Wire dependencies in composition root only.
4. Ensure replacing adapters does not change domain behavior.
