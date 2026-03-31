# Design Principles

This document explains the design philosophy and principles applied to the `dev_backend` implementation.

## SOLID Principles

### 1. Single Responsibility Principle (SRP)

Each class/module should have only one reason to change.

**Applied to dev_backend**:

- `architecture_matrix.ts`: Responsible ONLY for defining patterns and matching
  - Changes when: new patterns discovered, matching algorithm refined
  - NOT responsible for: parsing, validation, output formatting

- `recommendations.ts`: Responsible ONLY for generating recommendations
  - Changes when: recommendation logic changes
  - NOT responsible for: pattern definition, requirement parsing

- `requirement_parser.ts`: Responsible ONLY for extracting requirements
  - Changes when: new requirement types or parsing strategies discovered
  - NOT responsible for: pattern matching, validation

- `before_execution.ts`: Responsible ONLY for orchestration
  - Changes when: integration flow changes
  - NOT responsible for: algorithm implementations

**Real Example**:
```typescript
// GOOD: Single responsibility
class RequirementParser {
  parseRequirements(source: RequirementSource): Requirements { }
}

// BAD: Too many responsibilities
class BackendArchitect {
  parseRequirements() { }
  matchPatterns() { }
  generateAnalysis() { }
  saveToDatabase() { }
}
```

### 2. Open/Closed Principle (OCP)

Software entities should be open for extension but closed for modification.

**Applied to dev_backend**:

Adding a new architecture pattern should NOT require modifying existing code.

```typescript
// GOOD: Add new pattern without modifying existing logic
ARCHITECTURE_PATTERNS.push({
  name: 'ML Training Pipeline',
  requirements: { /* ... */ },
  recommendation: { /* ... */ },
  tradeoffs: { /* ... */ }
});

// BAD: Would require modifying findMatchingPattern() function
function findMatchingPattern(requirements) {
  if (requiresMLTraining) {
    // Special case code here - CHANGE TO EXISTING CODE
  }
}
```

**Benefits**:
- Easy to add 7th, 8th pattern without regression risk
- Matching algorithm stays stable
- New contributors can add patterns independently

### 3. Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types.

**Applied to dev_backend**:

All patterns follow the same `ArchitecturePattern` interface:

```typescript
interface ArchitecturePattern {
  name: string;
  requirements: Requirements;
  recommendation: Recommendation;
  tradeoffs: Tradeoffs;
  alternatives: Alternative[];
}
```

Any pattern can be used interchangeably:

```typescript
// Works with any pattern without knowing specific type
function analyzePattern(pattern: ArchitecturePattern): void {
  console.log(pattern.name);
  console.log(pattern.recommendation.language);
  console.log(pattern.tradeoffs.performance);
}

// Can call with ANY pattern
analyzePattern(ARCHITECTURE_PATTERNS[0]); // Works
analyzePattern(ARCHITECTURE_PATTERNS[3]); // Works
```

### 4. Interface Segregation Principle (ISP)

Clients should not be forced to depend on interfaces they don't use.

**Applied to dev_backend**:

Requirements interface is minimal and focused:

```typescript
// GOOD: Clients only see what they need
interface ExecutionContext {
  conversation?: string;
  config?: Record<string, any>;
  systemPrompt?: string;
}

interface ExecutionResult {
  requirements: Requirements | null;
  recommendation: Recommendation | null;
  analysis: string;
  nextSteps: string[];
  confidence: { requirementsParsing: number; recommendationMatch: number };
}

// BAD: Too many options, confusing interface
interface ExecutionContext {
  conversation?: string;
  config?: Record<string, any>;
  systemPrompt?: string;
  userId?: string;          // Not needed
  projectId?: string;       // Not needed
  deploymentTarget?: string; // Not needed
  version?: string;         // Not needed
  // ... 10 more fields
}
```

### 5. Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions.

**Applied to dev_backend**:

```typescript
// GOOD: Depends on Requirements abstraction
function getRecommendation(requirements: Requirements): Recommendation {
  // Works with ANY Requirements object
  const pattern = findMatchingPattern(requirements);
  // ...
}

// BAD: Depends on concrete input type
function getRecommendation(req: HttpRequest): Recommendation {
  const volume = req.query.volume;
  const latency = req.query.latency;
  // Tightly coupled to HTTP
}
```

## KISS Principle (Keep It Simple, Stupid)

Prefer simple solutions over complex ones.

**Applied to dev_backend**:

### Requirement Parsing: Simple Regex Over ML

```typescript
// GOOD: Simple, understandable regex patterns
if (/1[.,]?0*\s*[mM]\s*(?:requests|rps)/.test(text)) {
  requirements.volume = 'extreme';
}

// BAD: Complex ML model for simple pattern
const model = require('tensorflow').model;
const prediction = await model.predict(text);
// Harder to understand, maintain, debug
```

### Pattern Matching: Linear Scoring Over Complex Algorithm

```typescript
// GOOD: Simple point system
let score = 0;
if (pattern.requirements.volume?.includes(req.volume)) score += 3;
if (pattern.requirements.latency?.includes(req.latency)) score += 3;
// ... continue scoring
return bestMatch; // Highest score wins

// BAD: Complex decision tree
if (requirements.volume === 'extreme') {
  if (requirements.latency === 'realtime') {
    if (requirements.costSensitivity === 'low') {
      if (/* ... 10 more conditions ... */) {
        return pattern;
      }
    }
  }
}
```

### Error Handling: Graceful Fallback Over Strict Validation

```typescript
// GOOD: Continue with defaults if partial input
const requirements = this.mergeWithDefaults(partial);
// Returns valid Requirements even if some fields missing

// BAD: Strict validation
if (!input.volume || !input.latency || !input.costSensitivity) {
  throw new ValidationError('Missing required fields');
}
```

## DRY Principle (Don't Repeat Yourself)

Avoid duplication of logic, data, and code.

**Applied to dev_backend**:

### Shared Schemas

```typescript
// GOOD: Single schema definition reused everywhere
export const RequirementsSchema = z.object({
  volume: VolumeRequirement,
  latency: LatencyRequirement,
  // ...
});

// Used in validation
const validated = RequirementsSchema.parse(input);

// Used in testing
const testReq: Requirements = { /* ... */ };

// BAD: Schema defined in multiple places
// requirements.ts
function validateRequirements(req) { /* check volume, latency */ }
// parser.ts
function parseRequirements(req) { /* check volume, latency */ }
// recommendations.ts
function getRecommendation(req) { /* check volume, latency */ }
// Result: Changes needed in 3 places
```

### Shared Utility Functions

```typescript
// GOOD: Reusable merge logic
private mergeWithDefaults(partial: Partial<Requirements>): Requirements {
  return {
    volume: partial.volume || defaults.volume,
    latency: partial.latency || defaults.latency,
    // ...
  };
}

// Used in all parsers
const fromConv = this.mergeWithDefaults(conversationReqs);
const fromConfig = this.mergeWithDefaults(configReqs);
const fromPrompt = this.mergeWithDefaults(promptReqs);

// BAD: Duplicated merge logic
// In parseFromConversation
const full = {
  volume: partial.volume || 'medium',
  latency: partial.latency || 'normal',
  // ...
};
// In parseFromConfig - DUPLICATED
const full = {
  volume: partial.volume || 'medium',
  latency: partial.latency || 'normal',
  // ...
};
```

## Domain-Driven Design (DDD)

Use language and structure that reflect the business domain.

**Applied to dev_backend**:

### Ubiquitous Language

Terms match the business domain (backend architecture):

```typescript
// GOOD: Business terminology
interface Requirements {
  volume: 'low' | 'medium' | 'high' | 'extreme';
  latency: 'relaxed' | 'normal' | 'responsive' | 'realtime';
  reliability: 'acceptable' | 'critical' | 'highly_critical';
}

// BAD: Technical jargon
interface SystemMetrics {
  throughput: number;
  responsetime: number;
  availability: number;
}
```

### Bounded Contexts

Clear separation of domains:

- **Requirements Domain**: Parsing and validation of requirements
- **Architecture Domain**: Patterns and their characteristics
- **Recommendation Domain**: Matching requirements to patterns
- **Execution Domain**: Orchestrating the overall flow

### Value Objects

Immutable, type-safe representations:

```typescript
// GOOD: Type-safe enums
type VolumeRequirement = 'low' | 'medium' | 'high' | 'extreme';

// Safe to use
if (req.volume === 'extreme') { /* ... */ }

// BAD: String types prone to typos
if (req.volume === 'extrem') { /* Typo! No error */ }
```

## Test-Driven Development (TDD)

Tests drive design and implementation.

**Applied to dev_backend**:

### Example: Test Drives Cascade Logic

Test written first:
```typescript
test('should cascade from conversation to config to system prompt', () => {
  const context = {
    conversation: 'We need 1M requests per second',
    config: { latency: 'realtime' },
    systemPrompt: 'Highly critical reliability required'
  };
  const reqs = parseRequirements(context);

  expect(reqs.volume).toBe('extreme'); // From conversation
  expect(reqs.latency).toBe('realtime'); // From config
  expect(reqs.reliability).toBe('highly_critical'); // From system prompt
});
```

Implementation follows to pass test:
```typescript
parseRequirements(source) {
  // Try conversation first
  if (source.conversation) {
    const fromConv = this.parseFromConversation(source.conversation);
    if (fromConv) return fromConv; // ← Passes volume test
  }

  // Try config second
  if (source.config) {
    const partial = this.parseFromConfig(source.config);
    const merged = this.mergeWithDefaults(partial);
    return merged; // ← Passes latency + reliability test
  }

  // Fallback
  return this.getDefaults();
}
```

### Benefits

- Code written is code needed (no unused code)
- Design discovered through testing
- Refactoring safe (tests catch regressions)
- Documentation (tests show how to use)

## Clean Code

### Naming

```typescript
// GOOD: Clear, intention-revealing names
function findMatchingPattern(requirements: Requirements): ArchitecturePattern | null {
  // Clear what it does
}

function buildDetailedReasoning(pattern: ArchitecturePattern): string {
  // Clear purpose
}

// BAD: Cryptic, vague names
function match(req) { }
function build(p) { }
```

### Functions

```typescript
// GOOD: Small, focused functions
function getRecommendation(requirements: Requirements): Recommendation | null {
  const pattern = findMatchingPattern(requirements);
  if (!pattern) return null;
  return createRecommendation(pattern);
}

// BAD: Large, doing too much
function processRequirements(req) {
  // 200 lines of mixed parsing, matching, formatting, etc.
}
```

### Comments

```typescript
// GOOD: Comment WHY, not WHAT
// Volume is weighted 3 points because it's the primary scalability driver
if (pattern.requirements.volume?.includes(requirements.volume)) {
  score += 3;
}

// BAD: Comment restates code
// Check if volume matches
if (pattern.requirements.volume?.includes(requirements.volume)) {
  score += 3; // Add 3 points
}
```

## Summary

| Principle | How Applied | Benefit |
|-----------|-------------|---------|
| SRP | One responsibility per module | Easy to understand, test, modify |
| OCP | Add patterns without modifying core | Safe to extend functionality |
| LSP | All patterns use same interface | Polymorphic, flexible code |
| ISP | Minimal, focused interfaces | Clear contracts, no unnecessary coupling |
| DIP | Depend on abstractions | Flexible, testable, maintainable |
| KISS | Simple algorithms over complex | Easy to debug and understand |
| DRY | Shared schemas and utilities | Changes in one place only |
| DDD | Business language in code | Aligned with domain experts |
| TDD | Tests before implementation | Code driven by requirements |
| Clean Code | Clear naming, small functions | Easy to read and maintain |

These principles combine to create code that is:
- **Easy to understand**: Clear intent and structure
- **Easy to modify**: Low coupling, high cohesion
- **Easy to test**: Dependency injection, focused responsibilities
- **Easy to extend**: Open for extension, closed for modification
- **Easy to maintain**: DRY, no duplication, clear names
