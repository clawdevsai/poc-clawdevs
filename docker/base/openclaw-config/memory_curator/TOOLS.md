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

# TOOLS.md - Memory_Curator

## available_tools
- `read(path)`: Read agents MEMORY.md and SHARED_MEMORY.md. Validate that path starts with `/data/openclaw/memory/` and does not contain `..`.
- `write(path, content)`: Write to agent MEMORY.md (move patterns to Archived) and to SHARED_MEMORY.md (add global patterns). Validate schema before persisting.
- `exec("tail -n 100 /data/openclaw/backlog/status/memory-curator.log")`: Consult the log of the previous cycle.

## usage_rules
- `read` and `write` only on `/data/openclaw/memory/**`.
- Never delete lines from MEMORY.md — only move between sections (`Active Patterns` → `Archived`).
- Never write to an agent workspace outside of `/data/openclaw/memory/`.
- Never write to `/data/openclaw/backlog/` except to the log file: `/data/openclaw/backlog/status/memory-curator.log`.
- Never interact with GitHub API (`gh`, `git`, etc.).
- Idempotent operation: running twice should produce the same result as running once.

## paths_autorizados
- Agent reading: `/data/openclaw/memory/<id>/MEMORY.md`
  - Allowed IDs: `ceo`, `po`, `arquiteto`, `dev_backend`, `dev_frontend`, `dev_mobile`, `qa_engineer`, `security_engineer`, `devops_sre`, `ux_designer`, `dba_data_engineer`, `memory_curator`
- Writing shared: `/data/openclaw/memory/shared/SHARED_MEMORY.md`
- Log: `/data/openclaw/backlog/status/memory-curator.log`

## prohibitions
- Without `sessions_spawn`, `sessions_send` or `sessions_list` — does not communicate with other agents
- Without `exec("gh ...")` or any GitHub operations
- No writing outside of `/data/openclaw/memory/`