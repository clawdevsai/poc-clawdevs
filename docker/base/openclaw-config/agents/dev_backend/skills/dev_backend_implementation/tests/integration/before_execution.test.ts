import { beforeExecution, ExecutionContext } from '../../src/hooks/before_execution';

describe('before_execution Hook Integration', () => {
  test('should analyze requirements and generate recommendation from conversation', async () => {
    const context: ExecutionContext = {
      conversation: 'We need to handle 1M requests per second with latency under 100ms',
    };

    const result = await beforeExecution(context);

    expect(result.requirements).not.toBeNull();
    expect(result.requirements?.volume).toBe('extreme');
    expect(result.requirements?.latency).toBe('realtime');
    expect(result.recommendation).not.toBeNull();
    expect(result.recommendation?.language).toBe('go');
    expect(result.recommendation?.protocol).toBe('grpc');
    expect(result.analysis).toBeDefined();
    expect(result.analysis.length).toBeGreaterThan(0);
    expect(result.nextSteps).toBeDefined();
    expect(result.nextSteps.length).toBeGreaterThan(0);
  });

  test('should parse requirements from config', async () => {
    const context: ExecutionContext = {
      config: {
        volume: 'extreme',
        latency: 'realtime',
        costSensitivity: 'low',
        reliability: 'highly_critical',
      },
    };

    const result = await beforeExecution(context);

    expect(result.requirements).not.toBeNull();
    expect(result.requirements?.volume).toBe('extreme');
    expect(result.requirements?.latency).toBe('realtime');
    expect(result.recommendation).not.toBeNull();
    expect(result.recommendation?.language).toBe('go');
  });

  test('should cascade parsing from multiple sources', async () => {
    const context: ExecutionContext = {
      conversation: 'High performance needed',
      config: { costSensitivity: 'low' },
      systemPrompt: 'Critical reliability required',
    };

    const result = await beforeExecution(context);

    expect(result.requirements).not.toBeNull();
    expect(result.recommendation).not.toBeNull();
    expect(result.requirements?.costSensitivity).toBe('low');
    expect(result.requirements?.reliability).toBe('highly_critical');
  });

  test('should include analysis and next steps', async () => {
    const context: ExecutionContext = {
      conversation: '100k requests per second',
    };

    const result = await beforeExecution(context);

    expect(result).toHaveProperty('requirements');
    expect(result).toHaveProperty('recommendation');
    expect(result).toHaveProperty('analysis');
    expect(result).toHaveProperty('nextSteps');
    expect(result.analysis).toContain('Backend Implementation Analysis');
  });

  test('should handle low-cost startup scenario', async () => {
    const context: ExecutionContext = {
      conversation: 'MVP backend for startup with limited budget, needs to launch in 2 weeks',
    };

    const result = await beforeExecution(context);

    expect(result.requirements).not.toBeNull();
    expect(result.requirements?.costSensitivity).toBe('high');
    expect(result.requirements?.timeToMarket).toBe('asap');
    expect(result.recommendation?.language).toBe('typescript');
    expect(result.recommendation?.pattern).toBe('serverless');
  });

  test('should handle high-reliability banking scenario', async () => {
    const context: ExecutionContext = {
      conversation: 'Financial payment system with 99.99% uptime, handles 50k transactions/sec, critical reliability',
    };

    const result = await beforeExecution(context);

    expect(result.requirements).not.toBeNull();
    expect(result.requirements?.reliability).toBe('highly_critical');
    expect(result.requirements?.volume).toBe('high');
    expect(result.recommendation).not.toBeNull();
    expect(result.recommendation?.pattern).toBe('distributed');
  });

  test('should handle real-time data analytics scenario', async () => {
    const context: ExecutionContext = {
      conversation:
        'Real-time analytics platform with streaming data processing, machine learning pipelines, and live dashboard updates',
    };

    const result = await beforeExecution(context);

    expect(result.requirements).not.toBeNull();
    expect(result.requirements?.dataComplexity).toBe('extreme');
    expect(result.recommendation).not.toBeNull();
    expect(result.recommendation?.messaging).toBe('kafka');
  });

  test('should provide confidence scores', async () => {
    const context: ExecutionContext = {
      conversation: 'We need to handle 1M requests per second with latency under 100ms',
    };

    const result = await beforeExecution(context);

    expect(result.confidence).toBeDefined();
    expect(result.confidence.requirementsParsing).toBeGreaterThan(0);
    expect(result.confidence.recommendationMatch).toBeGreaterThan(0);
    expect(result.confidence.requirementsParsing).toBeLessThanOrEqual(100);
    expect(result.confidence.recommendationMatch).toBeLessThanOrEqual(100);
  });

  test('should generate implementation roadmap in next steps', async () => {
    const context: ExecutionContext = {
      conversation: 'We need to handle 1M requests per second with latency under 100ms',
    };

    const result = await beforeExecution(context);

    expect(result.nextSteps.length).toBeGreaterThan(0);
    expect(result.nextSteps[0]).toContain('Initialize project');
    expect(Array.isArray(result.nextSteps)).toBe(true);
    result.nextSteps.forEach((step) => {
      expect(typeof step).toBe('string');
      expect(step.length).toBeGreaterThan(0);
    });
  });

  test('should handle graceful error when no input provided', async () => {
    const context: ExecutionContext = {};

    const result = await beforeExecution(context);

    // Should not throw, should return a result
    expect(result).toBeDefined();
    expect(result.analysis).toBeDefined();
  });

  test('should include trade-off analysis in analysis text', async () => {
    const context: ExecutionContext = {
      conversation: 'We need to handle 1M requests per second with latency under 100ms',
    };

    const result = await beforeExecution(context);

    expect(result.analysis).toContain('Trade-off');
    expect(result.analysis).toContain('Performance');
    expect(result.analysis).toContain('Development Speed');
  });

  test('should include alternative approaches in analysis', async () => {
    const context: ExecutionContext = {
      conversation: 'We need to handle 1M requests per second with latency under 100ms',
    };

    const result = await beforeExecution(context);

    expect(result.analysis).toContain('Alternative');
  });

  test('should recommend specific database for requirements', async () => {
    const context: ExecutionContext = {
      conversation:
        'Standard e-commerce backend with moderate scale, product catalog, orders, and user management',
    };

    const result = await beforeExecution(context);

    expect(result.recommendation?.database).toBeDefined();
    expect(typeof result.recommendation?.database).toBe('string');
  });

  test('should handle complex multi-requirement scenario', async () => {
    const context: ExecutionContext = {
      conversation:
        'Building a real-time collaboration platform (like Figma) that needs to handle 1M concurrent users with <50ms latency, complex data synchronization, on-premise deployment, and 99.99% uptime SLA',
    };

    const result = await beforeExecution(context);

    expect(result.requirements).not.toBeNull();
    expect(result.recommendation).not.toBeNull();
    expect(result.analysis.length).toBeGreaterThan(200);
    expect(result.nextSteps.length).toBeGreaterThanOrEqual(5);
  });

  test('should provide different recommendations for different scenarios', async () => {
    const startupContext: ExecutionContext = {
      conversation: 'MVP startup with 2-week launch timeline',
    };

    const enterpriseContext: ExecutionContext = {
      conversation: 'Enterprise system with 99.99% uptime and unlimited budget',
    };

    const startupResult = await beforeExecution(startupContext);
    const enterpriseResult = await beforeExecution(enterpriseContext);

    expect(startupResult.recommendation?.pattern).not.toBe(enterpriseResult.recommendation?.pattern);
  });

  test('should handle system prompt with embedded requirements', async () => {
    const context: ExecutionContext = {
      systemPrompt: 'You are a backend architect. Requirements: highly critical reliability, 99.99% uptime',
    };

    const result = await beforeExecution(context);

    expect(result.requirements?.reliability).toBe('highly_critical');
  });

  test('should parse requirements schema correctly', async () => {
    const context: ExecutionContext = {
      config: {
        volume: 'extreme',
        latency: 'realtime',
        costSensitivity: 'low',
        reliability: 'critical',
        dataComplexity: 'complex',
        timeToMarket: 'normal',
      },
    };

    const result = await beforeExecution(context);

    expect(result.requirements?.volume).toBe('extreme');
    expect(result.requirements?.latency).toBe('realtime');
    expect(result.requirements?.costSensitivity).toBe('low');
    expect(result.requirements?.reliability).toBe('critical');
    expect(result.requirements?.dataComplexity).toBe('complex');
    expect(result.requirements?.timeToMarket).toBe('normal');
  });

  test('should recommend appropriate messaging technology', async () => {
    const context: ExecutionContext = {
      conversation: 'Event-driven microservices with async processing and real-time updates',
    };

    const result = await beforeExecution(context);

    expect(result.recommendation?.messaging).toBeDefined();
    const validMessaging = ['kafka', 'rabbitmq', 'sqs', 'pubsub', 'none'];
    expect(validMessaging).toContain(result.recommendation?.messaging);
  });

  test('should include pattern characteristics in analysis', async () => {
    const context: ExecutionContext = {
      conversation: 'We need to handle 1M requests per second with latency under 100ms',
    };

    const result = await beforeExecution(context);

    expect(result.analysis).toContain('Pattern Characteristics');
    expect(result.analysis).toContain('Best For');
    expect(result.analysis).toContain('Strengths');
    expect(result.analysis).toContain('Challenges');
  });
});
