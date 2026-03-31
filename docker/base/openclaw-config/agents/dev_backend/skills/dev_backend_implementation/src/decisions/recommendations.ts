import { Requirements } from '../../../shared/schemas/requirements';
import { Recommendation, RecommendationSchema } from '../../../shared/schemas/recommendations';
import { ARCHITECTURE_PATTERNS, findMatchingPattern, ArchitecturePattern } from './architecture_matrix';

/**
 * getRecommendation - Generates a complete recommendation from requirements
 *
 * Process:
 * 1. Matches requirements against architecture matrix
 * 2. Extracts recommendation data from matched pattern
 * 3. Validates against RecommendationSchema
 * 4. Returns complete Recommendation object with reasoning and alternatives
 *
 * @param requirements The parsed requirements object
 * @returns Complete Recommendation object or null if no pattern matches
 */
export function getRecommendation(requirements: Requirements): Recommendation | null {
  const pattern = findMatchingPattern(requirements);
  if (!pattern) {
    return null;
  }

  try {
    const recommendation: Recommendation = {
      language: pattern.recommendation.language,
      protocol: pattern.recommendation.protocol,
      database: pattern.recommendation.database,
      pattern: pattern.recommendation.pattern,
      messaging: pattern.recommendation.messaging,
      reasoning: buildDetailedReasoning(pattern, requirements),
      tradeoffs: pattern.tradeoffs,
      alternatives: pattern.alternatives?.map((alt) => ({
        language: alt.language,
        pros: alt.pros,
        cons: alt.cons,
      })),
    };

    // Validate against schema
    return RecommendationSchema.parse(recommendation);
  } catch (error) {
    console.error('Failed to generate recommendation', { error, pattern });
    return null;
  }
}

/**
 * buildDetailedReasoning - Constructs detailed reasoning explaining the recommendation
 *
 * Creates a comprehensive explanation that:
 * - Names the matched pattern
 * - Explains why it fits the requirements
 * - Highlights key technology decisions
 * - Mentions important trade-offs
 *
 * @param pattern The matched architecture pattern
 * @param requirements The original requirements
 * @returns Detailed reasoning string
 */
function buildDetailedReasoning(pattern: ArchitecturePattern, requirements: Requirements): string {
  return `
Matched Pattern: ${pattern.name}

This recommendation is based on your requirements:
- Volume: ${requirements.volume}
- Latency: ${requirements.latency}
- Cost Sensitivity: ${requirements.costSensitivity}
- Reliability: ${requirements.reliability}
- Data Complexity: ${requirements.dataComplexity}
- Time to Market: ${requirements.timeToMarket}
${requirements.specialConstraints && requirements.specialConstraints.length > 0 ? `- Special Constraints: ${requirements.specialConstraints.join(', ')}` : ''}

Recommended Tech Stack:
- Language: ${pattern.recommendation.language}
- Protocol: ${pattern.recommendation.protocol}
- Database: ${pattern.recommendation.database}
- Architecture Pattern: ${pattern.recommendation.pattern}
- Messaging: ${pattern.recommendation.messaging}

Rationale:
${pattern.reasoning}

Trade-off Analysis:
- Performance: ${pattern.tradeoffs.performance}
- Development Speed: ${pattern.tradeoffs.development_speed}
- Operational Complexity: ${pattern.tradeoffs.operational_complexity}
- Cost Efficiency: ${pattern.tradeoffs.cost_efficiency}
`;
}

/**
 * getAllPatterns - Returns all available architecture patterns
 *
 * Useful for:
 * - Displaying all options to users
 * - Building decision matrices
 * - Comparing patterns
 *
 * @returns Array of all ArchitecturePattern objects
 */
export function getAllPatterns(): ArchitecturePattern[] {
  return ARCHITECTURE_PATTERNS;
}

/**
 * getPatternByName - Retrieves a specific pattern by name
 *
 * Case-insensitive lookup for easier access to known patterns.
 *
 * @param name The name of the pattern (case-insensitive)
 * @returns The matching ArchitecturePattern or undefined if not found
 */
export function getPatternByName(name: string): ArchitecturePattern | undefined {
  return ARCHITECTURE_PATTERNS.find((p) => p.name.toLowerCase() === name.toLowerCase());
}

/**
 * comparePatterns - Compares multiple patterns side-by-side
 *
 * Returns a comparison matrix showing:
 * - Technology choices for each pattern
 * - Trade-offs comparison
 * - Cost and performance estimates
 *
 * Useful for decision-making when multiple patterns seem viable.
 *
 * @param patternNames Array of pattern names to compare
 * @returns Array of matching patterns or empty array if not all found
 */
export function comparePatterns(patternNames: string[]): ArchitecturePattern[] {
  return patternNames
    .map((name) => getPatternByName(name))
    .filter((pattern): pattern is ArchitecturePattern => pattern !== undefined);
}

/**
 * getPatternsByRequirement - Filters patterns by a specific requirement
 *
 * Examples:
 * - getPatternsByRequirement('volume', 'extreme') - patterns for extreme scale
 * - getPatternsByRequirement('latency', 'ultra') - patterns for ultra-low latency
 * - getPatternsByRequirement('costSensitivity', 'high') - cost-conscious patterns
 *
 * @param requirementType The type of requirement to filter by
 * @param value The value to match
 * @returns Array of patterns that support this requirement value
 */
export function getPatternsByRequirement(
  requirementType: keyof ArchitecturePattern['requirements'],
  value: string,
): ArchitecturePattern[] {
  return ARCHITECTURE_PATTERNS.filter((pattern) => {
    const requirementValues = pattern.requirements[requirementType];
    return requirementValues ? requirementValues.includes(value) : false;
  });
}
