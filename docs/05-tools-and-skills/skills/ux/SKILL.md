---
name: ux
description: "User Experience: validate frontend, accessibility, and usability. Use `gh pr`, `gh issue` for PR review and feedback. Follow frontend design and UI/UX Pro Max guidelines."
---

# UX Skill

Validate frontend for UX/UI guidelines, accessibility, and usability. Review Developer PRs for the frontend layer. Use GitHub to view PRs, comment, and open issues for UX improvements.

## GitHub (gh CLI)

Always specify `--repo owner/repo` when not in a git directory. Use `$GITHUB_USER` for the authenticated account when applicable.

### Pull Requests

View PR diff and leave UX/accessibility comments:

```bash
gh pr view <pr-number> --repo owner/repo
gh pr checks <pr-number> --repo owner/repo
```

List PRs (e.g. open, for review):

```bash
gh pr list --repo owner/repo --state open --json number,title --jq '.[] | "\(.number): \(.title)"'
```

### Issues

Create UX/accessibility feedback issues. Identify the agent in the body:

```bash
gh issue create --repo owner/repo --title "UX: ..." --body "..."
# At end of body: — Created by [UX agent name], UX — ClawDevs
```

### API for advanced queries

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

## UX rules

- **Usability first:** Interface should explain itself; the user should not need a manual for the obvious.
- **Accessibility:** Inclusion is required, not optional.
- **Visual consistency:** Respect design system and patterns; avoid generic “AI slop” (see 23-frontend-design, 32-ui-ux-pro-max).
- **Performance vs aesthetics:** Do not increase load time by more than 10% for visual changes.
- **Heavy backend changes:** If a UX suggestion would require heavy DB/structure changes, consult the Architect first.
- **Workspace:** Clone repos to `/workspace`; never clone to system root or other folders.
