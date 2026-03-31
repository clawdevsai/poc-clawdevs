# Example: MVP Implementation

## Scenario

**Requirements**:
- Volume: 1k requests/day (prototype)
- Latency: <2s (not critical)
- Reliability: 99% (acceptable for MVP)
- Cost: Minimal
- Speed: **CRITICAL** (launch in 2 weeks)

## Recommended Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Language | **TypeScript/Node** | Fastest development, good ecosystem |
| Protocol | **REST** | Simple, well-understood, tools everywhere |
| Database | **SQLite** | Zero setup, file-based, enough for MVP |
| Pattern | **Monolith** | Single codebase, simple deployment |
| Messaging | **None** | Synchronous only, add later if needed |

## Implementation Approach

### Minimal Setup

```
Express.js → SQLite file
(Entire stack: ~50 lines of code for starter)
```

### Development Strategy

1. **Day 1-3**: Core API
   - User endpoints
   - Basic authentication
   - SQLite schema

2. **Day 4-7**: Features
   - Main feature logic
   - Basic error handling
   - Logging

3. **Day 8-10**: Testing
   - Unit tests (>70% coverage)
   - Manual testing

4. **Day 11-14**: Launch
   - Deploy to Heroku/Railway (free tier)
   - Monitor and fix bugs
   - Gather user feedback

### Database

```sql
-- Minimal schema
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT UNIQUE,
  created_at DATETIME
);

CREATE TABLE data (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  payload TEXT
);
```

### Deployment

```
Option 1 - Heroku Free Tier:
  - Push to Heroku, done
  - Cost: $0

Option 2 - Railway/Render:
  - Simple git push deployment
  - Cost: $0-5/month

Option 3 - EC2 + RDS:
  - More control, more ops
  - Cost: ~$15-20/month
```

## Quality Gates

- ✅ Minimum viable test coverage: 70%
- ✅ Code runs without errors
- ✅ Manual testing of happy path
- ✅ Basic error handling
- ⚠️ Not required: load testing, security hardening, monitoring

## Cost Estimate

**Free**:
- Development: Your laptop
- Deployment: Free tier Heroku/Railway
- Database: SQLite (embedded)
- Total: $0/month (first months)

**After launch** (when paying users arrive):
- Upgrade: ~$50-100/month for growth

## Timeline

**2 weeks to launch** ✓

## Trade-offs

✅ Strengths:
- Fastest possible development
- Lowest cost
- Simple to understand
- Easy to iterate

⚠️ Trade-offs:
- Not scalable beyond 100k requests/month
- SQLite not ideal for concurrency
- Will need full rewrite for scale
- No distributed features

## Migration Path

When MVP succeeds and you get traction:
1. Migrate from SQLite → PostgreSQL
2. Add caching (Redis)
3. Split monolith → services (if needed)
4. Add monitoring/observability
5. Load test and optimize

**Key insight**: Build for MVP success, plan migration to scale.
