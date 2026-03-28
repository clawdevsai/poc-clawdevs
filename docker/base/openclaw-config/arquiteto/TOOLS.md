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

# TOOLS.md - Architect

tools:
  - read/write
  - exec for git/gh/curl operational flow
  - sessions_list/sessions_spawn/sessions_send
  - web-search/web-read

rules:
  - validate active repository context before any gh/git action
  - use panel API for task lifecycle (create/update/list)
  - enforce SOURCE_VALIDATION.md for external-information decisions (>=3 independent sources, >=1 official source, explicit date, confidence)
  - mandatory order: docs -> commit -> panel_task -> validation -> session_finished
  - use sessions_send for agent channels (not message)
  - persist decision evidence contract: claim, sources, confidence, invalidators

routing_by_label:
  back_end: dev_backend
  front_end: dev_frontend
  mobile: dev_mobile
  tests: qa_engineer
  devops: devops_sre
  dba: dba_data_engineer
  security: security_engineer

github_permissions:
  type: read+write_limited
  allowed: ["gh pr", "gh label", "gh workflow", "gh run view"]
  denied: ["gh issue create/edit/close"]

panel_api_contract:
  required_fields: ["title", "label", "github_repo", "description"]
