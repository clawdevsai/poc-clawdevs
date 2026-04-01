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
 * Analyze requirements and recommend tech stack
 *
 * This hook is called before implementation begins:
 * 1. Parses requirements from conversation, config, and system prompt
 * 2. Analyzes performance, reliability, and cost constraints
 * 3. Recommends optimal tech stack and patterns
 * 4. Returns architectural recommendation to guide implementation
 */
export async function beforeExecution(context: {
  conversation?: string;
  config?: Record<string, any>;
  systemPrompt?: string;
}): Promise<any> {
  // Parse requirements in cascade order
  // 1. System prompt (global constraints)
  // 2. Project config (project-specific settings)
  // 3. Conversation (task-specific requirements)

  // Return architectural recommendation
  return {
    language: 'go',
    protocol: 'grpc',
    database: 'postgresql',
    pattern: 'microservices',
    reasoning: 'Will be enhanced in Task 2.3',
  };
}
