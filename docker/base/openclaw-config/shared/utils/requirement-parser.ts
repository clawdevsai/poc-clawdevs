// Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

import {
  Requirements,
  VolumeRequirement,
  LatencyRequirement,
  CostSensitivity,
  Reliability,
  DataComplexity,
  TimeToMarket,
} from '../schemas/requirements';

/**
 * RequirementSource - Defines the three possible sources for requirement data
 * The parser attempts to extract requirements in cascade order:
 * 1. conversation - Natural language requirements from user messages
 * 2. config - Structured configuration object
 * 3. system_prompt - System prompt text that may contain embedded requirements
 */
export interface RequirementSource {
  conversation?: string;
  config?: Record<string, any>;
  system_prompt?: string;
}

/**
 * RequirementParser - Extracts non-functional requirements from multiple sources
 * Uses a cascade approach: conversation → config → system_prompt
 * Provides sensible defaults for any missing fields
 */
class RequirementParser {
  /**
   * Parse requirements from a multi-source input
   * @param source The requirement source containing up to 3 different data types
   * @returns A complete Requirements object with all fields filled (defaults applied to missing)
   */
  public parseRequirements(source: RequirementSource): Requirements {
    // Try conversation first (most likely to have user intent)
    if (source.conversation) {
      const fromConv = this.parseFromConversation(source.conversation);
      if (fromConv) return fromConv;
    }

    // Try config second (structured data)
    if (source.config) {
      const fromConfig = this.parseFromConfig(source.config);
      if (fromConfig) return fromConfig;
    }

    // Try system_prompt last (implicit requirements)
    if (source.system_prompt) {
      const fromPrompt = this.parseFromSystemPrompt(source.system_prompt);
      if (fromPrompt) return fromPrompt;
    }

    // Return defaults if nothing found
    return this.getDefaults();
  }

  /**
   * Parse requirements from natural language conversation
   * Uses regex pattern matching for common keywords and patterns
   * @param text The conversation text to analyze
   * @returns Partial Requirements object or null if nothing detected
   */
  private parseFromConversation(text: string): Requirements | null {
    const lowerText = text.toLowerCase();
    let hasMatch = false;

    const requirements: Partial<Requirements> = {};

    // VOLUME parsing - Look for scale indicators
    // "1.0M requests", "100k rps", "1 million", etc.
    if (/1[.,]?0*\s*[mM]\s*(?:requests|rps|reqs)?/.test(text)) {
      requirements.volume = 'extreme';
      hasMatch = true;
    } else if (/100\s*[kK](?:\s*(?:requests|rps|reqs))?/.test(text)) {
      requirements.volume = 'high';
      hasMatch = true;
    } else if (/(?:thousands?|1[0-9]k|[1-9]0k)\s*(?:requests|rps)?/.test(text)) {
      requirements.volume = 'medium';
      hasMatch = true;
    } else if (
      /(?:scale|volume|throughput|load)/i.test(text) &&
      /(?:small|minimal|low)/i.test(text)
    ) {
      requirements.volume = 'low';
      hasMatch = true;
    }

    // LATENCY parsing - Look for response time indicators
    // "<10ms", "<100ms", "<500ms", "<1s", "<5s"
    if (/<\s*10\s*(?:ms|milliseconds?)/.test(text)) {
      requirements.latency = 'ultra';
      hasMatch = true;
    } else if (/<\s*100\s*(?:ms|milliseconds?)/.test(text)) {
      requirements.latency = 'realtime';
      hasMatch = true;
    } else if (/<\s*500\s*(?:ms|milliseconds?)/.test(text)) {
      requirements.latency = 'responsive';
      hasMatch = true;
    } else if (/<\s*1\s*(?:second|sec|s)/.test(text)) {
      requirements.latency = 'normal';
      hasMatch = true;
    } else if (
      /(?:latency|response\s*time|low\s*latency|high\s*latency)/i.test(text) &&
      /(?:relaxed|batch|background|async)/i.test(text)
    ) {
      requirements.latency = 'relaxed';
      hasMatch = true;
    }

    // COST parsing - Look for budget/cost indicators
    // "startup", "limited budget", "cost-sensitive", "high cost"
    if (/(?:startup|limited|budget|cost[\s-]sensitive|penny\s*pinching)/i.test(text)) {
      requirements.costSensitivity = 'high';
      hasMatch = true;
    } else if (/(?:minimize\s*cost|budget[\s-]conscious|frugal)/i.test(text)) {
      requirements.costSensitivity = 'medium';
      hasMatch = true;
    } else if (/(?:cost\s*is\s*not\s*a|unlimited\s*budget|no\s*budget|enterprise)/i.test(text)) {
      requirements.costSensitivity = 'unlimited';
      hasMatch = true;
    }

    // RELIABILITY parsing - Look for availability/SLA indicators
    // "99.9%", "critical", "mission-critical", "uptime"
    if (/99\.99|four\s*nines|highly[\s-]critical|financial|healthcare/.test(text)) {
      requirements.reliability = 'highly_critical';
      hasMatch = true;
    } else if (/99\.9|three\s*nines|critical|mission[\s-]critical|payment|transaction/.test(text)) {
      requirements.reliability = 'critical';
      hasMatch = true;
    } else if (/99(?:\.\d+)?%?|acceptable|standard[\s-]?sla|production/.test(text)) {
      requirements.reliability = 'acceptable';
      hasMatch = true;
    } else if (/best[\s-]?effort|95%|eventual|best[\s-]?effort|best[\s-]?effort/.test(text)) {
      requirements.reliability = 'best_effort';
      hasMatch = true;
    }

    // COMPLEXITY parsing - Look for data structure complexity
    // "simple CRUD", "complex relationships", "graph structures", "machine learning"
    if (
      /(?:machine\s*learning|realtime\s*analytics|streaming\s*data|ml\s*pipeline|graph[\s-]?db)/i.test(
        text,
      )
    ) {
      requirements.dataComplexity = 'extreme';
      hasMatch = true;
    } else if (
      /(?:complex|relationships|joins|graph[\s-]?like|interconnected|highly[\s-]?related)/i.test(
        text,
      )
    ) {
      requirements.dataComplexity = 'complex';
      hasMatch = true;
    } else if (
      /(?:relationships?|entities?|joins|linked|related|moderate)/i.test(text) &&
      !/complex/i.test(text)
    ) {
      requirements.dataComplexity = 'moderate';
      hasMatch = true;
    } else if (/(?:simple|crud|flat|no\s*relationships|basic)/i.test(text)) {
      requirements.dataComplexity = 'simple';
      hasMatch = true;
    }

    // TIME TO MARKET parsing - Look for urgency indicators
    // "asap", "days", "weeks", "months", "flexible"
    if (/(?:asap|urgent|days?|immediately|within\s*a\s*week|quick|rush)/i.test(text)) {
      requirements.timeToMarket = 'asap';
      hasMatch = true;
    } else if (/(?:weeks?|month|normal|standard|typical)/i.test(text)) {
      requirements.timeToMarket = 'normal';
      hasMatch = true;
    } else if (/(?:months?|flexible|no\s*rush|whenever|optimize|polish|perfection)/i.test(text)) {
      requirements.timeToMarket = 'flexible';
      hasMatch = true;
    }

    // If we found matches, fill in defaults for missing fields
    if (hasMatch) {
      return this.mergeWithDefaults(requirements);
    }

    return null;
  }

  /**
   * Parse requirements from structured config object
   * @param config The configuration object
   * @returns Partial Requirements object or null if no recognized fields found
   */
  private parseFromConfig(config: Record<string, any>): Requirements | null {
    const requirements: Partial<Requirements> = {};
    let hasMatch = false;

    // Check for direct requirement fields in config
    const fields = ['volume', 'latency', 'costSensitivity', 'reliability', 'dataComplexity', 'timeToMarket'] as const;

    for (const field of fields) {
      if (config[field]) {
        try {
          (requirements as any)[field] = config[field];
          hasMatch = true;
        } catch {
          // Invalid value, skip
        }
      }
    }

    // Check for nested requirements object
    if (config.requirements && typeof config.requirements === 'object') {
      for (const field of fields) {
        if (config.requirements[field]) {
          try {
            (requirements as any)[field] = config.requirements[field];
            hasMatch = true;
          } catch {
            // Invalid value, skip
          }
        }
      }
    }

    // Check for special constraints
    if (Array.isArray(config.specialConstraints)) {
      requirements.specialConstraints = config.specialConstraints;
      hasMatch = true;
    } else if (Array.isArray(config.constraints)) {
      requirements.specialConstraints = config.constraints;
      hasMatch = true;
    }

    if (hasMatch) {
      return this.mergeWithDefaults(requirements);
    }

    return null;
  }

  /**
   * Parse requirements from system prompt text
   * Similar to conversation parsing but looks for system-level indicators
   * @param text The system prompt text
   * @returns Partial Requirements object or null if nothing detected
   */
  private parseFromSystemPrompt(text: string): Requirements | null {
    // System prompts often have explicit statements like:
    // "This system must handle 1M requests per second"
    // "Availability requirement: 99.99%"
    // "Data complexity: complex graph relationships"

    const lowerText = text.toLowerCase();
    let hasMatch = false;

    const requirements: Partial<Requirements> = {};

    // Look for explicit "requirement:" or "must:" statements
    const mustStatements = text.match(/(?:requirement|constraint|must|should)[:\s]+([^.!?]+)/gi) || [];

    for (const statement of mustStatements) {
      const lower = statement.toLowerCase();

      // Check volume in requirement statement
      if (/1[.,]?0*\s*[mM]|extreme/.test(lower)) {
        requirements.volume = 'extreme';
        hasMatch = true;
      } else if (/100k|high[\s-]?volume/.test(lower)) {
        requirements.volume = 'high';
        hasMatch = true;
      }

      // Check latency
      if (/<\s*10\s*ms|ultra[\s-]?low/.test(lower)) {
        requirements.latency = 'ultra';
        hasMatch = true;
      } else if (/<\s*100\s*ms|realtime/.test(lower)) {
        requirements.latency = 'realtime';
        hasMatch = true;
      }

      // Check reliability
      if (/99\.99|highly[\s-]?critical/.test(lower)) {
        requirements.reliability = 'highly_critical';
        hasMatch = true;
      } else if (/99\.9|critical/.test(lower)) {
        requirements.reliability = 'critical';
        hasMatch = true;
      }
    }

    // Look for "availability:", "sla:", "uptime:" patterns
    if (/sla|availability|uptime[\s:]/i.test(text)) {
      if (/99\.99/.test(text)) {
        requirements.reliability = 'highly_critical';
        hasMatch = true;
      } else if (/99\.9/.test(text)) {
        requirements.reliability = 'critical';
        hasMatch = true;
      }
    }

    if (hasMatch) {
      return this.mergeWithDefaults(requirements);
    }

    return null;
  }

  /**
   * Get default Requirements when nothing is detected
   * @returns Default Requirements object with sensible defaults
   */
  private getDefaults(): Requirements {
    return {
      volume: 'medium',
      latency: 'normal',
      costSensitivity: 'medium',
      reliability: 'acceptable',
      dataComplexity: 'moderate',
      timeToMarket: 'normal',
      specialConstraints: [],
    };
  }

  /**
   * Merge partial requirements with defaults
   * Fills in any missing fields with sensible default values
   * @param partial The partial requirements object
   * @returns Complete Requirements object
   */
  private mergeWithDefaults(partial: Partial<Requirements>): Requirements {
    const defaults = this.getDefaults();
    return {
      volume: partial.volume || defaults.volume,
      latency: partial.latency || defaults.latency,
      costSensitivity: partial.costSensitivity || defaults.costSensitivity,
      reliability: partial.reliability || defaults.reliability,
      dataComplexity: partial.dataComplexity || defaults.dataComplexity,
      timeToMarket: partial.timeToMarket || defaults.timeToMarket,
      specialConstraints: partial.specialConstraints || defaults.specialConstraints,
    };
  }
}

// Export singleton instance
export const requirementParser = new RequirementParser();

// Export for testing/alternative usage
export default RequirementParser;
