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

# Hooks Specification

## Purpose

Define the lifecycle events where plugins/agents can intercept and modify behavior. Hooks are extension points; each hook has a well-defined input, output, and execution order.

## Hook Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT EXECUTION LOOP                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. message.received  → Log, rate-limit check, auth            │
│    └─ Can modify message before processing                    │
│                                                                 │
│ 2. session.loaded    → Load user context, preferences         │
│    └─ Can inject session metadata                             │
│                                                                 │
│ 3. context.loaded    → Assemble context window                │
│    └─ Can rerank memories, filter messages                    │
│                                                                 │
│ 4. prompt.built      → System prompt assembled                │
│    └─ Can prepend standing orders or warnings                 │
│                                                                 │
│ 5. before.model      → Ready to call LLM                       │
│    └─ Can inject defense checks (prompt injection)            │
│                                                                 │
│ 6. model.response    → LLM returned response                   │
│    └─ Can validate output, check for issues                   │
│                                                                 │
│ 7. tools.available   → Tool list assembled                     │
│    └─ Can add/remove tools, validate permissions              │
│                                                                 │
│ 8. tool.selected     → Agent chose a tool to call             │
│    └─ Can validate tool call, log intent                      │
│                                                                 │
│ 9. tool.executed     → Tool returned result                    │
│    └─ Can sanitize result, check for errors                   │
│                                                                 │
│ 10. response.ready   → Final response assembled               │
│     └─ Can scrub secrets, add footer, etc                     │
│                                                                 │
│ 11. response.sent    → Response sent to user                   │
│     └─ Can log, notify, update metrics                        │
│                                                                 │
│ 12. session.saved    → Session persisted                       │
│     └─ Can post-process, archive, cleanup                     │
│                                                                 │
│ 13. error.occurred   → Exception or error                      │
│     └─ Can log, escalate, retry, fallback                     │
└─────────────────────────────────────────────────────────────────┘
```

## Hook Definitions

### 1. message.received

**When**: User sends message to agent via any channel

**Input**:
```json
{
  "message_id": "msg_123456",
  "content": "string",
  "channel": "telegram|whatsapp|discord|api",
  "user_id": "user_12345",
  "timestamp": "2026-03-31T10:00:00Z"
}
```

**Output**: Modified message or null (to reject)

**Handlers**:
- `log-to-database`: Log all messages
- `rate-limit-check`: Enforce per-channel rate limits
- `auth-check`: Verify user is authenticated
- `spam-filter`: Detect spam/abuse patterns
- `content-filter`: Block inappropriate content

**Order**: Executed in sequence; if any rejects, stop

---

### 2. session.loaded

**When**: Session retrieved from storage

**Input**:
```json
{
  "session_id": "user:12345",
  "created_at": "2026-01-01T00:00:00Z",
  "message_count": 150,
  "memory_entries": 25
}
```

**Output**: Modified session metadata

**Handlers**:
- `inject-user-preferences`: Add user's stored preferences
- `load-workspace-context`: Load active project info
- `check-session-health`: Verify session not corrupted

---

### 3. context.loaded

**When**: Context engine assembled the context window

**Input**:
```json
{
  "total_available_tokens": 500000,
  "context_window_tokens": 80000,
  "selected_messages": 20,
  "selected_memories": 5,
  "artifacts": ["file1.md", "file2.yaml"]
}
```

**Output**: Modified context or metadata

**Handlers**:
- `rerank-memories`: Adjust memory relevance scores
- `filter-sensitive`: Remove PII before passing to LLM
- `add-context-metadata`: Inject timestamps, sources
- `optimize-for-latency`: Reduce context size if needed

---

### 4. prompt.built

**When**: System prompt assembled from agent config

**Input**:
```json
{
  "system_prompt": "string (full system prompt)",
  "agent_name": "dev_backend",
  "skills": ["skill1", "skill2"],
  "standing_orders": [...]
}
```

**Output**: Modified system prompt

**Handlers**:
- `inject-constitution`: Prepend CONSTITUTION constraints
- `add-standing-orders`: Inject daily standing orders
- `add-security-footer`: Add security/safety reminders

---

### 5. before.model

**When**: Ready to call LLM; final validation before inference

**Input**:
```json
{
  "model": "claude-opus-4",
  "prompt_tokens": 45000,
  "max_output_tokens": 4096,
  "temperature": 0.7
}
```

**Output**: Modified parameters or reject (throw error)

**Handlers**:
- `prompt-injection-defense`: Check for injection attempts
- `token-usage-check`: Verify under quota
- `model-override`: Switch model if needed (cost optimization)
- `security-validation`: Final security checks

---

### 6. model.response

**When**: LLM returned text response

**Input**:
```json
{
  "response": "string (raw LLM output)",
  "completion_tokens": 2500,
  "total_tokens": 47500,
  "finish_reason": "stop|length|error"
}
```

**Output**: Validated response (may modify)

**Handlers**:
- `validate-response`: Check response isn't malformed
- `check-hallucination`: Look for obvious errors
- `extract-confidence`: Add confidence scores

---

### 7. tools.available

**When**: Tool list assembled from plugins

**Input**:
```json
{
  "tools": [
    {
      "name": "create_github_issue",
      "plugin": "github-integration",
      "requires_auth": true
    },
    ...
  ]
}
```

**Output**: Filtered/modified tool list

**Handlers**:
- `check-permissions`: Verify agent can use each tool
- `validate-plugin-health`: Check plugins are healthy
- `cost-optimization`: Remove expensive tools if under quota

---

### 8. tool.selected

**When**: Agent chose which tool to invoke

**Input**:
```json
{
  "tool_name": "create_github_issue",
  "parameters": {...},
  "confidence": 0.95
}
```

**Output**: Validated tool call (may reject)

**Handlers**:
- `validate-parameters`: Check parameters are valid
- `log-tool-call`: Log which tool, what params
- `ask-confirmation`: For destructive tools, ask first
- `cost-check`: Verify tool execution won't exceed budget

---

### 9. tool.executed

**When**: Tool returned result (success or error)

**Input**:
```json
{
  "tool_name": "create_github_issue",
  "status": "success|error|timeout",
  "result": {...},
  "duration_ms": 1234,
  "cost": 0.001,
  "result_size_bytes": 142000
}
```

**Output**: Processed result (may modify, compressed)

**Handlers**:
- `context-mode-compress`: **[NEW]** Compress large outputs (>5KB) via ctx_execute
  - Detects output size
  - If >5KB: filters/summarizes output (99% compression)
  - Returns compressed result to agent context
  - Reduces tokens: 142KB → 3KB
  - Examples: `npm list` (142KB→3KB), `git log` (315KB→2KB), `gh pr list` (280KB→5KB)
- `sanitize-result`: Remove PII/secrets from result
- `error-handling`: Log errors, trigger retries
- `update-metrics`: Track API usage, costs, compression ratio

**Context Mode Impact**:
- **Before**: Tool outputs consume 70% of context window
- **After**: Compressed outputs consume <5% of context window
- **Monthly Cost Reduction**: ~$562 (97% reduction)

---

### 10. response.ready

**When**: Final response assembled, ready to send to user

**Input**:
```json
{
  "response": "string",
  "response_length": 1500,
  "tools_used": ["create_github_issue"],
  "total_tokens_used": 47500
}
```

**Output**: Final response to send

**Handlers**:
- `scrub-secrets`: Remove any exposed keys
- `scrub-prompts`: Remove system prompts if leaked
- `add-footer`: Add attribution, feedback links
- `add-metrics`: Add token counts, costs
- `truncate-if-needed`: Ensure response fits channel limits

---

### 11. response.sent

**When**: Response delivered to user

**Input**:
```json
{
  "response_id": "resp_123456",
  "sent_to_user": "user:12345",
  "channel": "telegram",
  "sent_timestamp": "2026-03-31T10:00:05Z"
}
```

**Output**: None (for logging only)

**Handlers**:
- `log-response`: Store response in database
- `update-metrics`: Track response time, quality
- `notify-observers`: Alert monitoring systems
- `queue-follow-ups`: Schedule follow-up tasks

---

### 12. session.saved

**When**: Session persisted to storage

**Input**:
```json
{
  "session_id": "user:12345",
  "messages_added": 2,
  "memories_updated": 1,
  "size_bytes": 125000
}
```

**Output**: None (for post-processing)

**Handlers**:
- `post-process`: Update indices, cache
- `backup`: Create backup of session
- `archive-if-old`: Move to archive if old
- `cleanup`: Remove temp files

---

### 13. error.occurred

**When**: Any error during execution

**Input**:
```json
{
  "error_type": "timeout|permission|validation|api_error",
  "message": "string",
  "context": {...},
  "retry_count": 0,
  "timestamp": "2026-03-31T10:00:05Z"
}
```

**Output**: Action (retry, fallback, escalate)

**Handlers**:
- `log-error`: Store error with context
- `retry-logic`: Decide if/how to retry
- `escalate`: Notify supervisor if critical
- `fallback`: Use degraded mode if applicable

---

## Hook Configuration

```yaml
hooks:
  # Hook execution order (earlier = first)
  execution_order:
    - message.received     # 100
    - session.loaded       # 200
    - context.loaded       # 300
    - prompt.built         # 400
    - before.model         # 500
    - model.response       # 600
    - tools.available      # 700
    - tool.selected        # 800
    - tool.executed        # 900
    - response.ready       # 1000
    - response.sent        # 1100
    - session.saved        # 1200
    - error.occurred       # 9999 (always last)

  # Hook timeout
  timeout_ms: 5000        # Kill hook if takes > 5s

  # If hook fails
  on_failure: "continue" # "stop" | "fallback" | "log_only"

  # Log all hook executions
  log_hooks: true

  # Per-hook configuration
  hooks:
    message.received:
      handlers:
        - plugin: "rate-limiter"
          timeout_ms: 100
        - plugin: "auth-validator"
          timeout_ms: 500

    before.model:
      handlers:
        - plugin: "prompt-injection-defense"
          timeout_ms: 1000
        - plugin: "token-usage-monitor"
          timeout_ms: 100

    tool.executed:
      handlers:
        - plugin: "context-mode-compress"
          timeout_ms: 3000
          config:
            enabled: true
            threshold_bytes: 5120      # Compress if > 5KB
            compression_target: 0.05   # Aim for 5% of original size
            keep_first_lines: 10
            keep_last_lines: 30
        - plugin: "sanitize-result"
          timeout_ms: 1000
        - plugin: "error-logger"
          timeout_ms: 500

    error.occurred:
      handlers:
        - plugin: "error-logger"
          timeout_ms: 100
        - plugin: "escalation-handler"
          timeout_ms: 500
```

## Monitoring Hooks

```bash
# Show hook execution metrics
openclaw hooks metrics --period 24h

# Show hooks registered
openclaw hooks list --agent dev_backend

# Show hook latency
openclaw hooks latency --hook before.model --percentile 95

# Audit hook executions
openclaw hooks audit --hook prompt-injection-defense --days 7
```

## Best Practices

1. **Keep hooks fast**: < 1s total time per hook
2. **Don't modify too much**: Hooks should validate, not rewrite
3. **Log everything**: Easy debugging if issues arise
4. **Test hooks**: Verify behavior with test cases
5. **Order matters**: Hooks execute in defined order
6. **Handle failures**: What if a hook fails?
7. **Monitor latency**: Track if hooks slow down execution

