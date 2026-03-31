import { findMatchingPattern, ARCHITECTURE_PATTERNS } from '../../src/decisions/architecture_matrix';
import { Requirements } from '../../src/schemas/requirements';

describe('Architecture Decisions', () => {
  test('should find High-Performance pattern for extreme volume + realtime latency', () => {
    const reqs: Requirements = {
      volume: 'extreme',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern).not.toBeNull();
    expect(pattern?.name).toBe('High Performance');
    expect(pattern?.recommendation.language).toBe('go');
    expect(pattern?.recommendation.protocol).toBe('grpc');
    expect(pattern?.recommendation.pattern).toBe('microservices');
  });

  test('should find Low-Cost pattern for startup budget constraints', () => {
    const reqs: Requirements = {
      volume: 'low',
      latency: 'normal',
      costSensitivity: 'high',
      reliability: 'acceptable',
      dataComplexity: 'simple',
      timeToMarket: 'asap',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern).not.toBeNull();
    expect(pattern?.name).toBe('Low Cost');
    expect(pattern?.recommendation.language).toBe('typescript');
    expect(pattern?.recommendation.pattern).toBe('serverless');
  });

  test('should find High-Reliability pattern for critical uptime requirement', () => {
    const reqs: Requirements = {
      volume: 'high',
      latency: 'responsive',
      costSensitivity: 'low',
      reliability: 'highly_critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern).not.toBeNull();
    expect(pattern?.name).toBe('High Reliability');
    expect(pattern?.recommendation.pattern).toBe('distributed');
  });

  test('should find MVP pattern for fast launch requirement', () => {
    const reqs: Requirements = {
      volume: 'low',
      latency: 'normal',
      costSensitivity: 'high',
      reliability: 'acceptable',
      dataComplexity: 'simple',
      timeToMarket: 'asap',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern).not.toBeNull();
    expect(pattern?.name).toBe('MVP/Quick Launch');
    expect(pattern?.recommendation.pattern).toBe('monolith');
  });

  test('should score patterns correctly based on requirement matching', () => {
    const reqs: Requirements = {
      volume: 'high',
      latency: 'responsive',
      costSensitivity: 'medium',
      reliability: 'critical',
      dataComplexity: 'moderate',
      timeToMarket: 'normal',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern).not.toBeNull();
    expect(pattern?.recommendation).toBeDefined();
    expect(pattern?.tradeoffs).toBeDefined();
  });

  test('should handle all 6+ architecture patterns', () => {
    expect(ARCHITECTURE_PATTERNS.length).toBeGreaterThanOrEqual(6);
    ARCHITECTURE_PATTERNS.forEach((pattern) => {
      expect(pattern.name).toBeDefined();
      expect(pattern.recommendation).toBeDefined();
      expect(pattern.tradeoffs).toBeDefined();
      expect(pattern.reasoning).toBeDefined();
    });
  });

  test('should find Standard Web Application pattern for moderate requirements', () => {
    const reqs: Requirements = {
      volume: 'medium',
      latency: 'responsive',
      costSensitivity: 'medium',
      reliability: 'acceptable',
      dataComplexity: 'moderate',
      timeToMarket: 'normal',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern).not.toBeNull();
    expect(pattern?.name).toBe('Standard Web Application');
    expect(pattern?.recommendation.language).toBe('typescript');
    expect(pattern?.recommendation.database).toBe('postgresql');
  });

  test('should find Real-Time Data Processing pattern for extreme data complexity', () => {
    const reqs: Requirements = {
      volume: 'high',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'extreme',
      timeToMarket: 'normal',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern).not.toBeNull();
    expect(pattern?.name).toBe('Real-Time Data Processing');
    expect(pattern?.recommendation.messaging).toBe('kafka');
    expect(pattern?.recommendation.protocol).toBe('websocket');
  });

  test('should return pattern with valid alternatives', () => {
    const reqs: Requirements = {
      volume: 'extreme',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern?.alternatives).toBeDefined();
    if (pattern?.alternatives) {
      expect(pattern.alternatives.length).toBeGreaterThan(0);
      pattern.alternatives.forEach((alt) => {
        expect(alt.language).toBeDefined();
        expect(alt.pros).toBeDefined();
        expect(alt.cons).toBeDefined();
        expect(Array.isArray(alt.pros)).toBe(true);
        expect(Array.isArray(alt.cons)).toBe(true);
      });
    }
  });

  test('should provide trade-off analysis for selected pattern', () => {
    const reqs: Requirements = {
      volume: 'extreme',
      latency: 'realtime',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'normal',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern?.tradeoffs).toBeDefined();
    expect(pattern?.tradeoffs.performance).toBeDefined();
    expect(pattern?.tradeoffs.development_speed).toBeDefined();
    expect(pattern?.tradeoffs.operational_complexity).toBeDefined();
    expect(pattern?.tradeoffs.cost_efficiency).toBeDefined();
  });

  test('should find pattern for flexible timeline with optimization focus', () => {
    const reqs: Requirements = {
      volume: 'medium',
      latency: 'responsive',
      costSensitivity: 'low',
      reliability: 'critical',
      dataComplexity: 'complex',
      timeToMarket: 'flexible',
    };
    const pattern = findMatchingPattern(reqs);
    expect(pattern).not.toBeNull();
    expect(pattern?.recommendation).toBeDefined();
  });

  test('should handle all volume levels', () => {
    const volumes = ['low', 'medium', 'high', 'extreme'] as const;
    for (const volume of volumes) {
      const reqs: Requirements = {
        volume,
        latency: 'normal',
        costSensitivity: 'medium',
        reliability: 'acceptable',
        dataComplexity: 'simple',
        timeToMarket: 'normal',
      };
      const pattern = findMatchingPattern(reqs);
      expect(pattern).not.toBeNull();
    }
  });

  test('should handle all latency levels', () => {
    const latencies = ['relaxed', 'normal', 'responsive', 'realtime', 'ultra'] as const;
    for (const latency of latencies) {
      const reqs: Requirements = {
        volume: 'medium',
        latency,
        costSensitivity: 'medium',
        reliability: 'acceptable',
        dataComplexity: 'simple',
        timeToMarket: 'normal',
      };
      const pattern = findMatchingPattern(reqs);
      expect(pattern).not.toBeNull();
    }
  });

  test('should handle all reliability levels', () => {
    const reliabilities = ['best_effort', 'acceptable', 'critical', 'highly_critical'] as const;
    for (const reliability of reliabilities) {
      const reqs: Requirements = {
        volume: 'medium',
        latency: 'normal',
        costSensitivity: 'medium',
        reliability,
        dataComplexity: 'simple',
        timeToMarket: 'normal',
      };
      const pattern = findMatchingPattern(reqs);
      expect(pattern).not.toBeNull();
    }
  });
});
