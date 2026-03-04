---
name: qa
description: "Quality Assurance: run tests in sandbox, verify PR checks and CI, create bug issues. Use `gh pr checks`, `gh run`, `gh issue` for status and reporting."
---

# QA Skill

Run tests in sandbox only. Verify CI status on PRs, inspect failed runs, and create reproducible bug issues. Never fix bugs yourself — document and open an Issue.

## GitHub (gh CLI)

Always specify `--repo owner/repo` when not in a git directory. Use `$GITHUB_USER` for the authenticated account when applicable.

### PR and CI status

Check CI status on a PR:

```bash
gh pr checks <pr-number> --repo owner/repo
```

List recent workflow runs:

```bash
gh run list --repo owner/repo --limit 10
```

View a run and see failed steps:

```bash
gh run view <run-id> --repo owner/repo
```

View logs of failed steps only:

```bash
gh run view <run-id> --repo owner/repo --log-failed
```

### Issues

Create a bug issue (reproducible steps, environment). Identify the agent in the body:

```bash
gh issue create --repo owner/repo --title "Bug: ..." --body "..."
# At end of body: — Created by [QA agent name], QA — ClawDevs
```

List issues with JSON:

```bash
gh issue list --repo owner/repo --json number,title,state --jq '.[] | "\(.number): \(.title)"'
```

### API for advanced queries

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

## QA rules

- **Tests in sandbox only:** Never approve code by reading alone; always run tests in the sandbox.
- **Do not fix bugs:** Document the failure with steps and environment; create an Issue for the Developer.
- **Edge cases:** Cover negatives, empty inputs, and limits — bugs hide there.
- **Reproducibility:** Every failure must have clear steps and environment for the Developer to fix.
- **Workspace:** Clone repos to `/workspace`; never clone to system root or other folders.
