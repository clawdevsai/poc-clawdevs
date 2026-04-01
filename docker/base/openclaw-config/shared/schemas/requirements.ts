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

import { z } from 'zod';

/**
 * Volume enum - Defines the scale of requests the system must handle
 * - low: Less than 1,000 requests/second
 * - medium: 1,000 to 100,000 requests/second
 * - high: 100,000 to 1,000,000 requests/second
 * - extreme: More than 1,000,000 requests/second
 */
export const VolumeRequirement = z.enum(['low', 'medium', 'high', 'extreme']);
export type VolumeRequirement = z.infer<typeof VolumeRequirement>;

/**
 * Latency enum - Defines the acceptable response time for operations
 * - relaxed: Less than 5 seconds (batch/background jobs)
 * - normal: Less than 1 second (regular operations)
 * - responsive: Less than 500ms (user-facing operations)
 * - realtime: Less than 100ms (interactive operations)
 * - ultra: Less than 10ms (ultra-low latency, real-time streaming)
 */
export const LatencyRequirement = z.enum(['relaxed', 'normal', 'responsive', 'realtime', 'ultra']);
export type LatencyRequirement = z.infer<typeof LatencyRequirement>;

/**
 * CostSensitivity enum - Defines budget constraints and operational costs
 * - unlimited: No budget constraints
 * - low: Minimize costs at the expense of other factors
 * - medium: Balanced cost and performance
 * - high: Cost is a critical constraint, prefer cheaper solutions
 */
export const CostSensitivity = z.enum(['unlimited', 'low', 'medium', 'high']);
export type CostSensitivity = z.infer<typeof CostSensitivity>;

/**
 * Reliability enum - Defines the required system uptime and SLA
 * - best_effort: 95%+ uptime (typical web services)
 * - acceptable: 99%+ uptime (standard SLA)
 * - critical: 99.9%+ uptime (mission-critical systems)
 * - highly_critical: 99.99%+ uptime (financial, healthcare systems)
 */
export const Reliability = z.enum(['best_effort', 'acceptable', 'critical', 'highly_critical']);
export type Reliability = z.infer<typeof Reliability>;

/**
 * DataComplexity enum - Defines the complexity of data structures and relationships
 * - simple: CRUD operations on flat structures
 * - moderate: Relationships between entities, basic joins
 * - complex: Graph-like structures, complex relationships
 * - extreme: Machine learning pipelines, real-time analytics, streaming data
 */
export const DataComplexity = z.enum(['simple', 'moderate', 'complex', 'extreme']);
export type DataComplexity = z.infer<typeof DataComplexity>;

/**
 * TimeToMarket enum - Defines the urgency of deployment
 * - asap: Days to weeks
 * - normal: Weeks to months
 * - flexible: Months or longer, allowing for optimization
 */
export const TimeToMarket = z.enum(['asap', 'normal', 'flexible']);
export type TimeToMarket = z.infer<typeof TimeToMarket>;

/**
 * RequirementsSchema - Defines all non-functional requirements for a system
 *
 * Usage:
 * ```typescript
 * const req = RequirementsSchema.parse({
 *   volume: 'high',
 *   latency: 'responsive',
 *   costSensitivity: 'medium',
 *   reliability: 'critical',
 *   dataComplexity: 'complex',
 *   timeToMarket: 'normal',
 *   specialConstraints: ['GDPR compliance', 'Offline first']
 * });
 * ```
 */
export const RequirementsSchema = z.object({
  /**
   * Scale of requests the system must handle
   */
  volume: VolumeRequirement,

  /**
   * Acceptable response time for operations
   */
  latency: LatencyRequirement,

  /**
   * Budget constraints and operational costs
   */
  costSensitivity: CostSensitivity,

  /**
   * Required system uptime and SLA
   */
  reliability: Reliability,

  /**
   * Complexity of data structures and relationships
   */
  dataComplexity: DataComplexity,

  /**
   * Urgency of deployment to production
   */
  timeToMarket: TimeToMarket,

  /**
   * Optional array of special constraints or requirements
   * Examples: 'GDPR compliance', 'Offline first', 'Real-time collaboration',
   * 'Distributed transactions', 'Multi-tenancy', 'Custom hardware', etc.
   */
  specialConstraints: z.array(z.string()).optional(),
});

export type Requirements = z.infer<typeof RequirementsSchema>;
