import { getRecommendation } from '../../src/decisions/recommendations';
import { Requirements } from '../../src/schemas/requirements';

describe('Tech Stack Recommendations', () => {
  test('should generate recommendation with language choice', () => {
    const reqs: Requirements = {
      volume: 'extreme',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.language).toBeDefined();
    expect(['go', 'rust', 'typescript', 'python', 'java', 'csharp']).toContain(rec?.language);
  });

  test('should include protocol recommendation', () => {
    const reqs: Requirements = {
      volume: 'high',
      latency: 'responsive',
      costSensitivity: 'medium',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(['grpc', 'rest', 'websocket', 'graphql', 'mqtt']).toContain(rec?.protocol);
  });

  test('should include database recommendation', () => {
    const reqs: Requirements = {
      volume: 'medium',
      latency: 'normal',
      costSensitivity: 'medium',
      reliability: 'acceptable',
      dataComplexity: 'moderate',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.database).toBeDefined();
    expect(typeof rec?.database).toBe('string');
  });

  test('should include trade-off analysis', () => {
    const reqs: Requirements = {
      volume: 'extreme',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.tradeoffs).toBeDefined();
    expect(rec?.tradeoffs.performance).toBeDefined();
    expect(rec?.tradeoffs.development_speed).toBeDefined();
    expect(rec?.tradeoffs.operational_complexity).toBeDefined();
    expect(rec?.tradeoffs.cost_efficiency).toBeDefined();
  });

  test('should include reasoning for recommendation', () => {
    const reqs: Requirements = {
      volume: 'low',
      latency: 'normal',
      costSensitivity: 'high',
      reliability: 'acceptable',
      dataComplexity: 'simple',
      timeToMarket: 'asap',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.reasoning).toBeDefined();
    expect(typeof rec?.reasoning).toBe('string');
    expect(rec?.reasoning.length).toBeGreaterThan(50);
  });

  test('should provide alternative recommendations', () => {
    const reqs: Requirements = {
      volume: 'extreme',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec?.alternatives).toBeDefined();
    if (rec?.alternatives) {
      expect(rec.alternatives.length).toBeGreaterThan(0);
      rec.alternatives.forEach((alt) => {
        expect(alt.language).toBeDefined();
        expect(alt.pros).toBeDefined();
        expect(alt.cons).toBeDefined();
        expect(Array.isArray(alt.pros)).toBe(true);
        expect(Array.isArray(alt.cons)).toBe(true);
      });
    }
  });

  test('should recommend appropriate pattern for requirements', () => {
    const reqs: Requirements = {
      volume: 'medium',
      latency: 'normal',
      costSensitivity: 'high',
      reliability: 'acceptable',
      dataComplexity: 'simple',
      timeToMarket: 'asap',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.pattern).toBeDefined();
    const validPatterns = [
      'monolith',
      'microservices',
      'serverless',
      'event_driven',
      'batch',
      'streaming',
      'distributed',
    ];
    expect(validPatterns).toContain(rec?.pattern);
  });

  test('should recommend messaging technology when appropriate', () => {
    const reqs: Requirements = {
      volume: 'high',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'extreme',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.messaging).toBeDefined();
    const validMessaging = ['kafka', 'rabbitmq', 'sqs', 'pubsub', 'none'];
    expect(validMessaging).toContain(rec?.messaging);
  });

  test('should handle extreme performance requirements', () => {
    const reqs: Requirements = {
      volume: 'extreme',
      latency: 'ultra',
      costSensitivity: 'low',
      reliability: 'highly_critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.language).toBe('go');
    expect(rec?.protocol).toBe('grpc');
  });

  test('should handle startup budget constraints', () => {
    const reqs: Requirements = {
      volume: 'low',
      latency: 'normal',
      costSensitivity: 'high',
      reliability: 'acceptable',
      dataComplexity: 'simple',
      timeToMarket: 'asap',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.language).toBe('typescript');
    expect(rec?.pattern).toBe('serverless');
  });

  test('should handle complex data requirements', () => {
    const reqs: Requirements = {
      volume: 'high',
      latency: 'responsive',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'extreme',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.database).toBeDefined();
  });

  test('should balance cost and performance appropriately', () => {
    const reqs: Requirements = {
      volume: 'medium',
      latency: 'responsive',
      costSensitivity: 'medium',
      reliability: 'acceptable',
      dataComplexity: 'moderate',
      timeToMarket: 'normal',
    };
    const rec = getRecommendation(reqs);
    expect(rec).not.toBeNull();
    expect(rec?.language).toBe('typescript');
    expect(rec?.database).toBe('postgresql');
  });
});
