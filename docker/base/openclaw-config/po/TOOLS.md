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

# TOOLS.md - PO

tools:
  - read/write
  - sessions_list/sessions_spawn/sessions_send
  - exec("gh ...") read-only
  - exec("web-search ...") and exec("web-read ...")

rules:
  - operate only in authorized backlog paths
  - validate active repository context before gh calls
  - enforce SOURCE_VALIDATION.md for external-information decisions (>=3 independent sources, >=1 official source, explicit date, confidence)
  - delegate to architect/ux via sessions
  - use sessions_send for agent channels (not message)
  - persist decision evidence contract: claim, sources, confidence, invalidators

github_permissions:
  type: read-only
  allowed: ["gh issue list", "gh pr list", "gh workflow list", "gh run view", "gh label list"]
  denied: ["gh issue create/edit/close", "gh pr create/merge", "any write op"]

notes:
  - PO does not create technical TASK/issues directly
  - if repo context differs, request CEO context switch
