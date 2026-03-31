# Decisions Matrix

## Tech Stack Recommendations by Scenario

### High Performance (1M+ req/s, <100ms latency)

| Aspect | Recommendation |
|--------|-----------------|
| Language | Go or Rust |
| Protocol | gRPC |
| Database | PostgreSQL + Redis |
| Pattern | Microservices |
| Messaging | Kafka |
| Reasoning | Efficiency at extreme scale |

### Low Cost (Minimal infrastructure)

| Aspect | Recommendation |
|--------|-----------------|
| Language | TypeScript/Node or Python |
| Protocol | REST |
| Database | SQLite/PostgreSQL |
| Pattern | Serverless or Monolith |
| Messaging | None (sync) or SQS |
| Reasoning | Minimize operational overhead |

### High Reliability (99.99% uptime)

| Aspect | Recommendation |
|--------|-----------------|
| Language | Go or Rust |
| Protocol | gRPC |
| Database | PostgreSQL + failover |
| Pattern | Distributed, multi-region |
| Messaging | Kafka |
| Reasoning | Fault tolerance and resilience |

### MVP (Time-to-market critical)

| Aspect | Recommendation |
|--------|-----------------|
| Language | TypeScript/Node |
| Protocol | REST |
| Database | PostgreSQL |
| Pattern | Monolith |
| Messaging | None initially |
| Reasoning | Speed of development |

## Decision Flow

1. Identify requirements (volume, latency, cost, reliability)
2. Look up matching scenario in matrix
3. Review reasoning and trade-offs
4. Validate against constraints
5. Document decision
