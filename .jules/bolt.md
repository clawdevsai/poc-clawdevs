## 2025-05-15 - Optimize aggregations with SQL func
**Learning:** Fetching full ORM objects and then using `len()` or `sum()` in Python is an anti-pattern that leads to high memory usage and unnecessary data transfer.
**Action:** Use `func.count()` and `func.sum()` within `select()` to perform aggregations at the database level.
