import { requirementParser } from '../../src/utils/requirement-parser';

describe('Requirement Parser', () => {
  test('should parse volume from natural language - extreme', () => {
    const text = 'We need to handle 1M requests per second';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.volume).toBe('extreme');
  });

  test('should parse volume from natural language - high', () => {
    const text = 'We need to handle 100k requests per second';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.volume).toBe('high');
  });

  test('should parse volume from natural language - medium', () => {
    const text = 'We need to handle thousands of requests per second';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.volume).toBe('medium');
  });

  test('should parse latency from natural language - realtime', () => {
    const text = 'Latency must be under 100ms';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.latency).toBe('realtime');
  });

  test('should parse latency from natural language - ultra', () => {
    const text = 'Response time must be less than 10ms';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.latency).toBe('ultra');
  });

  test('should parse latency from natural language - responsive', () => {
    const text = 'We need response times under 500ms';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.latency).toBe('responsive');
  });

  test('should parse latency from natural language - normal', () => {
    const text = 'Response should come back in under 1 second';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.latency).toBe('normal');
  });

  test('should parse cost sensitivity from natural language - high', () => {
    const text = 'We are a startup with limited budget, so cost is critical';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.costSensitivity).toBe('high');
  });

  test('should parse cost sensitivity from natural language - unlimited', () => {
    const text = 'Cost is not a concern for our enterprise deployment';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.costSensitivity).toBe('unlimited');
  });

  test('should parse reliability from natural language - highly_critical', () => {
    const text = 'We need 99.99% uptime for our financial system';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.reliability).toBe('highly_critical');
  });

  test('should parse reliability from natural language - critical', () => {
    const text = 'This is mission-critical with 99.9% SLA requirement';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.reliability).toBe('critical');
  });

  test('should parse data complexity from natural language - extreme', () => {
    const text = 'We need real-time analytics with machine learning pipelines';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.dataComplexity).toBe('extreme');
  });

  test('should parse data complexity from natural language - complex', () => {
    const text = 'Complex relationships between entities with graph-like structures';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.dataComplexity).toBe('complex');
  });

  test('should parse data complexity from natural language - simple', () => {
    const text = 'Simple CRUD operations with no relationships';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.dataComplexity).toBe('simple');
  });

  test('should parse time to market from natural language - asap', () => {
    const text = 'We need this shipped immediately, within days';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.timeToMarket).toBe('asap');
  });

  test('should parse time to market from natural language - flexible', () => {
    const text = 'We have months to optimize and polish this solution';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.timeToMarket).toBe('flexible');
  });

  test('should parse requirements from config object', () => {
    const config = {
      volume: 'extreme',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const reqs = requirementParser.parseRequirements({ config });
    expect(reqs.volume).toBe('extreme');
    expect(reqs.latency).toBe('realtime');
    expect(reqs.reliability).toBe('critical');
  });

  test('should parse requirements from nested requirements object in config', () => {
    const config = {
      requirements: {
        volume: 'high',
        latency: 'responsive',
      },
    };
    const reqs = requirementParser.parseRequirements({ config });
    expect(reqs.volume).toBe('high');
    expect(reqs.latency).toBe('responsive');
  });

  test('should parse special constraints from config', () => {
    const config = {
      volume: 'medium',
      specialConstraints: ['GDPR compliant', 'On-premise only'],
    };
    const reqs = requirementParser.parseRequirements({ config });
    expect(reqs.specialConstraints).toEqual(['GDPR compliant', 'On-premise only']);
  });

  test('should cascade from conversation to config to system prompt', () => {
    const text = 'We need 1M requests per second';
    const config = { latency: 'realtime' };
    const systemPrompt = 'Highly critical reliability required';

    const reqs = requirementParser.parseRequirements({
      conversation: text,
      config,
      system_prompt: systemPrompt,
    });

    expect(reqs.volume).toBe('extreme'); // From conversation
    expect(reqs.latency).toBe('realtime'); // From config (conversation didn't set it)
    expect(reqs.reliability).toBe('highly_critical'); // From system prompt
  });

  test('should use defaults when no input provided', () => {
    const reqs = requirementParser.parseRequirements({});
    expect(reqs.volume).toBe('medium');
    expect(reqs.latency).toBe('normal');
    expect(reqs.costSensitivity).toBe('medium');
    expect(reqs.reliability).toBe('acceptable');
    expect(reqs.dataComplexity).toBe('moderate');
    expect(reqs.timeToMarket).toBe('normal');
  });

  test('should parse multiple requirements from single conversation', () => {
    const text =
      'We need to handle 1M requests/sec with <100ms latency, 99.99% uptime, complex data relationships, and we need it deployed in 2 weeks';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.volume).toBe('extreme');
    expect(reqs.latency).toBe('realtime');
    expect(reqs.reliability).toBe('highly_critical');
    expect(reqs.dataComplexity).toBe('complex');
    expect(reqs.timeToMarket).toBe('asap');
  });

  test('should parse SLA requirements from system prompt', () => {
    const systemPrompt = 'System must maintain 99.99% availability SLA';
    const reqs = requirementParser.parseRequirements({ system_prompt: systemPrompt });
    expect(reqs.reliability).toBe('highly_critical');
  });

  test('should handle various 1M formats', () => {
    const variations = ['1M requests', '1,000,000 rps', '1.0M req/s'];
    for (const text of variations) {
      const reqs = requirementParser.parseRequirements({ conversation: text });
      expect(reqs.volume).toBe('extreme');
    }
  });

  test('should parse cost sensitivity variations', () => {
    const testCases = [
      { text: 'startup with limited budget', expected: 'high' },
      { text: 'minimize costs', expected: 'medium' },
      { text: 'enterprise with unlimited budget', expected: 'unlimited' },
    ];

    for (const { text, expected } of testCases) {
      const reqs = requirementParser.parseRequirements({ conversation: text });
      expect(reqs.costSensitivity).toBe(expected);
    }
  });

  test('should parse batch/background job requirements', () => {
    const text = 'Batch processing jobs with relaxed latency requirements';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.latency).toBe('relaxed');
  });

  test('should merge partial config with defaults', () => {
    const config = { volume: 'high' };
    const reqs = requirementParser.parseRequirements({ config });
    expect(reqs.volume).toBe('high');
    expect(reqs.latency).toBe('normal'); // Default
    expect(reqs.costSensitivity).toBe('medium'); // Default
  });

  test('should handle conversation with partial matches', () => {
    const text = 'High volume backend service';
    const reqs = requirementParser.parseRequirements({ conversation: text });
    expect(reqs.volume).toBe('high');
    // Other fields should be defaults
    expect(reqs.latency).toBe('normal');
    expect(reqs.costSensitivity).toBe('medium');
  });
});
