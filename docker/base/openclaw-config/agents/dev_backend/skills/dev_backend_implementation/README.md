# dev_backend Implementation Guide

A comprehensive backend architecture decision system that analyzes non-functional requirements and recommends optimal technology stacks for different scenarios.

## Overview

The `dev_backend` skill provides AI-driven architecture recommendations based on requirements analysis. It examines your project's constraints (volume, latency, cost, reliability, data complexity, time-to-market) and recommends:

- **Programming Language**: Go, Rust, TypeScript, Python, Java, or C#
- **Communication Protocol**: gRPC, REST, WebSocket, GraphQL, or MQTT
- **Database**: PostgreSQL, MongoDB, Redis, DynamoDB, Cassandra, etc.
- **Architectural Pattern**: Monolith, Microservices, Serverless, Event-Driven, Batch, Streaming, or Distributed
- **Messaging Technology**: Kafka, RabbitMQ, SQS, Pub/Sub, or None

## Real-World Examples

### Example 1: High-Performance E-Commerce Platform

**Scenario**: Building a Black Friday-ready e-commerce backend handling 1M requests/second with <100ms latency, critical reliability (99.99% uptime), and complex product/inventory relationships.

**Input**:
```typescript
const requirements = {
  volume: 'extreme',           // 1M+ req/s
  latency: 'realtime',        // <100ms
  costSensitivity: 'low',     // Budget available
  reliability: 'highly_critical',  // 99.99% uptime
  dataComplexity: 'complex',  // Product catalog with relationships
  timeToMarket: 'normal'      // 2-3 months available
};
```

**Output Recommendation**:
```typescript
{
  language: 'go',
  protocol: 'grpc',
  database: 'PostgreSQL + Redis',
  pattern: 'microservices',
  messaging: 'kafka',
  reasoning: "Go offers excellent concurrency with goroutines and produces single-binary deployments..."
}
```

**Implementation Path**:
1. Structure as microservices (Product Service, Inventory Service, Order Service, Payment Service)
2. Use PostgreSQL for transactional data with Redis caching layer
3. gRPC for service-to-service communication (efficient binary protocol)
4. Kafka for order events and inventory updates
5. Deploy across multiple availability zones with automated failover

**Trade-offs**:
- Performance: Excellent (optimized for 1M+ req/s, <100ms p99)
- Development Speed: Medium (Go learning curve, but strong tooling)
- Operational Complexity: High (distributed systems, service mesh)
- Cost Efficiency: Good (efficient resource usage, but infrastructure costs)

---

### Example 2: MVP Startup Backend

**Scenario**: Building a social app MVP that needs to launch in 2 weeks with minimal budget, handling low initial volume, and accepting startup-level reliability.

**Input**:
```typescript
const requirements = {
  volume: 'low',              // <1000 req/s initially
  latency: 'normal',          // <1 second acceptable
  costSensitivity: 'high',    // Bootstrap funded
  reliability: 'acceptable',  // 99%+ uptime acceptable
  dataComplexity: 'simple',   // User profiles, posts, follows
  timeToMarket: 'asap'        // 2 weeks deadline
};
```

**Output Recommendation**:
```typescript
{
  language: 'typescript',
  protocol: 'rest',
  database: 'SQLite',
  pattern: 'serverless',
  messaging: 'none',
  reasoning: "TypeScript maximizes developer velocity with full-stack JavaScript..."
}
```

**Implementation Path**:
1. Express.js API deployed on AWS Lambda (serverless)
2. SQLite database (zero infrastructure overhead)
3. REST API following standard patterns
4. Single monolithic codebase initially
5. Deploy on free tier or minimal cost ($0-30/month)

**Trade-offs**:
- Performance: Good (adequate for MVP)
- Development Speed: Excellent (fastest time-to-market)
- Operational Complexity: Minimal (serverless handles scaling)
- Cost Efficiency: Excellent ($0-30/month)

**Scaling Path**: When you hit MVP success:
- Migrate to PostgreSQL for better scalability
- Consider containerized deployment for better control
- Eventually split into microservices by domain

---

### Example 3: Real-Time Analytics Platform

**Scenario**: Building a live dashboard system processing streaming IoT sensor data with real-time ML-driven anomaly detection, requiring responsive updates (<500ms) and complex data analysis.

**Input**:
```typescript
const requirements = {
  volume: 'high',             // 100k+ events/second
  latency: 'responsive',      // <500ms dashboard updates
  costSensitivity: 'low',     // Enterprise customer
  reliability: 'critical',    // 99.9% uptime SLA
  dataComplexity: 'extreme',  // Streaming, ML pipelines, analytics
  timeToMarket: 'normal'      // 4-6 weeks available
};
```

**Output Recommendation**:
```typescript
{
  language: 'go',
  protocol: 'websocket',
  database: 'PostgreSQL + TimescaleDB',
  pattern: 'event_driven',
  messaging: 'kafka',
  reasoning: "Go excels at handling concurrent connections with goroutines..."
}
```

**Implementation Path**:
1. Kafka cluster for ingesting sensor data (ordered, durable)
2. Go services consuming Kafka and processing events
3. TimescaleDB (PostgreSQL extension) for time-series storage
4. WebSocket connections for live dashboard updates
5. Optional Flink/Spark for complex stream processing and ML

**Technology Stack**:
```
IoT Devices → Kafka Cluster
                    ↓
              Go Stream Processors
                    ↓
         TimescaleDB (time-series DB)
                    ↓
          Go API Server (WebSocket)
                    ↓
          Frontend (real-time dashboard)
```

**Trade-offs**:
- Performance: Excellent (optimized for concurrent connections)
- Development Speed: Medium (event-driven complexity)
- Operational Complexity: Medium-High (Kafka, real-time pipeline)
- Cost Efficiency: Good-Medium (typically $1k-5k/month)

---

### Example 4: Mission-Critical Financial System

**Scenario**: Building a payments processing backend that handles critical financial transactions with zero data loss, automatic geographic failover, multi-region deployment, and extreme reliability requirements.

**Input**:
```typescript
const requirements = {
  volume: 'high',             // 50k+ transactions/second
  latency: 'responsive',      // <500ms for user feedback
  costSensitivity: 'low',     // Cost secondary to reliability
  reliability: 'highly_critical', // 99.99% uptime (< 4 minutes downtime/year)
  dataComplexity: 'complex',  // Account state, transaction ledgers, audit logs
  timeToMarket: 'normal'      // Enterprise timelines
};
```

**Output Recommendation**:
```typescript
{
  language: 'go',
  protocol: 'grpc',
  database: 'PostgreSQL + replicas',
  pattern: 'distributed',
  messaging: 'kafka',
  reasoning: "Distributed pattern enables fault isolation and graceful degradation..."
}
```

**Implementation Path**:
1. Multi-region deployment (US-East, US-West, EU)
2. PostgreSQL with synchronous replication + hot standby
3. Kafka for durable, replicated event processing
4. gRPC for service communication with circuit breakers
5. Comprehensive monitoring and alerting (Datadog, PagerDuty)

**Infrastructure**:
```
Primary Region (US-East)      Replica Regions (US-West, EU)
   ├─ Transaction Service           ├─ Replicated DB
   ├─ Account Service               ├─ Read-only Replicas
   ├─ Audit Service                 ├─ Failover Ready
   └─ PostgreSQL (Primary)          └─ Auto-failover
        ↓
    Kafka Brokers (3+ regions)
        ↓
   Health Checks & Alerts
```

**Trade-offs**:
- Performance: Excellent (optimized for high throughput)
- Development Speed: Medium (distributed complexity)
- Operational Complexity: Very High (multi-region, replication, monitoring)
- Cost Efficiency: Medium (requires redundant infrastructure, $5k+/month)

---

## Quick Start

### Installation

```bash
npm install dev_backend
```

### Basic Usage

```typescript
import { beforeExecution } from 'dev_backend/hooks/before_execution';

// Provide requirements in natural language
const result = await beforeExecution({
  conversation: 'We need to handle 1M requests/second with <100ms latency'
});

console.log(result.recommendation.language);        // 'go'
console.log(result.recommendation.pattern);         // 'microservices'
console.log(result.analysis);                       // Detailed markdown analysis
console.log(result.nextSteps);                      // Implementation roadmap
```

### Using Structured Config

```typescript
const result = await beforeExecution({
  config: {
    volume: 'extreme',
    latency: 'realtime',
    costSensitivity: 'low',
    reliability: 'highly_critical',
    dataComplexity: 'complex',
    timeToMarket: 'normal'
  }
});
```

### Multi-Source Input

```typescript
const result = await beforeExecution({
  conversation: 'High-performance backend needed',
  config: { costSensitivity: 'low' },
  systemPrompt: 'Critical reliability 99.99% uptime required'
});
```

## Architecture Patterns

### 1. High Performance (Extreme Scale)
- **For**: 1M+ req/s, <100ms latency
- **Recommended**: Go, gRPC, PostgreSQL + Redis, Microservices, Kafka
- **Cost**: Medium-High
- **Complexity**: High

### 2. Low Cost (Bootstrap)
- **For**: Startup budget, rapid launch
- **Recommended**: TypeScript, REST, SQLite, Serverless, None
- **Cost**: Low ($30-100/month)
- **Complexity**: Low

### 3. High Reliability (Mission-Critical)
- **For**: 99.99% uptime, financial/healthcare
- **Recommended**: Go, gRPC, PostgreSQL + replicas, Distributed, Kafka
- **Cost**: High
- **Complexity**: Very High

### 4. MVP/Quick Launch
- **For**: 2-4 week launch, validation
- **Recommended**: TypeScript, REST, SQLite, Monolith, None
- **Cost**: Low-Medium
- **Complexity**: Low

### 5. Standard Web Application
- **For**: Typical SaaS, moderate scale
- **Recommended**: TypeScript, REST, PostgreSQL, Monolith, None
- **Cost**: Low-Medium
- **Complexity**: Low-Medium

### 6. Real-Time Data Processing
- **For**: Streaming data, analytics, real-time updates
- **Recommended**: Go, WebSocket, PostgreSQL + TimescaleDB, Event-Driven, Kafka
- **Cost**: Medium-High
- **Complexity**: Medium-High

## Design Principles

### SOLID Principles Applied

- **Single Responsibility**: Each pattern has one clear purpose
- **Open/Closed**: Easy to add new patterns without modifying existing ones
- **Liskov Substitution**: All patterns conform to Architecture interface
- **Interface Segregation**: Requirements interface is minimal and focused
- **Dependency Inversion**: Depends on abstractions (Requirements, Recommendation)

### KISS (Keep It Simple, Stupid)

- Clear, straightforward logic in pattern matching
- Minimal complexity in requirement parsing
- No over-engineered decision trees

### DRY (Don't Repeat Yourself)

- Shared recommendation schema
- Reusable pattern templates
- Common utility functions for parsing and validation

## Testing

Run the comprehensive test suite (>80% coverage):

```bash
npm test

# Unit tests
npm test -- tests/unit/decisions.test.ts
npm test -- tests/unit/recommendations.test.ts
npm test -- tests/unit/parser.test.ts

# Integration tests
npm test -- tests/integration/before_execution.test.ts
```

## Project Structure

```
src/
├── decisions/
│   ├── architecture_matrix.ts    # Core pattern definitions
│   ├── patterns.ts               # Architectural pattern guide
│   └── recommendations.ts        # Recommendation generation
├── hooks/
│   └── before_execution.ts       # Main execution hook
├── schemas/
│   ├── requirements.ts           # Requirements validation
│   ├── recommendations.ts        # Recommendation schema
│   └── task_scope.ts             # Task scope definition
└── utils/
    ├── logger.ts                 # Structured logging
    └── requirement-parser.ts     # Natural language parsing

tests/
├── unit/
│   ├── decisions.test.ts
│   ├── recommendations.test.ts
│   └── parser.test.ts
└── integration/
    └── before_execution.test.ts

docs/
├── README.md                     # This file
├── ARCHITECTURE.md               # System design
└── PRINCIPLES.md                 # Design philosophy
```

## Contributing

When adding a new architecture pattern:

1. Add to `ARCHITECTURE_PATTERNS` in `architecture_matrix.ts`
2. Define matching requirements
3. Add trade-off analysis
4. Include 2+ alternative approaches
5. Add unit tests in `decisions.test.ts`
6. Document in `ARCHITECTURE.md`

## References

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Architectural Patterns](https://microservices.io/patterns/index.html)
- [System Design Interview](https://www.educative.io/courses/grokking-system-design-interview)

## License

Part of the OpenClaw/NemoClaw framework
