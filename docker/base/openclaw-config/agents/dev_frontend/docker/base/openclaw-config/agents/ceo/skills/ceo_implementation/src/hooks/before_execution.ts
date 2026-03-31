import { findMatchingPattern } from "../decisions/patterns";
import { generateRecommendation } from "../decisions/recommendations";
import { parseRequirements } from "../utils/requirement-parser";
import { Logger } from "../utils/logger";

const logger = new Logger("before_execution");

export interface BeforeExecutionInput {
  conversation?: string;
  projectConfig?: Record<string, any>;
  systemPrompt?: string;
}

export interface BeforeExecutionOutput {
  success: boolean;
  recommendation?: any;
  error?: string;
  executionTime?: number;
}

export async function beforeExecutionHook(input: BeforeExecutionInput): Promise<BeforeExecutionOutput> {
  const startTime = Date.now();
  try {
    const requirements = parseRequirements(input);
    const { pattern } = findMatchingPattern({});
    const recommendation = generateRecommendation(pattern, requirements.parsed, requirements.sources);

    return {
      success: true,
      recommendation,
      executionTime: Date.now() - startTime,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      executionTime: Date.now() - startTime,
    };
  }
}
