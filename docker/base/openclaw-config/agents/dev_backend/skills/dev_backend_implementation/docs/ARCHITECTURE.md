# Architecture

## Design Decisions

### Intelligent Hooks

**before_execution**: Analyzes requirements and recommends tech stack
- Parses conversation context
- Reads project configuration
- Falls back to system prompt
- Returns architectural recommendation

**after_execution**: Logs metrics and generates reports
- Records execution duration
- Logs test results and coverage
- Generates evidence report
- Documents trade-offs

### Architecture Matrix

Maps requirements to tech stack:
- Volume (low, medium, high, extreme)
- Latency (relaxed, normal, responsive, realtime, ultra)
- Cost sensitivity (unlimited, low, medium, high)
- Reliability (best_effort, acceptable, critical, highly_critical)

## Structure

```
src/
├── hooks/              # Pre/post execution logic
├── decisions/          # Architecture matrix and recommendations
├── utils/              # Executors, validators, reporters
└── schemas/            # Data validation schemas
```

## Patterns

- Monolith for small teams and simple domains
- Microservices for scale and team independence
- Serverless for cost-sensitive, variable load
- Event-driven for asynchronous processing
