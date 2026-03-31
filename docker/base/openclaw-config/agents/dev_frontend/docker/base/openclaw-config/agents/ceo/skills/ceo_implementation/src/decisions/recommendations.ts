export function generateRecommendation(pattern: any, requirements: any, sources: string[]) {
  return {
    patternId: pattern.id,
    patternName: pattern.name,
    confidence: 0.85,
    reasoning: "Pattern selected based on requirements analysis",
    nextSteps: ["Review pattern", "Validate with team", "Begin implementation"],
  };
}
