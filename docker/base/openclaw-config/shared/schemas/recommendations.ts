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
 * Language enum - Primary programming language for implementation
 * - go: Fast, compiled, excellent concurrency
 * - rust: Memory-safe, high performance, steep learning curve
 * - typescript: JavaScript ecosystem, rapid development, type safety
 * - python: Rapid prototyping, ML libraries, data science
 * - java: Enterprise maturity, strong typing, verbose
 * - csharp: .NET ecosystem, enterprise features, Windows-focused
 */
export const LanguageRecommendation = z.enum(['go', 'rust', 'typescript', 'python', 'java', 'csharp']);
export type LanguageRecommendation = z.infer<typeof LanguageRecommendation>;

/**
 * Protocol enum - Communication protocol between services
 * - grpc: High-performance, strongly typed, binary format
 * - rest: Stateless, HTTP-based, widely understood
 * - websocket: Bidirectional, real-time communication
 * - graphql: Flexible queries, single endpoint
 * - mqtt: Lightweight, publish-subscribe, IoT-friendly
 */
export const ProtocolRecommendation = z.enum(['grpc', 'rest', 'websocket', 'graphql', 'mqtt']);
export type ProtocolRecommendation = z.infer<typeof ProtocolRecommendation>;

/**
 * Database enum - Primary data store
 * Allows enum values or custom strings for combinations (e.g., "PostgreSQL + Redis")
 */
export const DatabaseRecommendation = z.union([
  z.enum(['postgresql', 'mysql', 'mongodb', 'dynamodb', 'cassandra', 'redis', 'elasticsearch']),
  z.string(), // Allow combinations like "PostgreSQL + Redis"
]);
export type DatabaseRecommendation = z.infer<typeof DatabaseRecommendation>;

/**
 * Pattern enum - Architectural pattern for system design
 * - monolith: Single codebase and deployment unit
 * - microservices: Multiple independent services
 * - serverless: Event-driven, managed by cloud provider
 * - event_driven: Asynchronous communication via events
 * - batch: Scheduled batch processing jobs
 * - streaming: Real-time data streaming and processing
 */
export const ArchitecturalPattern = z.enum(['monolith', 'microservices', 'serverless', 'event_driven', 'batch', 'streaming']);
export type ArchitecturalPattern = z.infer<typeof ArchitecturalPattern>;

/**
 * Messaging enum - Message broker/queue technology
 * - kafka: High-throughput, distributed, event streaming
 * - rabbitmq: Reliable, flexible routing, AMQP protocol
 * - sqs: AWS-managed, scalable, simple
 * - pubsub: Google Cloud Pub/Sub, managed service
 * - none: No messaging layer required
 */
export const MessagingRecommendation = z.enum(['kafka', 'rabbitmq', 'sqs', 'pubsub', 'none']);
export type MessagingRecommendation = z.infer<typeof MessagingRecommendation>;

/**
 * Tradeoff - Evaluation of implementation tradeoffs
 */
export const Tradeoff = z.object({
  /**
   * Performance characteristics (0-100 scale, or descriptive)
   */
  performance: z.union([z.number().min(0).max(100), z.string()]),

  /**
   * Development speed (0-100 scale, or descriptive)
   */
  development_speed: z.union([z.number().min(0).max(100), z.string()]),

  /**
   * Operational complexity (0-100 scale, or descriptive)
   */
  operational_complexity: z.union([z.number().min(0).max(100), z.string()]),

  /**
   * Cost efficiency (0-100 scale, or descriptive)
   */
  cost_efficiency: z.union([z.number().min(0).max(100), z.string()]),
});
export type Tradeoff = z.infer<typeof Tradeoff>;

/**
 * Alternative - Alternative technology or approach
 */
export const Alternative = z.object({
  /**
   * Alternative language or technology name
   */
  language: z.string(),

  /**
   * Advantages of this alternative
   */
  pros: z.array(z.string()),

  /**
   * Disadvantages of this alternative
   */
  cons: z.array(z.string()),
});
export type Alternative = z.infer<typeof Alternative>;

/**
 * RecommendationSchema - Defines all recommended technologies and patterns
 *
 * Usage:
 * ```typescript
 * const rec = RecommendationSchema.parse({
 *   language: 'go',
 *   protocol: 'grpc',
 *   database: 'PostgreSQL + Redis',
 *   pattern: 'microservices',
 *   messaging: 'kafka',
 *   reasoning: 'Go provides fast startup times and excellent concurrency...',
 *   tradeoffs: {
 *     performance: 95,
 *     development_speed: 'Good',
 *     operational_complexity: 'Medium',
 *     cost_efficiency: 'High'
 *   },
 *   alternatives: [
 *     {
 *       language: 'Rust',
 *       pros: ['Memory safety', 'Zero-cost abstractions'],
 *       cons: ['Steep learning curve', 'Slower development']
 *     }
 *   ]
 * });
 * ```
 */
export const RecommendationSchema = z.object({
  /**
   * Primary programming language for implementation
   */
  language: LanguageRecommendation,

  /**
   * Communication protocol between services
   */
  protocol: ProtocolRecommendation,

  /**
   * Primary data store (supports combinations)
   */
  database: DatabaseRecommendation,

  /**
   * Architectural pattern for system design
   */
  pattern: ArchitecturalPattern,

  /**
   * Message broker/queue technology (or 'none')
   */
  messaging: MessagingRecommendation,

  /**
   * Detailed explanation of why this recommendation is suitable
   * Should reference specific requirements and tradeoffs
   */
  reasoning: z.string(),

  /**
   * Evaluation of implementation tradeoffs
   */
  tradeoffs: Tradeoff,

  /**
   * Optional array of alternative approaches with pros/cons
   */
  alternatives: z.array(Alternative).optional(),
});

export type Recommendation = z.infer<typeof RecommendationSchema>;
