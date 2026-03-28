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

# BOOT.md - DBA_DataEngineer

## Boot Sequence

1. Load `IDENTITY.md`.
2. Load `AGENTS.md`.
3. Read `README.md` the repository to understand the application, stack and data model before modeling.
4. Load `SOUL.md`.
5. Load `INPUT_SCHEMA.json` and validate input schema.
6. Read `/data/openclaw/memory/shared/SHARED_MEMORY.md` — apply global team standards as base context.
7. Read `/data/openclaw/memory/dba_data_engineer/MEMORY.md` — retrieve your own learning from relevant databases.
8. Validate `/data/openclaw/` and database workspace.
9. Check `active_repository.env` at `/data/openclaw/contexts/`.
10. Create working directory: `/data/openclaw/backlog/database/`.
11. Check PATH: `psql`, `flyway`, `alembic`, `prisma` available (warn if missing, do not fail).
12. When completing the session: register up to 3 learnings in `/data/openclaw/memory/dba_data_engineer/MEMORY.md`.
13. Ready to receive tasks from the Architect or Dev_Backend.

##healthcheck
- `/data/openclaw/` accessible? ✅
- INPUT_SCHEMA.json loaded? ✅
- `active_repository.env` available? ✅
- `database/` Directory created? ✅
- SHARED_MEMORY.md and MEMORY.md (dba_data_engineer) read? ✅