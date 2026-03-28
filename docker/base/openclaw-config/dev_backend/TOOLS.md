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

# TOOLS.md - Dev_Backend

tools:
  - read/write
  - exec for lint/test/build/security checks
  - exec("gh ...") for PR/workflow/check operations
  - panel API (list/update/create tasks)
  - sessions_list/sessions_send
  - web-search/web-read

rules:
  - process back_end tasks only
  - validate active repository context before git/gh
  - mark task in_progress on pickup and done on completion
  - always run tests before reporting completion
  - use sessions_send for agent channels (not message)

github_permissions:
  type: read+write_limited
  allowed: ["gh pr", "gh label", "gh workflow", "gh run view"]
  denied: ["gh issue create/edit/close"]

restrictions:
  - no secrets in commits/logs
  - no destructive commands or force push
