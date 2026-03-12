---
name: github-cli
description: "Interact with GitHub using the gh CLI for issues, pull requests, workflow runs, and API queries. Use when an agent must inspect or update GitHub state."
---

# GitHub Skill

Use `gh` CLI for repository operations. If outside a git checkout, always pass `--repo owner/repo`.

## Issues

List open issues with JSON output:
```bash
gh issue list --repo owner/repo --state open --json number,title,url
```

Create an issue:
```bash
gh issue create --repo owner/repo --title "Title" --body "Body"
```

## Pull Requests

Check PR checks:
```bash
gh pr checks 55 --repo owner/repo
```

List workflow runs:
```bash
gh run list --repo owner/repo --limit 10
```

View failed logs:
```bash
gh run view <run-id> --repo owner/repo --log-failed
```

## API Queries

Use `gh api` for advanced fields:
```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```
