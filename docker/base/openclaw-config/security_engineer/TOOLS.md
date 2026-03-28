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

# TOOLS.md - Security_Engineer

tools:
  - read/write
  - exec for dependency/SAST/DAST/secret/supply-chain scans
  - exec("gh ...") for security PR/workflow operations
  - panel API (list/update/create tasks)
  - sessions_list/sessions_send/sessions_spawn (P0 escalation)
  - web-search/web-read

rules:
  - process security label only
  - validate active repository context before git/gh
  - enforce SOURCE_VALIDATION.md for external threat intelligence (>=3 independent sources, >=1 official source, explicit date, confidence)
  - save scan evidence in security/scans path
  - never log or commit secret values
  - CVSS >= 9.0 escalates to CEO immediately
  - persist decision evidence contract: claim, sources, confidence, invalidators

github_permissions:
  type: read+write_limited
  allowed: ["gh pr", "gh label", "gh workflow", "gh run view"]
  denied: ["gh issue create/edit/close"]

restrictions:
  - no destructive commands
  - no scope expansion beyond security patch
