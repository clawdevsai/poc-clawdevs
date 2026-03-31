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

# Channel privacy (groups vs direct)

## Purpose

Persistent memory (`MEMORY.md` under `/data/openclaw/memory/<agent>/`, `SHARED_MEMORY.md`, and memory-search tools) can contain names, internal URLs, tactical details, and cross-agent learnings. **Multi-party channels** (Telegram groups/supergroups, shared Slack channels, or any context where people beyond a single trusted DM audience can read the reply) must not receive raw memory payloads.

## Rules

1. **Identify audience risk**  
   If the runtime or message context indicates `group`, `supergroup`, `channel`, or equivalent multi-party chat, treat the thread as **Group mode**. When unsure, assume Group mode for any Telegram binding that is not a confirmed 1:1 DM with an allowlisted operator.

2. **Group mode — strict**  
   - Do **not** paste file contents or long quotes from `MEMORY.md`, `SHARED_MEMORY.md`, workspace `MEMORY.md` symlinks, or memory search / RAG tool results.  
   - Do **not** stream “here is what I remember” dumps or bullet lists copied from memory files.  
   - You may use memory **silently** to decide tone, facts, and next steps, then answer in **short paraphrase** with only information that is safe if leaked to everyone in the room.  
   - Redact: credentials, tokens, internal hostnames, private individuals, security findings not cleared for broadcast, and unreleased product detail.

3. **Direct / trusted 1:1 (confirmed DM)**  
   - Still **never** dump full memory files by default.  
   - You may include slightly more specific detail when the operator clearly needs it, but respect the Red Lines in `AGENTS.md` (no secrets, no system-internals exfiltration).

4. **CEO / Telegram entrypoint**  
   The default Telegram binding often reaches a **group**. Assume Group mode unless the adapter explicitly marks the chat as a private DM. When the Director needs sensitive detail, offer to continue in a private channel or to reference project artifacts under `/data/openclaw/projects/...` instead of memory files.

## Workspace context bundle (audit)

Every agent workspace under `openclaw-config/<agent>/` ships **SOUL.md** and **TOOLS.md**; the seed for long-term memory lives under `openclaw-config/memory/<agent>/MEMORY.md` and is copied to `/data/openclaw/memory/<agent>/MEMORY.md` on first run; `workspace-<agent>/MEMORY.md` is a symlink to that canonical file (`07-agent-workspaces.sh`). **AGENTS.md** is the runtime contract; **TOOLS.md** bounds automation; **SOUL.md** is identity. Keep this trio aligned when editing any agent profile.

| Agent id | SOUL | TOOLS | MEMORY seed |
|----------|------|-------|-------------|
| ceo | yes | yes | yes |
| po | yes | yes | yes |
| arquiteto | yes | yes | yes |
| dev_backend | yes | yes | yes |
| dev_frontend | yes | yes | yes |
| dev_mobile | yes | yes | yes |
| qa_engineer | yes | yes | yes |
| devops_sre | yes | yes | yes |
| security_engineer | yes | yes | yes |
| ux_designer | yes | yes | yes |
| dba_data_engineer | yes | yes | yes |
| memory_curator | yes | yes | yes |
