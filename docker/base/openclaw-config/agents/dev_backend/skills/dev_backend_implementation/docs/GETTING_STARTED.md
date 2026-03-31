# Getting Started Guide

A practical walkthrough to use the `dev_backend` skill for your architecture decisions.

## 5-Minute Quick Start

### Step 1: Import the Hook

```typescript
import { beforeExecution } from 'dev_backend/hooks/before_execution';
```

### Step 2: Provide Requirements (3 Ways)

**Option A: Natural Language**
```typescript
const result = await beforeExecution({
  conversation: 'We need to handle 1M requests per second with latency under 100ms'
});
```

**Option B: Structured Config**
```typescript
const result = await beforeExecution({
  config: {
    volume: 'extreme',
    latency: 'realtime',
    costSensitivity: 'low',
    reliability: 'critical',
    dataComplexity: 'complex',
    timeToMarket: 'normal'
  }
});
```

**Option C: Mix & Match**
```typescript
const result = await beforeExecution({
  conversation: 'High-performance backend',
  config: { costSensitivity: 'low' },
  systemPrompt: 'Critical reliability required'
});
```

### Step 3: Use the Results

```typescript
console.log('Language:', result.recommendation?.language);     // 'go'
console.log('Database:', result.recommendation?.database);     // 'PostgreSQL + Redis'
console.log('Pattern:', result.recommendation?.pattern);       // 'microservices'

console.log('\nAnalysis:');
console.log(result.analysis);                                   // Markdown with full details

console.log('\nNext Steps:');
result.nextSteps.forEach(step => console.log('- ' + step));
```

## Common Scenarios

### Scenario 1: Startup MVP (2-Week Launch)

**Your Situation**: Bootstrap-funded startup, need to validate market fit quickly

**Input**:
```typescript
const result = await beforeExecution({
  conversation: `
    We're a startup with 2 weeks to launch our MVP. Budget is tight,
    team is 3 developers. Building a simple social networking app.
    Initial load is low, maybe 1000 users day one. Cost is critical.
  `
});
```

**Expected Output**:
```typescript
{
  language: 'typescript',
  protocol: 'rest',
  database: 'sqlite',
  pattern: 'serverless',
  messaging: 'none'
}
```

**What This Means**:
- **TypeScript**: Fast development, full-stack JavaScript
- **REST**: Simple to implement, widely understood
- **SQLite**: Zero infrastructure, works locally
- **Serverless**: Deploy on free tier (AWS Lambda, Google Cloud Run)
- **Cost**: $0-30/month initially

**Next Steps** (from `result.nextSteps`):
1. Initialize Express.js project
2. Set up SQLite locally
3. Define REST endpoints
4. Deploy to AWS Lambda
5. Set up monitoring

**Implementation Timeline**:
- Day 1-2: Project setup and scaffolding
- Day 3-5: Core API endpoints
- Day 6-8: Database schema and queries
- Day 9-10: Frontend integration
- Day 11-12: Testing and bug fixes
- Day 13-14: Deployment and polish

---

### Scenario 2: Scale-Up from MVP

**Your Situation**: MVP gained traction (100k DAU), need to scale from SQLite+Serverless

**Input**:
```typescript
const result = await beforeExecution({
  conversation: `
    Our MVP is handling 100k daily active users. We're getting 100k requests
    per day (avg 1 req/sec but spiky). SQLite is becoming a bottleneck.
    Uptime matters now (99%+). We have budget and team of 8 engineers.
  `
});
```

**Expected Output**:
```typescript
{
  language: 'typescript',
  protocol: 'rest',
  database: 'postgresql',
  pattern: 'monolith',
  messaging: 'none'
}
```

**Migration Path from MVP**:
1. Keep Express.js (already working)
2. Replace SQLite with PostgreSQL
3. Keep REST (already built)
4. Move from Serverless to container (Docker)
5. Deploy on container platform (Heroku, Railway, Render)

**Cost**: $500-2000/month

**Timeline**: 4-6 weeks

---

### Scenario 3: High-Performance Backend

**Your Situation**: Building e-commerce backend for major retailer (Black Friday ready)

**Input**:
```typescript
const result = await beforeExecution({
  conversation: `
    E-commerce platform for major retailer. Need to handle 1 million
    requests per second during Black Friday. Latency <100ms for checkout.
    99.99% uptime required. Complex product catalog with recommendations.
    Team of 20+ engineers. Budget is not a concern.
  `
});
```

**Expected Output**:
```typescript
{
  language: 'go',
  protocol: 'grpc',
  database: 'PostgreSQL + Redis',
  pattern: 'microservices',
  messaging: 'kafka'
}
```

**Architecture Overview**:

```
                     Load Balancer
                          │
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
Product Service    Order Service          Payment Service
    │                      │                      │
    ├─→ PostgreSQL        ├─→ PostgreSQL        ├─→ PostgreSQL
    │                      │                      │
    └─→ Redis Cache       └─→ Redis Cache       └─→ Redis Cache
                           │
                           ▼
                       Kafka (Event Bus)
                           │
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
Search Service      Notification Service    Analytics Service
```

**Tech Stack Details**:
- **Language**: Go (goroutines for 1M concurrent connections)
- **Protocol**: gRPC (efficient binary, HTTP/2 multiplexing)
- **Database**: PostgreSQL (primary) + Redis (cache)
- **Pattern**: Microservices (independent scaling)
- **Messaging**: Kafka (event-driven, durable)

**Implementation Phases**:

Phase 1 (Weeks 1-4): Foundation
- Service discovery (Kubernetes)
- API Gateway
- Database replication
- gRPC communication

Phase 2 (Weeks 5-8): Core Services
- Product catalog microservice
- Order processing service
- Payment integration
- Inventory management

Phase 3 (Weeks 9-12): Reliability
- Circuit breakers
- Bulkheads
- Distributed tracing
- Comprehensive monitoring

Phase 4 (Weeks 13-16): Performance
- Load testing (Locust, k6)
- Query optimization
- Caching strategy
- CDN integration

**Cost**: $5000-50000/month (depending on volume)

---

### Scenario 4: Real-Time Analytics Dashboard

**Your Situation**: Building live analytics platform for SaaS

**Input**:
```typescript
const result = await beforeExecution({
  conversation: `
    Real-time analytics dashboard. Customers have 1000+ IoT sensors
    streaming data. Need live updates <500ms. Processing complex metrics
    and anomaly detection. Eventually consistent is fine. Team of 6.
    Mid-range budget.
  `
});
```

**Expected Output**:
```typescript
{
  language: 'go',
  protocol: 'websocket',
  database: 'PostgreSQL + TimescaleDB',
  pattern: 'event_driven',
  messaging: 'kafka'
}
```

**Implementation Stack**:

```
Sensors → Kafka Broker → Stream Processors
                              │
                              ▼
                        TimescaleDB
                        (time-series)
                              │
                              ▼
                         API Server
                        (WebSocket)
                              │
                              ▼
                    Frontend Dashboard
                     (real-time updates)
```

**Tech Details**:
- **Sensors**: MQTT protocol sending to Kafka
- **Kafka**: High-throughput event ingestion
- **Go Processors**: Consume events, compute metrics
- **TimescaleDB**: Optimized for time-series data
- **WebSocket**: Push updates to frontend
- **Frontend**: React with WebSocket subscriptions

**Cost**: $1000-5000/month

---

## Reference: Requirement Values

### Volume
- **low**: <1,000 requests/second
- **medium**: 1,000-100,000 requests/second
- **high**: 100,000-1,000,000 requests/second
- **extreme**: >1,000,000 requests/second

### Latency
- **relaxed**: <5 seconds (batch jobs)
- **normal**: <1 second (regular operations)
- **responsive**: <500ms (user-facing)
- **realtime**: <100ms (interactive)
- **ultra**: <10ms (real-time streaming)

### Cost Sensitivity
- **high**: Minimize costs (startup budget)
- **medium**: Balanced cost/performance
- **low**: Cost secondary to other factors
- **unlimited**: Cost not a concern

### Reliability
- **best_effort**: 95%+ uptime
- **acceptable**: 99%+ uptime
- **critical**: 99.9%+ uptime
- **highly_critical**: 99.99%+ uptime

### Data Complexity
- **simple**: CRUD, flat structures
- **moderate**: Entity relationships, basic joins
- **complex**: Graph-like structures, complex joins
- **extreme**: ML pipelines, streaming, real-time analytics

### Time to Market
- **asap**: Days to weeks
- **normal**: Weeks to months
- **flexible**: Months or longer

## Troubleshooting

### Problem: "No matching pattern found"

**Cause**: Conflicting requirements (e.g., extreme volume + $0 budget)

**Solution**:
1. Adjust one requirement to be more realistic
2. Check if you're in a transition phase (scaling up)
3. Consider a hybrid approach

**Example**:
```typescript
// Too constraining
const impossible = {
  volume: 'extreme',      // 1M+ req/s
  costSensitivity: 'high' // Bootstrap budget
  // Can't do both!
};

// Realistic options
const realistic = {
  volume: 'extreme',
  costSensitivity: 'low'  // Need budget for scale
};
```

### Problem: Low confidence score

**Cause**: Incomplete or vague requirements

**Solution**: Provide more specific information

```typescript
// Low confidence (vague)
const vague = { conversation: 'We need a fast backend' };

// High confidence (specific)
const specific = {
  conversation: 'We need to handle 100k req/sec with <200ms latency'
};
```

### Problem: Wrong recommendation

**Solution**: Check your requirements carefully

```typescript
// Verify parsing
console.log(result.requirements);

// Verify pattern matching
console.log(result.recommendation?.pattern);

// Adjust and try again
if (result.confidence.requirementsParsing < 70) {
  // Provide more explicit requirements
}
```

## Next: Deep Dives

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: How the system works internally
- **[PRINCIPLES.md](PRINCIPLES.md)**: Design philosophy and patterns
- **[README.md](../README.md)**: Complete reference with more examples

## Questions?

Check the test files for working examples:
- `tests/unit/decisions.test.ts` - Pattern matching examples
- `tests/unit/recommendations.test.ts` - Recommendation generation
- `tests/integration/before_execution.test.ts` - End-to-end flows
