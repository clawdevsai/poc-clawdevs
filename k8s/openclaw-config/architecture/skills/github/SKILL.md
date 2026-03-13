# GitHub

Use this skill when you need to interact with GitHub issues, pull requests, workflow runs, or API endpoints.

Guidelines:
- Use the `gh` CLI for all GitHub actions.
- Use `GITHUB_REPOSITORY` as the default target for all repository-scoped commands.
- Use `GITHUB_TOKEN` for authentication. If needed, export `GH_TOKEN="$GITHUB_TOKEN"` before running `gh`.
- When not inside a git repository, always pass `--repo "$GITHUB_REPOSITORY"`.
- Never hardcode `owner/repo` unless the requester explicitly asks for a different repository.
- Prefer `--json` plus `--jq` for structured, machine-friendly output.
- For issue creation from local backlog artifacts, summarize the task clearly and include source file paths.
- For labels, never send a JSON-like string as a scalar value (for example, `"[EPIC01]"`).
- With `gh issue create`, pass one `--label` per label (for example, `--label task --label P0 --label EPIC01`).
- With `gh api` to `/issues/{n}/labels`, send arrays using repeated fields (`-f labels[]=EPIC01`) or JSON input body.
- Official CLI documentation: https://cli.github.com/manual/gh

Issue examples:
```bash
gh issue list --repo "$GITHUB_REPOSITORY" --json number,title --jq '.[] | "\(.number): \(.title)"'
gh issue create --repo "$GITHUB_REPOSITORY" --title "Task: improve onboarding" --body "Derived from /data/openclaw/backlog/tasks/TASK-101-onboarding.md"
gh issue create --repo "$GITHUB_REPOSITORY" --title "Task: improve onboarding" --body "..." --label task --label P1 --label EPIC01
gh api "repos/$GITHUB_REPOSITORY/issues/123/labels" --method POST -f labels[]=EPIC01 -f labels[]=P1
```

Pull request and CI examples:
```bash
gh pr checks 55 --repo "$GITHUB_REPOSITORY"
gh run list --repo "$GITHUB_REPOSITORY" --limit 10
gh run view <run-id> --repo "$GITHUB_REPOSITORY"
gh run view <run-id> --repo "$GITHUB_REPOSITORY" --log-failed
```

API example:
```bash
gh api "repos/$GITHUB_REPOSITORY/pulls/55" --jq '.title, .state, .user.login'
```
