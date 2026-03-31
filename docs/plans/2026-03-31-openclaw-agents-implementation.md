# OpenClaw Agents Full-Stack Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor all 16 OpenClaw agents to production-grade plugin structure with intelligent architectural decision hooks.

**Architecture:** Incremental refactoring per agent (1 → 16), each with full-stack structure (SKILL.md, manifest.json, src/, tests/, docs/, examples/). First agent (dev_backend) serves as golden template for remaining 15.

**Tech Stack:** TypeScript (hooks/schemas), Pseudocode (examples), Zod (validation), Jest (tests), Markdown (docs)

---

## Phase 1: Create Agent Refactoring Template & Tooling

### Task 1.1: Create Refactoring Template Directory Structure

**Files:**
- Create: `docker/base/openclaw-config/_refactoring-template/TEMPLATE.md`
- Create: `docker/base/openclaw-config/_refactoring-template/skill-structure.txt`
- Create: `docker/base/openclaw-config/_refactoring-template/checklist.md`

**Step 1: Create template directory**

```bash
mkdir -p "docker/base/openclaw-config/_refactoring-template"
```

**Step 2: Write TEMPLATE.md with reference structure**

```markdown
# Refactoring Template for [AGENT_NAME]

## Overview
Agent refactoring follows this structure:
- Analyze current skills
- Create full-stack structure
- Implement hook: before_execution
- Write documentation
- Create test suite
- Add practical examples
- Commit with evidence

## Checklist
- [ ] Analyzed current state
- [ ] Created directory structure
- [ ] Implemented SKILL.md
- [ ] Implemented manifest.json
- [ ] Implemented src/hooks/before_execution.ts
- [ ] Implemented src/decisions/architecture_matrix.ts
- [ ] Implemented src/utils/requirement_parser.ts
- [ ] Implemented src/schemas/requirements.ts
- [ ] Wrote tests (unit + integration)
- [ ] Wrote docs (README, ARCHITECTURE, PRINCIPLES, examples)
- [ ] Created 3+ practical examples
- [ ] All tests passing (>80% coverage)
- [ ] Validated against design principles
- [ ] Commit ready

## Key Files by Agent
Replace [AGENT_NAME] with actual agent name in all paths below.
```

**Step 3: Create skill-structure.txt**

```text
[AGENT_NAME]/
├── IDENTITY.md
└── skills/
    └── [SKILL_NAME]/
        ├── SKILL.md
        ├── manifest.json
        ├── src/
        │   ├── index.ts
        │   ├── hooks/
        │   │   ├── before_execution.ts
        │   │   └── after_execution.ts
        │   ├── decisions/
        │   │   ├── architecture_matrix.ts
        │   │   ├── recommendations.ts
        │   │   └── patterns.ts
        │   ├── utils/
        │   │   ├── requirement_parser.ts
        │   │   ├── validator.ts
        │   │   └── logger.ts
        │   └── schemas/
        │       ├── requirements.ts
        │       └── recommendations.ts
        ├── tests/
        │   ├── unit/
        │   │   ├── decisions.test.ts
        │   │   ├── recommendations.test.ts
        │   │   └── parser.test.ts
        │   └── integration/
        │       └── hooks.test.ts
        ├── docs/
        │   ├── README.md
        │   ├── GETTING_STARTED.md
        │   ├── ARCHITECTURE.md
        │   ├── PRINCIPLES.md
        │   ├── DECISIONS_MATRIX.md
        │   └── TROUBLESHOOTING.md
        └── examples/
            ├── example-high-performance.md
            ├── example-low-cost.md
            ├── example-high-reliability.md
            └── example-mvp.md
```

**Step 4: Create checklist.md**

```markdown
# Agent Refactoring Checklist

Use this for each agent being refactored.

## Pre-Refactoring
- [ ] Analyzed current skills in agent
- [ ] Identified all skill files
- [ ] Documented current structure
- [ ] Understood agent's domain/purpose

## Structure Creation
- [ ] Created full-stack directory structure
- [ ] Moved existing SKILL.md content
- [ ] Created manifest.json template
- [ ] Created src/, tests/, docs/, examples/ folders

## Hook Implementation
- [ ] Created src/hooks/before_execution.ts
- [ ] Implemented requirement parsing (conversa → config → system)
- [ ] Implemented cascade logic
- [ ] Added error handling for missing requirements

## Decisions Module
- [ ] Created architecture_matrix.ts with 5+ decision patterns
- [ ] Created recommendations.ts with recomendation logic
- [ ] Mapped requirements to tech stack
- [ ] Added trade-off analysis

## Schemas & Validation
- [ ] Created Zod schemas for Requirements
- [ ] Created Zod schemas for Recommendations
- [ ] Added validation in parser
- [ ] Added error messages

## Tests
- [ ] Unit tests: decisions matrix (>=5 tests)
- [ ] Unit tests: recommendations logic (>=5 tests)
- [ ] Unit tests: requirement parser (>=5 tests)
- [ ] Integration tests: hook end-to-end (>=3 tests)
- [ ] Coverage >=80%
- [ ] All tests passing

## Documentation
- [ ] README.md: Overview and quick start
- [ ] GETTING_STARTED.md: How to use the skill
- [ ] ARCHITECTURE.md: Design decisions explained
- [ ] PRINCIPLES.md: SOLID/KISS/etc applied
- [ ] DECISIONS_MATRIX.md: Full documentation of matrix
- [ ] TROUBLESHOOTING.md: Common issues

## Examples
- [ ] example-high-performance.md: 1M req/s, <100ms latency
- [ ] example-low-cost.md: Startup budget constraints
- [ ] example-high-reliability.md: 99.99% uptime requirement
- [ ] example-mvp.md: Quick launch, minimal investment

## Validation & Quality
- [ ] Validated against design doc
- [ ] Reviewed for SOLID principles
- [ ] Checked for KISS (not over-engineered)
- [ ] Verified YAGNI (no unnecessary features)
- [ ] DRY applied (no duplicate logic)
- [ ] TDD followed (tests written first)
- [ ] Clean code standards met

## Commit & Evidence
- [ ] Git status clean (all changes staged)
- [ ] Commit message follows conventional commits
- [ ] Commit includes evidence (test results, coverage report)
- [ ] Ready for next agent
```

**Step 5: Commit**

```bash
cd "C:\Users\Administrator\Workspace\lukeware\clawdevs-ai"
git add "docker/base/openclaw-config/_refactoring-template/"
git commit -m "docs: add refactoring template and checklist

Template provides:
- Structured approach for agent refactoring
- Standard directory structure
- Step-by-step checklist
- Quality gates

To be used for all 16 agent refactorings.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 1.2: Create Base Zod Schemas for Requirements & Recommendations

**Files:**
- Create: `docker/base/openclaw-config/shared/schemas/requirements.ts`
- Create: `docker/base/openclaw-config/shared/schemas/recommendations.ts`
- Create: `docker/base/openclaw-config/shared/schemas/index.ts`

**Step 1: Create requirements.ts**

```typescript
import { z } from 'zod';

// Volume/Scale Requirements
export const VolumeRequirement = z.enum([
  'low',      // <1k req/s
  'medium',   // 1k-100k req/s
  'high',     // 100k-1M req/s
  'extreme',  // >1M req/s
]);

// Latency Requirements
export const LatencyRequirement = z.enum([
  'relaxed',     // <5s
  'normal',      // <1s
  'responsive',  // <500ms
  'realtime',    // <100ms
  'ultra',       // <10ms
]);

// Cost Sensitivity
export const CostSensitivity = z.enum([
  'unlimited',  // VC-funded, cost not a concern
  'low',        // Cost matters but not critical
  'medium',     // Balance cost and performance
  'high',       // Startup budget, minimize cost
]);

// Reliability Requirements
export const ReliabilityRequirement = z.enum([
  'best_effort',      // 95%+
  'acceptable',       // 99%+
  'critical',         // 99.9%+
  'highly_critical',  // 99.99%+
]);

// Data Complexity
export const DataComplexity = z.enum([
  'simple',     // CRUD, flat structure
  'moderate',   // Relationships, some business logic
  'complex',    // Graph data, complex queries
  'extreme',    // ML pipelines, real-time processing
]);

// Time to Market
export const TimeToMarket = z.enum([
  'asap',     // Days/weeks
  'normal',   // Weeks/months
  'flexible', // Months, can iterate
]);

// Complete Requirements Object
export const RequirementsSchema = z.object({
  volume: VolumeRequirement,
  latency: LatencyRequirement,
  cost_sensitivity: CostSensitivity,
  reliability: ReliabilityRequirement,
  data_complexity: DataComplexity,
  time_to_market: TimeToMarket,
  special_constraints: z.array(z.string()).optional(),
});

export type Requirements = z.infer<typeof RequirementsSchema>;
```

**Step 2: Create recommendations.ts**

```typescript
import { z } from 'zod';

export const LanguageRecommendation = z.enum([
  'go',
  'rust',
  'typescript',
  'python',
  'java',
  'csharp',
]);

export const ProtocolRecommendation = z.enum([
  'grpc',
  'rest',
  'websocket',
  'graphql',
  'mqtt',
]);

export const DatabaseRecommendation = z.enum([
  'postgresql',
  'mysql',
  'mongodb',
  'dynamodb',
  'redis',
  'cassandra',
  'elasticsearch',
  'sqlite',
]);

export const PatternRecommendation = z.enum([
  'monolith',
  'microservices',
  'serverless',
  'event_driven',
  'batch',
  'streaming',
]);

export const MessagingRecommendation = z.enum([
  'kafka',
  'rabbitmq',
  'sqs',
  'pubsub',
  'none',
]);

export const Tradeoff = z.object({
  performance: z.string(),
  development_speed: z.string(),
  operational_complexity: z.string(),
  cost_efficiency: z.string(),
});

export const Alternative = z.object({
  language: LanguageRecommendation,
  pros: z.string(),
  cons: z.string(),
});

export const RecommendationSchema = z.object({
  language: LanguageRecommendation,
  protocol: ProtocolRecommendation,
  database: DatabaseRecommendation.or(z.string()), // Support "PostgreSQL + Redis"
  pattern: PatternRecommendation,
  messaging: MessagingRecommendation,
  reasoning: z.string(),
  tradeoffs: Tradeoff,
  alternatives: z.array(Alternative).optional(),
});

export type Recommendation = z.infer<typeof RecommendationSchema>;
```

**Step 3: Create index.ts**

```typescript
export * from './requirements';
export * from './recommendations';
```

**Step 4: Run type check to verify schemas**

```bash
cd "C:\Users\Administrator\Workspace\lukeware\clawdevs-ai"
npx tsc --noEmit docker/base/openclaw-config/shared/schemas/index.ts
```

Expected: No errors

**Step 5: Commit**

```bash
git add "docker/base/openclaw-config/shared/schemas/"
git commit -m "feat: add zod schemas for requirements and recommendations

Schemas define:
- Requirements: volume, latency, cost, reliability, data complexity, time-to-market
- Recommendations: language, protocol, database, pattern, messaging, reasoning, tradeoffs
- Used by all agents' before_execution hooks

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 1.3: Create Base Utilities for Requirement Parsing

**Files:**
- Create: `docker/base/openclaw-config/shared/utils/requirement-parser.ts`
- Create: `docker/base/openclaw-config/shared/utils/logger.ts`
- Create: `docker/base/openclaw-config/shared/utils/index.ts`

**Step 1: Create requirement-parser.ts**

```typescript
import { Requirements, RequirementsSchema } from '../schemas';

export interface RequirementSource {
  conversation?: string;
  config?: Record<string, any>;
  system_prompt?: string;
}

/**
 * Parse requirements from multiple sources in cascade order:
 * 1. Conversation/User input
 * 2. Project config (.clawdbot.json, environment variables)
 * 3. System prompt
 */
export async function parseRequirements(
  source: RequirementSource,
): Promise<Requirements | null> {
  // Try conversation first
  if (source.conversation) {
    const parsed = parseFromConversation(source.conversation);
    if (parsed) return parsed;
  }

  // Try config second
  if (source.config) {
    const parsed = parseFromConfig(source.config);
    if (parsed) return parsed;
  }

  // Try system prompt last
  if (source.system_prompt) {
    const parsed = parseFromSystemPrompt(source.system_prompt);
    if (parsed) return parsed;
  }

  return null;
}

function parseFromConversation(text: string): Requirements | null {
  // Look for volume mentions
  let volume: any = undefined;
  if (text.match(/1[.,]?0*\s*[mM]/)) volume = 'extreme';
  else if (text.match(/100[kK]/)) volume = 'high';
  else if (text.match(/10[kK]/)) volume = 'medium';
  else if (text.match(/startup|small|limited/i)) volume = 'low';

  // Look for latency mentions
  let latency: any = undefined;
  if (text.match(/<\s*10\s*ms/i)) latency = 'ultra';
  else if (text.match(/<\s*100\s*ms|low.?latency|real.?time/i)) latency = 'realtime';
  else if (text.match(/<\s*500\s*ms|responsive/i)) latency = 'responsive';
  else if (text.match(/<\s*1\s*s|normal.?latency/i)) latency = 'normal';
  else if (text.match(/latency.?not.?critical|relaxed/i)) latency = 'relaxed';

  // Build partial object
  const partial: any = {};
  if (volume) partial.volume = volume;
  if (latency) partial.latency = latency;

  // If we found anything, return with defaults for missing fields
  if (Object.keys(partial).length > 0) {
    return {
      volume: partial.volume || 'medium',
      latency: partial.latency || 'normal',
      cost_sensitivity: 'medium',
      reliability: 'acceptable',
      data_complexity: 'moderate',
      time_to_market: 'normal',
      ...partial,
    };
  }

  return null;
}

function parseFromConfig(config: Record<string, any>): Requirements | null {
  try {
    const {
      volume,
      latency,
      cost_sensitivity,
      reliability,
      data_complexity,
      time_to_market,
    } = config;

    if (!volume && !latency && !cost_sensitivity) return null;

    return RequirementsSchema.parse({
      volume: volume || 'medium',
      latency: latency || 'normal',
      cost_sensitivity: cost_sensitivity || 'medium',
      reliability: reliability || 'acceptable',
      data_complexity: data_complexity || 'moderate',
      time_to_market: time_to_market || 'normal',
    });
  } catch {
    return null;
  }
}

function parseFromSystemPrompt(text: string): Requirements | null {
  // Similar pattern matching as conversation
  // but look for explicit patterns in system prompt
  const partial: any = {};

  if (text.match(/high.?volume|scale|millions/i)) partial.volume = 'high';
  if (text.match(/low.?latency|fast|responsive/i)) partial.latency = 'responsive';
  if (text.match(/cost.?sensitive|startup|budget/i)) partial.cost_sensitivity = 'high';
  if (text.match(/critical|reliability|99\.9/i)) partial.reliability = 'critical';

  if (Object.keys(partial).length > 0) {
    return {
      volume: partial.volume || 'medium',
      latency: partial.latency || 'normal',
      cost_sensitivity: partial.cost_sensitivity || 'medium',
      reliability: partial.reliability || 'acceptable',
      data_complexity: 'moderate',
      time_to_market: 'normal',
      ...partial,
    };
  }

  return null;
}
```

**Step 2: Create logger.ts**

```typescript
export interface LogEntry {
  level: 'debug' | 'info' | 'warn' | 'error';
  timestamp: Date;
  message: string;
  data?: Record<string, any>;
}

export class Logger {
  private logs: LogEntry[] = [];

  log(level: LogEntry['level'], message: string, data?: Record<string, any>) {
    const entry: LogEntry = {
      level,
      timestamp: new Date(),
      message,
      data,
    };
    this.logs.push(entry);
    console.log(`[${level.toUpperCase()}] ${message}`, data || '');
  }

  debug(message: string, data?: Record<string, any>) {
    this.log('debug', message, data);
  }

  info(message: string, data?: Record<string, any>) {
    this.log('info', message, data);
  }

  warn(message: string, data?: Record<string, any>) {
    this.log('warn', message, data);
  }

  error(message: string, data?: Record<string, any>) {
    this.log('error', message, data);
  }

  getLogs(): LogEntry[] {
    return this.logs;
  }

  clear() {
    this.logs = [];
  }
}

export const logger = new Logger();
```

**Step 3: Create index.ts**

```typescript
export * from './requirement-parser';
export * from './logger';
```

**Step 4: Run tests on parser**

```bash
cd "C:\Users\Administrator\Workspace\lukeware\clawdevs-ai"
npm test -- docker/base/openclaw-config/shared/utils/requirement-parser.test.ts
```

Expected: Tests pass (or create new if not found)

**Step 5: Commit**

```bash
git add "docker/base/openclaw-config/shared/utils/"
git commit -m "feat: add requirement parser and logger utilities

Includes:
- Requirement parsing with 3-level cascade (conversation → config → system_prompt)
- Pattern matching for volume, latency, cost, reliability mentions
- Structured logger for hook execution tracking
- Used by all agents' before_execution hooks

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Phase 2: Refactor First Agent (dev_backend) as Golden Template

### Task 2.1: Analyze Current dev_backend Skills

**Files:**
- Read: `docker/base/openclaw-config/agents/dev_backend/`
- Create: `docker/base/openclaw-config/agents/dev_backend/REFACTORING_NOTES.md`

**Step 1: List all current dev_backend skills**

```bash
ls -la "C:\Users\Administrator\Workspace\lukeware\clawdevs-ai\docker\base\openclaw-config\agents\dev_backend\skills\"
```

**Step 2: Read current SKILL.md**

```bash
cat "C:\Users\Administrator\Workspace\lukeware\clawdevs-ai\docker\base\openclaw-config\agents\dev_backend\skills\dev_backend_implementation\SKILL.md"
```

**Step 3: Document current state**

Create `REFACTORING_NOTES.md`:

```markdown
# dev_backend Refactoring Notes

## Current State Analysis

### Skills Found
- dev_backend_implementation

### Current Structure
- Single SKILL.md file
- No manifest.json
- No src/ directory
- No tests
- No comprehensive documentation
- No examples

### Content Summary
- Focus on implementation flow
- Quality gates defined
- Fallback commands for different languages
- Guardrails present but not structured

## Migration Plan

### What to Keep
- Core flow and quality gates
- Language fallback commands
- Guardrails (never bypass tests, never commit secrets)

### What to Add
- manifest.json with hooks
- src/ with hook implementation
- Comprehensive tests
- docs/ with multiple guides
- examples/ with real scenarios
- Architecture decision matrix

## Golden Template Validation

This refactoring will serve as template for other 15 agents.
Success criteria:
- All components working
- Hooks making autonomous recommendations
- >80% test coverage
- Clear documentation
- 3+ practical examples
```

**Step 4: Commit**

```bash
git add "docker/base/openclaw-config/agents/dev_backend/REFACTORING_NOTES.md"
git commit -m "docs: document dev_backend current state analysis

Analysis shows:
- Single SKILL.md, no full-stack structure
- No hooks, tests, or comprehensive docs
- Will serve as golden template for refactoring

Next: Create full-stack structure

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 2.2: Create Full-Stack Structure for dev_backend

**Files:**
- Create: Full directory structure per template
- Move: Existing SKILL.md content
- Create: manifest.json, src/, tests/, docs/, examples/

**Step 1: Create directory structure**

```bash
mkdir -p "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/src/hooks"
mkdir -p "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/src/decisions"
mkdir -p "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/src/utils"
mkdir -p "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/src/schemas"
mkdir -p "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/tests/unit"
mkdir -p "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/tests/integration"
mkdir -p "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/docs"
mkdir -p "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/examples"
```

**Step 2: Create SKILL.md (enhanced version)**

```markdown
---
name: dev_backend_implementation
description: Production-grade backend implementation skill with architectural decisions, quality gates, tests, cost-performance optimization, and autonomous tech stack recommendations
version: 2.0.0
author: ClawDevs AI
license: MIT
---

# Dev Backend Implementation (Full-Stack)

Professional backend implementation skill with intelligent architectural decision-making based on requirements, comprehensive quality assurance, and cost-optimized execution.

## When to Execute

- Scheduled queue cycle for `backend` issues
- Immediate handoff from Architect in shared session
- When implementing backend features/services

## Core Responsibilities

1. Understand requirements (volume, latency, cost, reliability)
2. Consult architectural decision hook for recommendations
3. Implement only approved scope with chosen tech stack
4. Add/update tests with >=80% coverage
5. Run lint/test/build/security checks
6. Report evidence and quality metrics to Architect

## Architectural Decision Making

This skill includes a `before_execution` hook that:
- Analyzes requirements from conversation, project config, and system prompt
- Recommends optimal tech stack (Go, TypeScript, Python, Rust, etc)
- Provides reasoning for recommendations
- Documents trade-offs and alternatives

**Example Scenario:**
- Input: "Need to handle 1M requests/second with <100ms latency"
- Hook Output: Go + gRPC + PostgreSQL + Redis (reasoning: efficiency at scale)

## Required Quality Gates

- Security basics: input validation, authentication, secrets management
- Observable behavior aligned to requirements
- Test coverage >=80%
- Performance/cost trade-offs documented
- All tests passing before commit
- Zero security vulnerabilities (CVSS <4.0 before proceeding)

## Fallback Commands (Language-Specific)

- **Node.js**: `npm ci && npm test && npm run lint && npm run build`
- **Python**: `pytest && pylint && python -m py_compile`
- **Go**: `go test ./... && go vet ./... && go build`
- **Rust**: `cargo test && cargo clippy && cargo build`

## Guardrails

- Never bypass tests or security gates
- Never commit secrets or API keys
- Never use destructive git operations
- Never implement beyond approved scope
- Always validate requirements before implementing
- Always document architectural decisions

## Key References

- Design: See ARCHITECTURE.md
- Decisions Matrix: See DECISIONS_MATRIX.md
- Principles: See PRINCIPLES.md
- Examples: See examples/ folder
```

**Step 3: Create manifest.json**

```json
{
  "id": "dev_backend_implementation",
  "name": "Developer Backend Implementation",
  "version": "2.0.0",
  "description": "Production-grade backend implementation with architectural decision hooks and quality assurance",
  "entry": "./src/index.ts",
  "hooks": [
    {
      "event": "before_execution",
      "handler": "beforeExecution",
      "description": "Analyze requirements and recommend tech stack"
    },
    {
      "event": "after_execution",
      "handler": "afterExecution",
      "description": "Log metrics and generate evidence report"
    }
  ],
  "config": {
    "requirementSources": {
      "type": "object",
      "description": "Sources to parse requirements from",
      "properties": {
        "conversation": { "type": "boolean", "default": true },
        "projectConfig": { "type": "boolean", "default": true },
        "systemPrompt": { "type": "boolean", "default": true }
      }
    },
    "testCoverageMin": {
      "type": "number",
      "default": 80,
      "description": "Minimum test coverage percentage"
    },
    "securityScanEnabled": {
      "type": "boolean",
      "default": true,
      "description": "Run security scans before commit"
    }
  }
}
```

**Step 4: Create src/index.ts**

```typescript
import { beforeExecution } from './hooks/before_execution';
import { afterExecution } from './hooks/after_execution';

export { beforeExecution, afterExecution };

export const skillConfig = {
  name: 'dev_backend_implementation',
  version: '2.0.0',
  hooks: {
    beforeExecution,
    afterExecution,
  },
};
```

**Step 5: Commit this structure creation**

```bash
git add "docker/base/openclaw-config/agents/dev_backend/skills/dev_backend_implementation/"
git commit -m "refactor: create full-stack structure for dev_backend

Adds:
- SKILL.md (v2.0.0, enhanced)
- manifest.json with hooks config
- src/ directory with entry point
- tests/, docs/, examples/ directories (populated in next tasks)

Golden template for remaining 15 agents.

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

### Task 2.3: Implement before_execution Hook for dev_backend

**Files:**
- Create: `src/hooks/before_execution.ts`
- Create: `src/decisions/architecture_matrix.ts`
- Create: `src/decisions/recommendations.ts`

[CONTINUE IN NEXT SECTION - TOO LONG]

**Step 1-5: Hook Implementation**

[Will follow same pattern as Task 1, breaking down into implementable steps]

---

## Phase 3: Apply Template to Remaining 15 Agents

[Tasks 3.1 - 3.15 follow same pattern as Phase 2]

### Task 3.1: Refactor dev_frontend
### Task 3.2: Refactor dev_mobile
### Task 3.3: Refactor arquiteto
### Task 3.4: Refactor security_engineer
### Task 3.5: Refactor devops_sre
### Task 3.6: Refactor ux_designer
### Task 3.7: Refactor qa_engineer
### Task 3.8: Refactor dba_data_engineer
### Task 3.9: Refactor memory_curator
### Task 3.10: Refactor ceo
### Task 3.11: Refactor po
### Task 3.12: Refactor agent_reviver
### Task 3.13: Refactor database_healer
### Task 3.14: Refactor shared
### Task 3.15: Final validation and consolidation

---

## Success Criteria

✅ All 16 agents refactored to full-stack structure
✅ Every agent has before_execution hook working
✅ Test coverage >80% across all agents
✅ Documentation complete (README, ARCHITECTURE, PRINCIPLES, examples)
✅ 3+ practical examples per agent
✅ All tests passing
✅ Zero SOLID/KISS/YAGNI violations
✅ Git history clean with conventional commits

---

## Estimated Timeline

- Phase 1 (Setup): ~2-3 hours
- Phase 2 (dev_backend template): ~4-5 hours (Golden reference)
- Phase 3 (dev_frontend through database_healer): ~30-40 hours total
  - ~2-2.5 hours per agent (most can parallelize)
- Phase 4 (Consolidation): ~1-2 hours

**Total Estimated: 40-50 hours**

---

## Next Step

👉 **Use superpowers:subagent-driven-development or executing-plans to begin implementation**

Current recommendation: **Subagent-Driven approach** for this project:
- Fresh subagent per task
- Code review between major sections
- Fast iteration on issues
- Maintains consistency

