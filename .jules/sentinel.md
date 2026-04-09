## 2026-05-21 - [FastAPI Parameter Order with Dependencies]
**Vulnerability:** Broken Authentication (Missing dependencies)
**Learning:** In FastAPI, parameters with default values (including those using `Depends()`) must come after parameters without default values. Adding `CurrentUser` dependencies to endpoints with existing `Query` or `Body` parameters requires careful ordering to avoid `SyntaxError`.
**Prevention:** Always place dependencies like `CurrentUser` before parameters with `Query`, `Path`, or `Body` if they have defaults, or ensure all parameters follow the correct Python function signature rules.
