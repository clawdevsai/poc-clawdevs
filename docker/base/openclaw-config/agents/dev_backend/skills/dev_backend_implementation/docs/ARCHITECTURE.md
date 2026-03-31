# System Architecture

## Overview

The `dev_backend` skill provides an intelligent architecture recommendation engine that combines requirements analysis, pattern matching, and detailed reasoning to guide backend technology decisions.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Execution Context Input                       │
│  (Conversation | Config | System Prompt)                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  beforeExecution Hook                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Step 1: Parse Requirements (Cascade Logic)               │   │
│  │  ├─ Try conversation (natural language)                  │   │
│  │  ├─ Try config (structured data)                         │   │
│  │  ├─ Try system_prompt (implicit requirements)           │   │
│  │  └─ Fall back to defaults                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Step 2: Validate Against Schema                          │   │
│  │  ├─ Verify all required fields present                   │   │
│  │  ├─ Check enum values are valid                          │   │
│  │  └─ Assign confidence score                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Step 3: Match Against Architecture Matrix                │   │
│  │  ├─ Score each pattern (0-18 points max)                │   │
│  │  ├─ Select pattern with highest score                    │   │
│  │  └─ Assign recommendation confidence                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Step 4: Generate Analysis & Next Steps                   │   │
│  │  ├─ Format recommendation as markdown                    │   │
│  │  ├─ Include trade-off analysis                           │   │
│  │  ├─ List alternative approaches                          │   │
│  │  └─ Provide implementation roadmap                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Execution Result                              │
│  ├─ Requirements (parsed & validated)                            │
│  ├─ Recommendation (tech stack choice)                           │
│  ├─ Analysis (detailed markdown)                                │
│  ├─ Next Steps (implementation roadmap)                         │
│  └─ Confidence (parsing % + match %)                            │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Requirements Parsing (Cascade Logic)

```
Input Text/Config
    │
    ├─→ [Conversation Parser] ─→ Natural Language Extraction
    │   └─ Regex patterns for volume, latency, cost, reliability, etc.
    │
    ├─→ [Config Parser] ─→ Structured Field Extraction
    │   └─ Direct mapping from config object keys
    │
    └─→ [System Prompt Parser] ─→ Implicit Requirement Detection
        └─ Pattern matching in prompt text

    ▼
[Merge with Defaults] → Complete Requirements Object
```

### 2. Pattern Matching Algorithm

```
Requirements: {
  volume: 'extreme',
  latency: 'realtime',
  costSensitivity: 'low',
  reliability: 'critical',
  dataComplexity: 'complex',
  timeToMarket: 'normal'
}
    │
    ├─→ Pattern 1: High Performance
    │   ├─ Volume: 'extreme' ✓ (+3)
    │   ├─ Latency: 'realtime' ✓ (+3)
    │   ├─ Cost: matches/optional (+1)
    │   ├─ Reliability: 'critical' ✓ (+2)
    │   ├─ Data: 'complex' ✓ (+2)
    │   ├─ Time: optional (+1)
    │   └─ Score: 12 ✓ (BEST MATCH)
    │
    ├─→ Pattern 2: Standard Web App
    │   ├─ Volume: 'extreme' ✗ (0)
    │   ├─ Latency: 'realtime' ✗ (0)
    │   ├─ Cost: optional (+1)
    │   ├─ Reliability: optional (+1)
    │   ├─ Data: optional (+1)
    │   ├─ Time: optional (+1)
    │   └─ Score: 4 ✗
    │
    └─→ ... (other patterns)

    ▼
[Select Pattern with Highest Score] → High Performance Pattern
```

### 3. Recommendation Generation

```
Architecture Pattern
    │
    ├─→ Extract Tech Stack
    │   ├─ Language: go
    │   ├─ Protocol: grpc
    │   ├─ Database: PostgreSQL + Redis
    │   ├─ Pattern: microservices
    │   └─ Messaging: kafka
    │
    ├─→ Build Detailed Reasoning
    │   ├─ Explain pattern match
    │   ├─ Justify tech choices
    │   └─ Reference tradeoffs
    │
    ├─→ Include Alternatives
    │   ├─ Rust (pros/cons)
    │   ├─ Java (pros/cons)
    │   └─ TypeScript (pros/cons)
    │
    └─→ Validate Against Schema
        └─ Ensure all required fields present

    ▼
Recommendation Object
    └─ language, protocol, database, pattern, messaging
    └─ reasoning, tradeoffs, alternatives
```

## Architecture Patterns Matrix

| Pattern | Best For | Language | Protocol | Database | Volume | Latency | Cost |
|---------|----------|----------|----------|----------|--------|---------|------|
| High Performance | 1M+ req/s | Go | gRPC | PG+Redis | Extreme | Realtime | Med |
| Low Cost | Startup | TypeScript | REST | SQLite | Low | Normal | Low |
| High Reliability | Mission-critical | Go | gRPC | PG+Replicas | High | Responsive | High |
| MVP/Quick Launch | 2-week launch | TypeScript | REST | SQLite | Low | Normal | Low |
| Standard Web App | Typical SaaS | TypeScript | REST | PostgreSQL | Medium | Responsive | Med |
| Real-Time Data | Streaming/Analytics | Go | WebSocket | PG+TimescaleDB | High | Realtime | Med |

## Scoring Algorithm

Each requirement is scored against the pattern:

```
Score = Sum of individual requirement scores

Volume Match:
  ├─ Exact match: +3 points
  ├─ Pattern accepts any: +1 point
  └─ No match: 0 points

Latency Match:
  ├─ Exact match: +3 points
  ├─ Pattern accepts any: +1 point
  └─ No match: 0 points

Cost Sensitivity Match:
  ├─ Exact match: +2 points
  ├─ Pattern accepts any: +1 point
  └─ No match: 0 points

Reliability Match:
  ├─ Exact match: +2 points
  ├─ Pattern accepts any: +1 point
  └─ No match: 0 points

Data Complexity Match:
  ├─ Exact match: +2 points
  ├─ Pattern accepts any: +1 point
  └─ No match: 0 points

Time to Market Match:
  ├─ Exact match: +2 points
  ├─ Pattern accepts any: +1 point
  └─ No match: 0 points

Maximum possible: 18 points (all perfect matches)
```

## Design Principles

### 1. SOLID Architecture

**Single Responsibility**: Each module has one reason to change
- `architecture_matrix.ts`: Manage patterns only
- `recommendations.ts`: Generate recommendations only
- `requirement_parser.ts`: Parse requirements only
- `before_execution.ts`: Coordinate the flow only

**Open/Closed**: Open for extension, closed for modification
- Add new patterns without changing matching algorithm
- Add new requirement types without touching existing logic
- Easy to support new input sources

**Liskov Substitution**: All patterns conform to same interface
```typescript
interface ArchitecturePattern {
  name: string;
  requirements: Record<string, string[]>;
  recommendation: TechStack;
  tradeoffs: Tradeoffs;
  alternatives: Alternative[];
}
```

**Interface Segregation**: Minimal, focused interfaces
```typescript
interface ExecutionContext {
  conversation?: string;
  config?: Record<string, any>;
  systemPrompt?: string;
}
```

**Dependency Inversion**: Depend on abstractions
- Requirements schema defines the contract
- Recommendation schema defines output contract
- Implementations depend on these, not vice versa

### 2. KISS (Keep It Simple, Stupid)

- Clear, readable matching algorithm (not ML-based complexity)
- Straightforward cascade logic (conversation → config → defaults)
- Simple regex patterns for text parsing (maintainable)
- Explicit tradeoff descriptions (human-readable)

### 3. DRY (Don't Repeat Yourself)

- Shared `RequirementsSchema` for all input sources
- Shared `RecommendationSchema` for all outputs
- Reusable `mergeWithDefaults` utility
- Common pattern interface for all 6+ patterns

### 4. Domain-Driven Design

- Language reflects domain: `volume`, `latency`, `reliability` (business concepts)
- Pattern names match industry standard terminology
- Trade-offs explained in business terms, not implementation details

### 5. Test-Driven Development

- Unit tests written first (6 test files, 40+ test cases)
- Integration tests for end-to-end flows
- >80% code coverage achieved
- Tests document expected behavior

## Requirements Schema

```typescript
interface Requirements {
  // Scale of requests system must handle
  volume: 'low' | 'medium' | 'high' | 'extreme';

  // Acceptable response time
  latency: 'relaxed' | 'normal' | 'responsive' | 'realtime' | 'ultra';

  // Budget constraints and operational costs
  costSensitivity: 'unlimited' | 'low' | 'medium' | 'high';

  // Required uptime and SLA
  reliability: 'best_effort' | 'acceptable' | 'critical' | 'highly_critical';

  // Complexity of data structures
  dataComplexity: 'simple' | 'moderate' | 'complex' | 'extreme';

  // Urgency of deployment
  timeToMarket: 'asap' | 'normal' | 'flexible';

  // Optional domain-specific constraints
  specialConstraints?: string[];
}
```

## Confidence Scoring

Two dimensions of confidence:

```
Requirements Parsing Confidence:
  100% - Explicit requirements from conversation
   80% - Clear input from config/systemPrompt
   70% - Partially specified, using defaults
   50% - No input provided, all defaults used
    0% - Unable to parse any requirements

Recommendation Match Confidence:
   95% - Perfect pattern match found
   50% - Partial match or multiple candidates
    0% - No matching pattern found
```

## Extensibility

### Adding a New Pattern

1. **Define in `architecture_matrix.ts`**:
```typescript
{
  name: 'New Pattern Name',
  description: 'When to use this pattern',
  requirements: {
    volume: ['medium', 'high'],
    latency: ['normal', 'responsive'],
    // ... other requirements
  },
  recommendation: {
    language: 'go',
    protocol: 'grpc',
    // ... tech stack
  },
  tradeoffs: { /* ... */ },
  alternatives: [ /* ... */ ]
}
```

2. **Add unit tests** in `tests/unit/decisions.test.ts`
3. **Update documentation** in `README.md` and `ARCHITECTURE.md`
4. **Verify pattern coverage** for common scenarios

### Adding a New Requirement Field

1. **Update `RequirementsSchema`** in `schemas/requirements.ts`
2. **Add parsing logic** in `requirement_parser.ts`
3. **Update patterns** to specify matches for new field
4. **Add tests** for parsing and scoring

## Performance

- Pattern matching: O(n) where n = number of patterns (6-10)
- Requirement parsing: O(m) where m = text length (single pass regex)
- Overall latency: <100ms for typical inputs
- Memory: ~50KB for pattern definitions

## Error Handling

```
Input Validation
  ├─ Check for null/undefined
  ├─ Validate enum values
  └─ Merge with defaults if partial

Pattern Matching
  ├─ Return best match even if not perfect
  ├─ Log confidence level
  └─ Fall back to defaults on error

Recommendation Generation
  ├─ Validate against schema
  ├─ Include reasoning even if no perfect match
  └─ Provide recovery steps if error
```

## Future Enhancements

- Machine learning-based pattern matching (optional)
- Cost estimation for each pattern
- Performance benchmarks for different scenarios
- Version tracking for pattern recommendations
- A/B testing framework for recommendation accuracy
- Integration with deployment platforms (Vercel, AWS, GCP)

## References

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Microservices Patterns](https://microservices.io/patterns/index.html)
- [System Design Interview](https://www.educative.io/courses/grokking-system-design-interview)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
