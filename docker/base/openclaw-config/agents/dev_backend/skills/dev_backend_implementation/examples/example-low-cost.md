# Example: Low-Cost Implementation

## Scenario

**Requirements**:
- Volume: 10k requests/second
- Latency: <1s (not critical)
- Reliability: 99%
- Cost: **Critical** (startup budget)

## Recommended Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Language | **TypeScript/Node** | Fast development, abundant libraries |
| Protocol | **REST** | Simple, no special infrastructure |
| Database | **PostgreSQL** | Free, open-source, robust |
| Pattern | **Serverless or Monolith** | No server management overhead |
| Messaging | **SQS or none** | Async when needed, minimal ops |

## Implementation Approach

### Minimal Infrastructure

Option A - Serverless:
```
API Gateway → Lambda → RDS PostgreSQL
(Pay per request, auto-scales)
Cost: ~$50-100/month for this volume
```

Option B - Single Server:
```
EC2 + PostgreSQL (RDS free tier first)
Cost: ~$20-50/month for this volume
```

### Database Strategy

- Single PostgreSQL instance (RDS free tier initially)
- Connection pooling (pgbouncer)
- No caching layer initially (add when needed)

### Async Processing

- Use SQS for email/notifications
- Lambda functions for processing
- Pay only for what you use

## Quality Gates

- Latency: p99 < 1s acceptable
- Throughput: 10k req/s required
- Error rate: < 1%
- Test coverage: >= 70% (pragmatic for MVP)

## Cost Estimate

**Serverless** (recommended for startup):
- Lambda: ~$20/month
- RDS: Free tier (first 12 months)
- API Gateway: ~$5/month
- SQS: ~$5/month
- **Total: ~$30/month** (first year with free tier)

**Self-managed**:
- EC2 t3.micro: ~$10/month
- RDS: ~$15/month
- Total: ~$25/month

## Trade-offs

✅ Strengths:
- Extremely low cost
- Fast time to market
- Minimal operational overhead
- Easy to scale if needed

⚠️ Trade-offs:
- Cold start latency on serverless
- Limited debugging on serverless
- Scale-up costs as volume increases
