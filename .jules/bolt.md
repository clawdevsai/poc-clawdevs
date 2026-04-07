## 2026-04-07 - SQL-level Aggregation for Metrics
**Learning:** Using `len(result.all())` or Python-level `sum()` on SQLAlchemy/SQLModel result sets is a performance anti-pattern that causes O(N) memory overhead and unnecessary data transfer by fetching full ORM objects.
**Action:** Use database-level `func.count()` and `func.sum()` with `session.exec(...).one()` for all counting and summation operations to minimize overhead.
