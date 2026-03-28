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

# Multi-Repo Coordination

> Guidelines for managing changes across multiple repositories in a coordinated manner.

## Overview

When a change in one repository impacts dependent repositories, agents MUST coordinate the changes to ensure consistency and avoid breaking builds.

## Repository Dependency Graph

Example structure:
```
frontend (depends on) → backend (depends on) → shared-lib
                                           → database-migrations
mobile (depends on) → backend-api
```

## Coordination Rules

### 1. Impact Analysis
Before implementing any task, agents MUST:
1. Identify all repositories that might be affected
2. Check for API changes that could break consumers
3. Check for shared code/dependencies that might need updating

### 2. Change Ordering
Changes MUST be applied in dependency order:
1. **First:** Shared libraries, database migrations
2. **Second:** Backend/API services
3. **Third:** Frontend/Consumer applications

### 3. PR Coordination
For cross-repo changes:
1. Create PRs in dependency order
2. Link related PRs in descriptions
3. Mark dependent PRs as "blocked" until dependencies merge
4. Use "depends-on:" prefix in PR titles

### 4. Version Management
- Use semantic versioning for API changes
- Document breaking changes in CHANGELOG.md
- Update dependency versions in package.json/Cargo.toml

## Implementation Workflow

### Step 1: Analyze Impact
```
Given: New feature requiring API change
When: Agent receives task
Then: 
  - Check which repos consume this API
  - Identify required changes in each repo
  - Create coordinated plan
```

### Step 2: Execute in Order
1. Update shared library/database
2. Update backend to use new shared code
3. Update frontend to use new API
4. Run integration tests

### Step 3: Coordinate PRs
- Create PR for shared library first
- Wait for merge or approval
- Create dependent PRs
- Link PRs using GitHub keywords:
  - `Closes #123`
  - `Depends on #456`
  - `Related to #789`

## Communication Protocol

### Agent-to-Agent Handoff
When Dev_Backend completes an API change:
1. Update SPEC.md with API contract
2. Notify Dev_Frontend via Control Panel
3. Mark related tasks as "ready for pickup"

### Status Updates
All cross-repo changes MUST log:
- Repository: [repo-name]
- Change type: [api-break/config/dep]
- Dependent repos: [list]
- PR link: [url]

## Example: Adding New Field to API

### Task: Add `user.avatar_url` to backend

1. **Dev_Backend:**
   - Add field to database model
   - Update API endpoint to return field
   - Create PR: `feat(api): add avatar_url to user endpoint`

2. **Dev_Frontend:**
   - Update TypeScript types
   - Update UI to display avatar
   - Create PR: `feat(ui): display user avatar`
   - In PR description: `Depends on: #123` (backend PR)

3. **QA_Engineer:**
   - Test integration between frontend and backend
   - Verify no breaking changes

## GitHub Organization

- Default org: Configured via `GIT_ORG` env var
- All repos must be in the same org for automatic coordination
- Use GitHub Teams for permission management

## Tools

- `gh` CLI for PR creation and management
- Control Panel for task coordination
- OpenClaw for agent handoffs

## Anti-Patterns

- **NEVER** merge breaking changes without coordination
- **NEVER** skip impact analysis for "small" changes
- **NEVER** create dependent PRs before dependency PRs
- **NEVER** update frontend before backend API is stable
