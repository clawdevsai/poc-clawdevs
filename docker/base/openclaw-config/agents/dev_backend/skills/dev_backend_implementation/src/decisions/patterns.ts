/**
 * ARCHITECTURAL_PATTERNS - Reference guide for architectural patterns
 *
 * Each pattern defines an approach to structuring a system, with pros, cons,
 * and guidance on when to use it. These patterns are building blocks used
 * in recommendation generation.
 */
export const ARCHITECTURAL_PATTERNS = {
  monolith: {
    name: 'Monolith',
    description: 'Single codebase deployed as one unit with shared database',
    bestFor: ['MVP', 'small teams', 'early stage', 'simple domains', 'rapid prototyping'],
    pros: [
      'Simple to understand and develop',
      'Easy to deploy as single artifact',
      'Straightforward debugging and testing',
      'Low operational overhead',
      'Transactions across entities',
      'Easy to understand call chains',
    ],
    cons: [
      'Hard to scale independent components',
      'Single point of failure',
      'Technology lock-in for entire codebase',
      'Difficult for large teams to coordinate',
      'Database bottleneck under load',
      'Must deploy entire app for single change',
    ],
    whenToUse: [
      'Team size < 10 developers',
      'Single product domain',
      'Manageable complexity (< 100k LOC)',
      'Volume < 10k req/s',
      'Time-to-market critical',
    ],
    whenToAvoid: [
      'Extreme scaling requirements',
      'Multiple independent teams',
      'Diverse technology needs',
      'Complex domain with distinct services',
      'Frequent independent deployments needed',
    ],
  },

  microservices: {
    name: 'Microservices',
    description: 'Multiple independent services, each with own database and business logic',
    bestFor: [
      'independent scaling',
      'team independence',
      'domain separation',
      'technology diversity',
      'large organizations',
    ],
    pros: [
      'Scale each service independently',
      'Teams can work autonomously',
      'Technology diversity per service',
      'Isolate failures (fault isolation)',
      'Independent deployment cycles',
      'Easier to replace/upgrade components',
      'Aligns with organizational structure',
    ],
    cons: [
      'Distributed systems complexity',
      'Network latency between services',
      'Data consistency challenges (eventual consistency)',
      'Harder to debug distributed flows',
      'Operational complexity (monitoring, deployment)',
      'Service discovery and load balancing required',
      'Testing becomes more complex',
    ],
    whenToUse: [
      'Team size > 15 developers',
      'Multiple independent product features',
      'Scalability at component level needed',
      'High availability required',
      'Frequent independent deployments',
      'Different services have different SLAs',
    ],
    whenToAvoid: [
      'Team size < 5 (Conway\'s Law)',
      'Early stage MVP',
      'Simple domain',
      'Latency-sensitive without mature tooling',
      'Limited operational expertise',
    ],
  },

  serverless: {
    name: 'Serverless',
    description: 'Event-driven functions managed by cloud provider, no server management',
    bestFor: [
      'variable load',
      'cost-sensitive',
      'event-driven',
      'background jobs',
      'APIs with unpredictable traffic',
    ],
    pros: [
      'No server management',
      'Pay-per-execution (scale to zero)',
      'Automatic scaling',
      'Reduced operational overhead',
      'Fast deployment (push code, runs)',
      'Built-in monitoring and logging',
      'No capacity planning',
    ],
    cons: [
      'Cold start latency',
      'Vendor lock-in',
      'Resource limits (memory, timeout, storage)',
      'Debugging is harder (distributed logs)',
      'Stateless by design (no persistent connections)',
      'Cost can be unpredictable with high volume',
      'Limited runtime choices',
    ],
    whenToUse: [
      'Traffic patterns unpredictable',
      'Cost is primary concern',
      'Bursty workloads',
      'Background jobs and events',
      'APIs with variable load',
      'Early stage with limited infrastructure',
    ],
    whenToAvoid: [
      'Consistent 1M+ req/s baseline',
      'Sub-100ms latency critical (cold starts)',
      'Long-running processes',
      'Stateful connections (WebSockets)',
      'Complex networking requirements',
      'Heavy vendor lock-in concerns',
    ],
  },

  event_driven: {
    name: 'Event-Driven',
    description: 'Services communicate asynchronously through events, decoupled via message broker',
    bestFor: [
      'real-time updates',
      'streaming data',
      'high throughput',
      'loose coupling',
      'reactive systems',
    ],
    pros: [
      'Services are decoupled',
      'High throughput (async processing)',
      'Scales well with volume',
      'Natural for real-time features',
      'Enables event sourcing',
      'Better resource utilization',
      'Easy to add new consumers',
    ],
    cons: [
      'Eventual consistency (not strong ACID)',
      'Harder to debug event flows',
      'Message broker becomes critical',
      'Testing distributed events complex',
      'Requires careful error handling',
      'Monitoring and observability harder',
      'Ordering guarantees required (per partition)',
    ],
    whenToUse: [
      'Real-time features (notifications, updates)',
      'High-throughput data processing',
      'Complex event orchestration',
      'Multiple systems reacting to events',
      'Streaming data pipelines',
      'Eventually-consistent requirements',
    ],
    whenToAvoid: [
      'Strong consistency required',
      'Simple CRUD operations',
      'Small team unfamiliar with async',
      'Immediate response required to user',
      'Simple request-response patterns',
    ],
  },

  batch: {
    name: 'Batch Processing',
    description: 'Scheduled jobs processing large datasets at fixed intervals',
    bestFor: [
      'scheduled jobs',
      'large data processing',
      'reporting',
      'data transformation',
      'background tasks',
    ],
    pros: [
      'Simple to understand',
      'Good for bulk data processing',
      'Resource efficient (concentrated compute)',
      'Easy to test and debug',
      'Predictable resource usage',
      'Good error handling strategies',
    ],
    cons: [
      'Not real-time (latency inherent)',
      'Data freshness limited to batch interval',
      'Can create load spikes',
      'Failed batches affect all data',
      'Hard to restart partial failures',
      'Not suitable for interactive features',
    ],
    whenToUse: [
      'Scheduled reporting',
      'End-of-day/month processing',
      'Large dataset transformations',
      'Data warehouse updates',
      'Bulk email/notification sending',
      'Machine learning training pipelines',
    ],
    whenToAvoid: [
      'Real-time requirements',
      'Sub-second latency needed',
      'Continuous data updates',
      'Interactive features',
      'Users expect immediate results',
    ],
  },

  streaming: {
    name: 'Streaming',
    description: 'Continuous data processing with ordered events, low-latency analysis',
    bestFor: [
      'real-time analytics',
      'IoT data',
      'financial data',
      'live dashboards',
      'anomaly detection',
    ],
    pros: [
      'Process events as they arrive',
      'Low latency (sub-second)',
      'Handles high-velocity data',
      'Ordered processing guarantees',
      'Natural for time-series data',
      'Scaling with data volume',
    ],
    cons: [
      'Complex frameworks (Kafka, Flink, Spark)',
      'Operational complexity high',
      'Requires distributed infrastructure',
      'State management complex',
      'Testing harder',
      'Monitoring and debugging challenging',
    ],
    whenToUse: [
      'Real-time dashboards',
      'IoT sensor data processing',
      'Financial trading systems',
      'Anomaly detection',
      'Real-time fraud detection',
      'Continuous metric aggregation',
    ],
    whenToAvoid: [
      'Simple use cases (batch sufficient)',
      'Limited ops expertise',
      'Cost-sensitive (infrastructure heavy)',
      'Small data volumes',
      'Strong consistency requirements',
    ],
  },

  distributed: {
    name: 'Distributed Systems',
    description: 'System components span multiple machines/regions with replication and failover',
    bestFor: [
      'high reliability',
      'geographic distribution',
      'fault tolerance',
      'multi-region deployment',
      'mission-critical systems',
    ],
    pros: [
      'Extreme reliability (99.99%+)',
      'Geographic redundancy',
      'Automatic failover',
      'Can survive data center failure',
      'Load distribution across regions',
      'Disaster recovery capability',
    ],
    cons: [
      'Very high operational complexity',
      'Network partitions to handle',
      'Data consistency challenges',
      'Debugging distributed issues hard',
      'Cost (multi-region infrastructure)',
      'Requires deep distributed systems knowledge',
    ],
    whenToUse: [
      'Mission-critical systems',
      'Financial/healthcare systems',
      'Global applications',
      '99.99%+ availability required',
      'Need disaster recovery',
      'Large data that must be distributed',
    ],
    whenToAvoid: [
      'Cost-sensitive projects',
      'Team lacks distributed systems expertise',
      'Simple reliability (99%+ fine)',
      'Single-region acceptable',
      'Complexity not justified',
    ],
  },
};

/**
 * PatternGuide - Helper type for accessing pattern information
 */
export interface PatternGuide {
  name: string;
  description: string;
  bestFor: string[];
  pros: string[];
  cons: string[];
  whenToUse: string[];
  whenToAvoid: string[];
}

/**
 * getPattern - Retrieves a specific pattern guide
 *
 * @param patternName The name of the pattern (key in ARCHITECTURAL_PATTERNS)
 * @returns The pattern guide or undefined if not found
 */
export function getPattern(patternName: keyof typeof ARCHITECTURAL_PATTERNS): PatternGuide {
  return ARCHITECTURAL_PATTERNS[patternName];
}

/**
 * getAllPatternNames - Returns names of all available patterns
 *
 * @returns Array of pattern names
 */
export function getAllPatternNames(): string[] {
  return Object.keys(ARCHITECTURAL_PATTERNS);
}

/**
 * getPatternDescription - Gets a short description of a pattern
 *
 * @param patternName The name of the pattern
 * @returns The description string
 */
export function getPatternDescription(patternName: keyof typeof ARCHITECTURAL_PATTERNS): string {
  return ARCHITECTURAL_PATTERNS[patternName].description;
}

/**
 * getPatternsForUseCase - Filters patterns applicable to a specific use case
 *
 * @param useCase The use case to search for (e.g., 'real-time', 'cost-sensitive')
 * @returns Array of matching pattern names
 */
export function getPatternsForUseCase(useCase: string): string[] {
  return Object.entries(ARCHITECTURAL_PATTERNS)
    .filter(([_, pattern]) => pattern.bestFor.some((use) => use.toLowerCase().includes(useCase.toLowerCase())))
    .map(([name]) => name);
}
