import { Requirements, RequirementsSchema } from '../../../shared/schemas/requirements';
import { Recommendation } from '../../../shared/schemas/recommendations';
import { requirementParser } from '../../../shared/utils/requirement-parser';
import { logger } from '../../../shared/utils/logger';
import { getRecommendation } from '../decisions/recommendations';
import { getPattern } from '../decisions/patterns';

/**
 * ExecutionContext - Input context for before_execution hook
 *
 * The hook receives input from three possible sources in cascade order:
 * 1. conversation - Natural language requirements from user
 * 2. config - Structured configuration object
 * 3. systemPrompt - System prompt with embedded requirements
 */
export interface ExecutionContext {
  /** Natural language conversation containing requirements */
  conversation?: string;

  /** Structured configuration object with settings */
  config?: Record<string, any>;

  /** System prompt potentially containing requirements */
  systemPrompt?: string;
}

/**
 * ExecutionResult - Output from before_execution hook
 *
 * Contains:
 * - Parsed requirements (or null if couldn't determine)
 * - Tech stack recommendation (or null if no pattern matches)
 * - Detailed analysis text
 * - Next steps for implementation
 */
export interface ExecutionResult {
  /** Parsed and validated requirements object */
  requirements: Requirements | null;

  /** Recommended technology stack */
  recommendation: Recommendation | null;

  /** Detailed analysis text for display */
  analysis: string;

  /** Suggested next steps for implementation */
  nextSteps: string[];

  /** Information about decision confidence */
  confidence: {
    /** How confident in the requirements parsing (0-100) */
    requirementsParsing: number;

    /** How confident in the recommendation match (0-100) */
    recommendationMatch: number;
  };
}

/**
 * beforeExecution - Main hook called before skill execution
 *
 * This is the central intelligence of the dev_backend skill. It:
 *
 * 1. **Parses Requirements** - Extracts non-functional requirements from:
 *    - Natural language conversation (most likely to have user intent)
 *    - Structured config (if provided)
 *    - System prompt (fallback, implicit requirements)
 *    Uses cascade logic: attempts conversation → config → system_prompt
 *
 * 2. **Validates Requirements** - Ensures all parsed requirements conform
 *    to the Requirements schema with proper enums and types
 *
 * 3. **Recommends Tech Stack** - Matches requirements against architecture
 *    matrix to find optimal technology choices:
 *    - Language (go, typescript, python, rust, java, csharp)
 *    - Protocol (grpc, rest, websocket, graphql, mqtt)
 *    - Database (PostgreSQL, MongoDB, Redis, etc.)
 *    - Pattern (monolith, microservices, serverless, event-driven, etc.)
 *    - Messaging (kafka, rabbitmq, sqs, pubsub, or none)
 *
 * 4. **Provides Analysis** - Returns detailed explanation of:
 *    - What requirements were detected
 *    - Why this tech stack was recommended
 *    - Trade-offs for each choice
 *    - How alternatives compare
 *
 * 5. **Suggests Next Steps** - Provides implementation guidance:
 *    - What to set up first
 *    - Project structure recommendations
 *    - Testing approach
 *    - Quality gates to implement
 *
 * @param context The execution context with conversation, config, or systemPrompt
 * @returns ExecutionResult with requirements, recommendation, analysis, and next steps
 *
 * @example
 * ```typescript
 * const result = await beforeExecution({
 *   conversation: "I need a backend that handles 1M requests/second with <100ms latency"
 * });
 *
 * // Result:
 * // {
 * //   requirements: {
 * //     volume: 'extreme',
 * //     latency: 'realtime',
 * //     costSensitivity: 'medium',
 * //     reliability: 'critical',
 * //     dataComplexity: 'moderate',
 * //     timeToMarket: 'normal'
 * //   },
 * //   recommendation: {
 * //     language: 'go',
 * //     protocol: 'grpc',
 * //     database: 'PostgreSQL + Redis',
 * //     pattern: 'microservices',
 * //     messaging: 'kafka',
 * //     reasoning: '...',
 * //     tradeoffs: { ... }
 * //   },
 * //   analysis: "### Backend Implementation Analysis\n...",
 * //   nextSteps: [...]
 * // }
 * ```
 */
export async function beforeExecution(context: ExecutionContext): Promise<ExecutionResult> {
  logger.info('before_execution hook started', {
    hasConversation: !!context.conversation,
    hasConfig: !!context.config,
    hasSystemPrompt: !!context.systemPrompt,
  });

  try {
    // Step 1: Parse requirements using cascade logic
    // Priority: conversation → config → system_prompt → defaults
    const requirements = requirementParser.parseRequirements({
      conversation: context.conversation,
      config: context.config,
      system_prompt: context.systemPrompt,
    });

    logger.info('Requirements parsed', {
      volume: requirements.volume,
      latency: requirements.latency,
      costSensitivity: requirements.costSensitivity,
      reliability: requirements.reliability,
      dataComplexity: requirements.dataComplexity,
      timeToMarket: requirements.timeToMarket,
    });

    // Step 2: Validate requirements against schema
    let validatedRequirements: Requirements | null = null;
    let requirementsConfidence = 100;

    try {
      validatedRequirements = RequirementsSchema.parse(requirements);
      logger.info('Requirements validated successfully');

      // If we had to use defaults, lower confidence
      if (!context.conversation && !context.config && !context.systemPrompt) {
        requirementsConfidence = 50; // Using all defaults
        logger.warn('Using default requirements (no input provided)', { confidence: requirementsConfidence });
      } else if (
        requirements.volume === 'medium' &&
        requirements.latency === 'normal' &&
        requirements.costSensitivity === 'medium'
      ) {
        requirementsConfidence = 70; // Partially defaulted
        logger.warn('Partially using defaults for some fields', { confidence: requirementsConfidence });
      }
    } catch (error: any) {
      logger.error('Requirements validation failed', { error: error.message });
      // Continue with null and explain in result
      validatedRequirements = null;
    }

    // Step 3: Get tech stack recommendation
    let recommendation: Recommendation | null = null;
    let recommendationConfidence = 0;

    if (validatedRequirements) {
      recommendation = getRecommendation(validatedRequirements);

      if (recommendation) {
        recommendationConfidence = 95; // High confidence if matched
        logger.info('Recommendation generated', {
          language: recommendation.language,
          pattern: recommendation.pattern,
          database: recommendation.database,
        });
      } else {
        logger.warn('No matching pattern found for requirements', { requirements: validatedRequirements });
        recommendationConfidence = 0;
      }
    }

    // Step 4: Generate analysis summary
    const analysis = generateAnalysis(validatedRequirements, recommendation, requirementsConfidence);

    // Step 5: Suggest next steps
    const nextSteps = generateNextSteps(recommendation, validatedRequirements);

    logger.info('before_execution hook completed successfully', {
      hasRequirements: validatedRequirements !== null,
      hasRecommendation: recommendation !== null,
      requirementsConfidence,
      recommendationConfidence,
    });

    return {
      requirements: validatedRequirements,
      recommendation,
      analysis,
      nextSteps,
      confidence: {
        requirementsParsing: requirementsConfidence,
        recommendationMatch: recommendationConfidence,
      },
    };
  } catch (error: any) {
    logger.error('before_execution hook failed with exception', {
      error: error.message,
      stack: error.stack?.split('\n').slice(0, 5),
    });

    // Return graceful error result
    return {
      requirements: null,
      recommendation: null,
      analysis: buildErrorAnalysis(error),
      nextSteps: buildErrorNextSteps(error),
      confidence: {
        requirementsParsing: 0,
        recommendationMatch: 0,
      },
    };
  }
}

/**
 * generateAnalysis - Creates detailed analysis text from requirements and recommendation
 *
 * Generates markdown-formatted analysis that includes:
 * - Requirements detected
 * - Recommended tech stack
 * - Detailed reasoning
 * - Trade-off analysis
 * - Pattern alternatives
 *
 * @param requirements The parsed requirements object
 * @param recommendation The tech stack recommendation
 * @param confidence The confidence level in requirements parsing
 * @returns Formatted analysis string
 */
function generateAnalysis(
  requirements: Requirements | null,
  recommendation: Recommendation | null,
  confidence: number,
): string {
  if (!requirements) {
    return `
# Backend Implementation Analysis

## Status
Unable to determine requirements from provided input.

## Recommended Next Steps
1. Provide explicit requirements in one of these formats:
   - Natural language: "I need to handle 1M requests/second with <100ms latency"
   - Configuration object: { volume: 'extreme', latency: 'realtime' }
   - System prompt with embedded requirements

2. Specify these key requirements:
   - **Volume**: low / medium / high / extreme
   - **Latency**: relaxed / normal / responsive / realtime / ultra
   - **Cost Sensitivity**: unlimited / low / medium / high
   - **Reliability**: best_effort / acceptable / critical / highly_critical
   - **Data Complexity**: simple / moderate / complex / extreme
   - **Time to Market**: asap / normal / flexible

3. Example conversation: "I'm building an MVP backend that needs to handle 10,000 requests per second with less than 500ms latency. Cost is a concern."
`;
  }

  if (!recommendation) {
    return `
# Backend Implementation Analysis

## Requirements Detected
- **Volume**: ${requirements.volume}
- **Latency**: ${requirements.latency}
- **Cost Sensitivity**: ${requirements.costSensitivity}
- **Reliability**: ${requirements.reliability}
- **Data Complexity**: ${requirements.dataComplexity}
- **Time to Market**: ${requirements.timeToMarket}
${requirements.specialConstraints && requirements.specialConstraints.length > 0 ? `- **Special Constraints**: ${requirements.specialConstraints.join(', ')}` : ''}

## Status
Unable to find a matching architecture pattern for these requirements.

This may indicate:
- An unusual or conflicting set of requirements
- Needs for a custom hybrid approach
- Requirements that span multiple patterns

## Recommended Action
Consider:
1. Adjusting requirements (e.g., accepting higher latency for lower cost)
2. Using a hybrid approach combining multiple patterns
3. Consulting with a solutions architect for custom recommendations
`;
  }

  const patternInfo = getPattern(
    recommendation.pattern as keyof ReturnType<typeof getPattern> extends string ? never : keyof ReturnType<typeof getPattern>
  );

  return `
# Backend Implementation Analysis

## Requirements Summary
Based on your inputs, the following requirements were detected:

| Requirement | Value | Impact |
|---|---|---|
| Volume | ${requirements.volume} | Scale requirement for the system |
| Latency | ${requirements.latency} | Response time requirements |
| Cost Sensitivity | ${requirements.costSensitivity} | Budget constraints |
| Reliability | ${requirements.reliability} | Uptime and SLA requirements |
| Data Complexity | ${requirements.dataComplexity} | Complexity of data structures |
| Time to Market | ${requirements.timeToMarket} | Development urgency |
${requirements.specialConstraints && requirements.specialConstraints.length > 0 ? `| Special Constraints | ${requirements.specialConstraints.join(', ')} | Domain-specific requirements |` : ''}

**Confidence**: ${confidence}% (${confidence > 80 ? 'High' : confidence > 60 ? 'Medium' : 'Low'})

## Recommended Tech Stack

### Architecture Pattern: ${recommendation.pattern}
${patternInfo.description}

### Technology Choices
- **Language**: ${recommendation.language}
- **Protocol**: ${recommendation.protocol}
- **Database**: ${recommendation.database}
- **Messaging**: ${recommendation.messaging}

## Detailed Reasoning
${recommendation.reasoning}

## Trade-off Analysis

| Aspect | Assessment |
|---|---|
| Performance | ${recommendation.tradeoffs.performance} |
| Development Speed | ${recommendation.tradeoffs.development_speed} |
| Operational Complexity | ${recommendation.tradeoffs.operational_complexity} |
| Cost Efficiency | ${recommendation.tradeoffs.cost_efficiency} |

## Pattern Characteristics
**Best For**: ${patternInfo.bestFor.join(', ')}

**Strengths**:
${patternInfo.pros.map((pro) => `- ${pro}`).join('\n')}

**Challenges**:
${patternInfo.cons.map((con) => `- ${con}`).join('\n')}

${
  recommendation.alternatives && recommendation.alternatives.length > 0
    ? `
## Alternative Approaches

${recommendation.alternatives
  .map(
    (alt) => `
### ${alt.language}

**Advantages**:
${alt.pros.map((pro) => `- ${pro}`).join('\n')}

**Disadvantages**:
${alt.cons.map((con) => `- ${con}`).join('\n')}
`,
  )
  .join('\n')}
`
    : ''
}
`;
}

/**
 * generateNextSteps - Creates implementation roadmap from recommendation
 *
 * Provides concrete, actionable next steps:
 * - Setup instructions
 * - Project structure
 * - Configuration
 * - Testing approach
 * - Quality gates
 *
 * @param recommendation The tech stack recommendation
 * @param requirements The validated requirements
 * @returns Array of step descriptions
 */
function generateNextSteps(recommendation: Recommendation | null, requirements: Requirements | null): string[] {
  if (!recommendation) {
    return [
      'Clarify and refine requirements',
      'Check against available architecture patterns',
      'Consult with team on trade-offs',
      'Re-run analysis with updated requirements',
    ];
  }

  const steps: string[] = [];

  // Setup steps
  steps.push(`Initialize project with ${recommendation.language} (${getLanguageDescription(recommendation.language)})`);
  steps.push(`Set up ${recommendation.database} database with proper configuration`);

  // Architecture-specific steps
  switch (recommendation.pattern) {
    case 'monolith':
      steps.push('Structure as single Express/Fastify application');
      steps.push('Organize code by feature/domain modules');
      break;
    case 'microservices':
      steps.push('Plan service boundaries based on domain');
      steps.push('Set up service discovery and inter-service communication');
      steps.push('Configure service mesh (Istio/Linkerd) for production');
      break;
    case 'serverless':
      steps.push('Set up cloud provider account (AWS Lambda/Google Cloud Run/Azure)');
      steps.push('Configure API Gateway for HTTP endpoints');
      steps.push('Set up structured logging and distributed tracing');
      break;
    case 'event_driven':
      steps.push(`Set up ${recommendation.messaging} as event broker`);
      steps.push('Define event schemas and topics');
      steps.push('Implement event handlers and sagas');
      break;
    case 'streaming':
      steps.push(`Configure ${recommendation.messaging} cluster for data streams`);
      steps.push('Design stream topology and partitioning strategy');
      steps.push('Implement state management for streaming operations');
      break;
  }

  // Protocol-specific setup
  switch (recommendation.protocol) {
    case 'grpc':
      steps.push('Define Protocol Buffers (.proto) for service contracts');
      steps.push('Generate gRPC client/server stubs');
      break;
    case 'websocket':
      steps.push('Set up WebSocket server with connection management');
      steps.push('Implement connection pooling and heartbeats');
      break;
    case 'rest':
      steps.push('Define OpenAPI/Swagger specification');
      steps.push('Implement RESTful endpoints with proper HTTP semantics');
      break;
  }

  // Quality and testing
  steps.push('Set up automated testing (unit, integration, load testing)');
  steps.push('Configure quality gates: minimum 80% code coverage, linting, type checking');
  steps.push('Set up CI/CD pipeline with automated deployments');

  // Monitoring and operations
  if (requirements?.reliability === 'highly_critical' || requirements?.reliability === 'critical') {
    steps.push('Configure comprehensive monitoring and alerting');
    steps.push('Set up distributed tracing (Jaeger/Datadog)');
    steps.push('Document runbooks for common operational issues');
  }

  // Performance optimization
  if (requirements?.volume === 'extreme' || requirements?.latency === 'ultra') {
    steps.push('Perform load testing and profiling');
    steps.push('Optimize database queries and add caching layer');
    steps.push('Configure CDN and edge caching strategies');
  }

  return steps;
}

/**
 * getLanguageDescription - Returns a short description of a programming language
 *
 * @param language The language enum value
 * @returns Descriptive string
 */
function getLanguageDescription(language: string): string {
  const descriptions: Record<string, string> = {
    go: 'Fast, compiled, excellent concurrency',
    rust: 'Memory-safe, high performance, steep learning curve',
    typescript: 'JavaScript ecosystem, rapid development, type safety',
    python: 'Rapid prototyping, ML libraries, data science',
    java: 'Enterprise maturity, strong typing, verbose',
    csharp: '.NET ecosystem, enterprise features',
  };
  return descriptions[language] || language;
}

/**
 * buildErrorAnalysis - Creates analysis text when an error occurs
 *
 * @param error The error that occurred
 * @returns Error analysis string
 */
function buildErrorAnalysis(error: Error): string {
  return `
# Backend Implementation Analysis

## Error
An error occurred while analyzing requirements:

\`\`\`
${error.message}
\`\`\`

## Troubleshooting Steps
1. Check that all input is valid (conversation, config, systemPrompt)
2. Ensure requirements follow the defined enums:
   - Volume: low, medium, high, extreme
   - Latency: relaxed, normal, responsive, realtime, ultra
   - Cost Sensitivity: unlimited, low, medium, high
   - Reliability: best_effort, acceptable, critical, highly_critical

3. Review the error message for specific validation failures
4. Try again with clarified input

## Support
If this error persists:
- Check the logs for detailed error information
- Validate input against the Requirements schema
- Consult the architecture decision documentation
`;
}

/**
 * buildErrorNextSteps - Provides recovery steps when an error occurs
 *
 * @param error The error that occurred
 * @returns Recovery step strings
 */
function buildErrorNextSteps(error: Error): string[] {
  return [
    'Review the error message above',
    'Validate input against Requirements schema',
    'Try with simpler, more explicit requirements',
    'Check documentation for valid enum values',
    'Run with --debug flag for detailed logs',
  ];
}
