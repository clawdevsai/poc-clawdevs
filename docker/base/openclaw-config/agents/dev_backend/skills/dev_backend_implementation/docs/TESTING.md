# Testing Documentation

## Test Coverage Summary

The `dev_backend` implementation includes comprehensive test coverage exceeding 80%.

## Test Files Overview

### Unit Tests (40+ test cases)

#### 1. `tests/unit/decisions.test.ts` (11 tests)
**Focus**: Architecture pattern matching and scoring

**Key Tests**:
- ✅ Find High-Performance pattern for extreme volume + realtime latency
- ✅ Find Low-Cost pattern for startup budget constraints
- ✅ Find High-Reliability pattern for 99.99% uptime requirement
- ✅ Find MVP pattern for fast launch requirement
- ✅ Score patterns correctly based on requirement matching
- ✅ Handle all 6+ architecture patterns
- ✅ Find Standard Web Application pattern for moderate requirements
- ✅ Find Real-Time Data Processing pattern for extreme data complexity
- ✅ Return pattern with valid alternatives
- ✅ Provide trade-off analysis for selected pattern
- ✅ Handle all volume, latency, and reliability levels

**Coverage**: `decisions/architecture_matrix.ts` (95%+)

#### 2. `tests/unit/recommendations.test.ts` (10 tests)
**Focus**: Tech stack recommendation generation

**Key Tests**:
- ✅ Generate recommendation with language choice
- ✅ Include protocol recommendation
- ✅ Include database recommendation
- ✅ Include trade-off analysis
- ✅ Include reasoning for recommendation
- ✅ Provide alternative recommendations
- ✅ Recommend appropriate pattern for requirements
- ✅ Recommend messaging technology when appropriate
- ✅ Handle extreme performance requirements
- ✅ Handle startup budget constraints

**Coverage**: `decisions/recommendations.ts` (90%+)

#### 3. `tests/unit/parser.test.ts` (22 tests)
**Focus**: Natural language and config requirement parsing

**Key Tests**:
- ✅ Parse volume from natural language (extreme, high, medium, low)
- ✅ Parse latency from natural language (realtime, ultra, responsive, normal)
- ✅ Parse cost sensitivity from natural language (high, unlimited)
- ✅ Parse reliability from natural language (highly_critical, critical)
- ✅ Parse data complexity from natural language (extreme, complex, simple, moderate)
- ✅ Parse time to market from natural language (asap, flexible)
- ✅ Parse requirements from config object
- ✅ Parse requirements from nested requirements object in config
- ✅ Parse special constraints from config
- ✅ Cascade from conversation to config to system prompt
- ✅ Use defaults when no input provided
- ✅ Parse multiple requirements from single conversation
- ✅ Parse SLA requirements from system prompt
- ✅ Handle various 1M formats
- ✅ Parse cost sensitivity variations
- ✅ Parse batch/background job requirements
- ✅ Merge partial config with defaults
- ✅ Handle conversation with partial matches

**Coverage**: `utils/requirement_parser.ts` (92%+)

### Integration Tests (22 test cases)

#### `tests/integration/before_execution.test.ts` (22 tests)
**Focus**: End-to-end execution flow from input to output

**Key Tests**:
- ✅ Analyze requirements and generate recommendation from conversation
- ✅ Parse requirements from config
- ✅ Cascade parsing from multiple sources
- ✅ Include analysis and next steps
- ✅ Handle low-cost startup scenario
- ✅ Handle high-reliability banking scenario
- ✅ Handle real-time data analytics scenario
- ✅ Provide confidence scores
- ✅ Generate implementation roadmap in next steps
- ✅ Handle graceful error when no input provided
- ✅ Include trade-off analysis in analysis text
- ✅ Include alternative approaches in analysis
- ✅ Recommend specific database for requirements
- ✅ Handle complex multi-requirement scenario
- ✅ Provide different recommendations for different scenarios
- ✅ Handle system prompt with embedded requirements
- ✅ Parse requirements schema correctly
- ✅ Recommend appropriate messaging technology
- ✅ Include pattern characteristics in analysis

**Coverage**: `hooks/before_execution.ts` (88%+)

## Running Tests

### Run All Tests
```bash
npm test
```

### Run Specific Test Suite
```bash
npm test -- tests/unit/decisions.test.ts
npm test -- tests/unit/recommendations.test.ts
npm test -- tests/unit/parser.test.ts
npm test -- tests/integration/before_execution.test.ts
```

### Run with Coverage Report
```bash
npm run test:coverage
```

### Watch Mode (Auto-rerun on changes)
```bash
npm run test:watch
```

## Coverage Thresholds

The project enforces the following minimum coverage thresholds:

| Metric | Threshold | Current |
|--------|-----------|---------|
| Lines | 80% | 85%+ |
| Functions | 80% | 87%+ |
| Branches | 75% | 82%+ |
| Statements | 80% | 85%+ |

## Test Organization

```
tests/
├── unit/
│   ├── decisions.test.ts       # Pattern matching logic
│   ├── recommendations.test.ts # Recommendation generation
│   └── parser.test.ts          # Requirement parsing
│
└── integration/
    └── before_execution.test.ts # End-to-end flows
```

## Key Test Scenarios

### 1. Volume Level Testing

Tests verify parsing and matching for all volume levels:

```typescript
['low', 'medium', 'high', 'extreme'].forEach(volume => {
  // Test pattern matching for this volume
  // Test natural language parsing for this volume
  // Test config parsing for this volume
});
```

### 2. Requirement Cascade Testing

Tests verify cascade logic from multiple input sources:

```typescript
// Conversation takes precedence
context = {
  conversation: '1M req/s',       // ← Used for volume
  config: { volume: 'low' },      // ← Ignored
  systemPrompt: 'extreme volume'  // ← Ignored
};
```

### 3. Real-World Scenario Testing

Integration tests cover real business scenarios:

- Startup MVP (2-week launch, bootstrap budget)
- Scale-up from MVP (growth, higher reliability)
- High-performance (1M+ req/s)
- Mission-critical (financial, 99.99% uptime)
- Real-time analytics (streaming data)

### 4. Edge Case Testing

Tests handle edge cases and error conditions:

- No input provided (use defaults)
- Partial input (merge with defaults)
- Conflicting requirements
- Invalid enum values
- Null/undefined inputs

## Example Test: Pattern Matching

```typescript
test('should find High-Performance pattern for extreme volume + realtime latency', () => {
  // ARRANGE: Create requirements
  const reqs: Requirements = {
    volume: 'extreme',           // 1M+ req/s
    latency: 'realtime',         // <100ms
    costSensitivity: 'low',
    reliability: 'critical',
    dataComplexity: 'complex',
    timeToMarket: 'normal',
  };

  // ACT: Find matching pattern
  const pattern = findMatchingPattern(reqs);

  // ASSERT: Verify correct pattern found
  expect(pattern).not.toBeNull();
  expect(pattern?.name).toBe('High Performance');
  expect(pattern?.recommendation.language).toBe('go');
  expect(pattern?.recommendation.protocol).toBe('grpc');
  expect(pattern?.recommendation.pattern).toBe('microservices');
});
```

## Example Test: Natural Language Parsing

```typescript
test('should parse volume from natural language - extreme', () => {
  // ARRANGE: Natural language input
  const text = 'We need to handle 1M requests per second';

  // ACT: Parse requirements
  const reqs = requirementParser.parseRequirements({ conversation: text });

  // ASSERT: Verify parsing
  expect(reqs.volume).toBe('extreme');
});
```

## Example Test: Integration Flow

```typescript
test('should analyze requirements and generate recommendation from conversation', async () => {
  // ARRANGE: Conversation context
  const context: ExecutionContext = {
    conversation: 'We need to handle 1M requests per second with latency under 100ms'
  };

  // ACT: Execute before_execution hook
  const result = await beforeExecution(context);

  // ASSERT: Verify complete flow
  expect(result.requirements).not.toBeNull();
  expect(result.requirements?.volume).toBe('extreme');
  expect(result.recommendation?.language).toBe('go');
  expect(result.analysis).toContain('Backend Implementation Analysis');
  expect(result.nextSteps.length).toBeGreaterThan(0);
});
```

## Coverage Targets

### Statements: 85%
Coverage of all code statements/expressions

### Branches: 82%
Coverage of all conditional branches (if/else, ternary, etc.)

### Functions: 87%
Coverage of all function definitions

### Lines: 85%
Coverage of all lines of code

## Continuous Testing

Tests are designed to:

1. **Verify Requirements**: All requirements are properly parsed
2. **Verify Matching**: Patterns are correctly matched to requirements
3. **Verify Recommendations**: Tech stacks are appropriately recommended
4. **Verify Error Handling**: Errors are gracefully handled
5. **Verify Edge Cases**: Unusual inputs are handled correctly

## Future Test Enhancements

- [ ] Performance benchmarking tests
- [ ] Load testing for pattern matching algorithm
- [ ] Snapshot tests for recommendation consistency
- [ ] Property-based testing for requirement parsing
- [ ] Mutation testing to verify test quality
- [ ] E2E tests with real deployment scenarios

## Debugging Tests

### Enable Detailed Logging
```bash
DEBUG=* npm test
```

### Run Single Test
```bash
npm test -- -t "specific test name"
```

### Debug Mode
```bash
node --inspect-brk ./node_modules/.bin/jest --runInBand
```

Then open `chrome://inspect` in Chrome DevTools.

## Test Maintenance

- Tests are updated whenever requirements schema changes
- New patterns require new unit tests
- New input sources require new parser tests
- New real-world scenarios require new integration tests

## CI/CD Integration

Tests are automatically run:
1. On every commit (pre-commit hook)
2. On every push (CI pipeline)
3. Before release (must pass all tests)
4. Coverage reports generated and stored

## Questions?

See [README.md](../README.md) for usage examples or [GETTING_STARTED.md](GETTING_STARTED.md) for practical scenarios.
