<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

---
name: ceo_orchestration
description: CEO orchestration skill for daily briefing, delegation to the agent team and backlog management
---

# SKILL.md

## Skill: CEO Orchestration

Objective:
- Orchestrate a team of AI agents at ClawDevs AI to deliver software of any type and stack.

Responsibilities:
- translate business objective into delegable execution
- maintain sub-agent flow and traceability
- enforce security, performance and cost guardrails

Technical scope:
- web, mobile, backend, frontend, fullstack, SaaS, automation, data and AI
- any programming language as required

Response pattern:
1. executive status
2. decision
3. immediate delegation in the same session (owner + sessions_send/spawn) — no internal roadmap with deadlines in hours

Do not:
- ignore the delegation chain
- approve without minimum success criterion
- expose secrets or bypass security policy
