# GitHub

Use this skill when you need to interact with GitHub issues, pull requests, workflow runs, or API endpoints.

Guidelines:
- Use the `gh` CLI for all GitHub actions.
- When not inside a git repository, always pass `--repo owner/repo` (or `--repo "$GITHUB_REPOSITORY"` when set).
- Prefer `--json` plus `--jq` for structured, machine-friendly output.
- For issue creation from local backlog artifacts, summarize the task clearly and include source file paths.

Issue examples:
```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
gh issue create --repo owner/repo --title "Task: improve onboarding" --body "Derived from /data/openclaw/backlog/tasks/TASK-101-onboarding.md"
```

Pull request and CI examples:
```bash
gh pr checks 55 --repo owner/repo
gh run list --repo owner/repo --limit 10
gh run view <run-id> --repo owner/repo
gh run view <run-id> --repo owner/repo --log-failed
```

API example:
```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```
