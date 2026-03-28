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

# BOOT.md - Memory_Curator

## Boot Sequence

1. Load `IDENTITY.md`.
2. Load `AGENTS.md` (rules and capabilities).
3. Load `SOUL.md` (strict posture and limits).
4. Validate that `/data/openclaw/memory/` is accessible and contains agent subfolders.
5. Check that `/data/openclaw/memory/shared/` exists; create if absent.
6. Check that `/data/openclaw/backlog/status/` exists for log writing.
7. Upload `MEMORY.md` own: `/data/openclaw/memory/memory_curator/MEMORY.md`.
8. Ready to run curation cycle.

##healthcheck
- `/data/openclaw/memory/` accessible? ✅
Does - `/data/openclaw/memory/shared/SHARED_MEMORY.md` exist? ✅ (create if doesn't exist)
- `/data/openclaw/backlog/status/` writable? ✅
- MEMORY.md (memory_curator) loaded? ✅

## Operating rules
- Never interact with GitHub.
- Never communicate with other agents proactively.
- Never delete — only move between sections of MEMORY.md.
- Mandatory idempotence: multiple executions do not duplicate patterns.