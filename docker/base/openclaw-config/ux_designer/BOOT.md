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

# BOOT.md - UX_Designer

## Boot Sequence

1. Load `IDENTITY.md`.
2. Load `AGENTS.md` (rules, capabilities and validations).
3. Read `README.md` the repository to understand the product, target users, and platforms.
4. Load `SOUL.md`.
5. Load `INPUT_SCHEMA.json` and validate input schema.
6. Read `/data/openclaw/memory/shared/SHARED_MEMORY.md` — apply global team standards as base context.
7. Read `/data/openclaw/memory/ux_designer/MEMORY.md` — retrieve your own relevant UX learnings.
8. Validate `/data/openclaw/` and design workspace.
9. Check `active_repository.env` at `/data/openclaw/contexts/`.
10. Create working directory: `/data/openclaw/backlog/ux/`.
11. When completing the session: register up to 3 learnings in `/data/openclaw/memory/ux_designer/MEMORY.md`.
12. Ready to receive delegation from the PO.

##healthcheck
- `/data/openclaw/` accessible? ✅
- INPUT_SCHEMA.json loaded? ✅
- `active_repository.env` available? ✅
- `ux/` Directory created? ✅
- SHARED_MEMORY.md and MEMORY.md (ux_designer) read? ✅