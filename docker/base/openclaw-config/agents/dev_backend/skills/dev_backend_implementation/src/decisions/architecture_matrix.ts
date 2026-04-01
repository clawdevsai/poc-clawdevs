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

/**
 * Architecture Decision Matrix
 *
 * Maps requirements (performance, reliability, cost) to tech stack recommendations.
 * Used by beforeExecution hook to guide implementation decisions.
 *
 * Will be fully implemented in Task 2.3 with:
 * - Scoring algorithm
 * - Pattern matching
 * - Trade-off analysis
 */

export const ARCHITECTURE_MATRIX = [
  {
    name: 'High Performance',
    volume: 'extreme',
    latency: 'realtime',
    language: 'Go',
    protocol: 'gRPC',
    database: 'Redis + PostgreSQL',
    cache: 'Redis/Memcached',
    messaging: 'Kafka/RabbitMQ',
    deployment: 'Kubernetes',
    minServers: 5,
    estimatedCost: 'High',
  },
  {
    name: 'Standard Web',
    volume: 'moderate',
    latency: '200-500ms',
    language: 'Node.js / Python',
    protocol: 'REST/GraphQL',
    database: 'PostgreSQL',
    cache: 'Redis',
    messaging: 'Bull/Celery',
    deployment: 'Docker + Load Balancer',
    minServers: 2,
    estimatedCost: 'Medium',
  },
  {
    name: 'Low Cost MVP',
    volume: 'low',
    latency: '1-2s',
    language: 'Node.js / Python',
    protocol: 'REST',
    database: 'PostgreSQL / SQLite',
    cache: 'In-memory',
    messaging: 'Basic queues',
    deployment: 'Single server',
    minServers: 1,
    estimatedCost: 'Low',
  },
  {
    name: 'High Reliability',
    volume: 'high',
    latency: '50-200ms',
    language: 'Go / Java',
    protocol: 'gRPC',
    database: 'PostgreSQL (replicated)',
    cache: 'Redis (replicated)',
    messaging: 'Kafka (multi-broker)',
    deployment: 'Kubernetes multi-region',
    minServers: 10,
    estimatedCost: 'Very High',
  },
];
