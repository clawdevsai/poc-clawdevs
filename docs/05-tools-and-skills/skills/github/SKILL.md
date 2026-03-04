---
name: github
description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries. DevOps: create repos with `gh repo create`, verify before claiming success, clone in /workspace/repos/."
---

# GitHub Skill

Use the `gh` CLI to interact with GitHub. Always specify `--repo owner/repo` when not in a git directory, or use `$GITHUB_USER` for the authenticated account (e.g. `--repo $GITHUB_USER/repo-name`). Never expose tokens in chat, logs, or repo.

## Pull Requests

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

## API for advanced queries

Use `gh api` for data not available in high-level subcommands:

```bash
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'
```

## JSON output

Most commands support `--json`; use `--jq` to filter:

```bash
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```

---

## DevOps: creating repositories (organization)

**Organization:** Repos are created under the **organization** clawdevs.ai (slug `$GITHUB_ORG` = clawdevs-ai). The authenticated user (`$GITHUB_USER` = clawdevsai) is Owner of this org. See `GITHUB-CONTEXT.md` in the workspace for full org data.

**Create repo in org:**

```bash
gh repo create $GITHUB_ORG/<nome-repo> --private --description="..." --clone=false
```

If `gh` fails, use the org API:

```bash
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/orgs/$GITHUB_ORG/repos -d '{"name":"<nome-repo>","private":true,"description":"..."}'
```

**Verify before claiming success:** Always check the exec output. Only tell the user the repo was created if the output indicates success. On error, report the exact error text and do not claim success.

**Optional confirmation:** Run `gh repo view $GITHUB_ORG/<nome-repo>` or `gh repo list $GITHUB_ORG --limit 5` after creating.

**Clone path (mandatory):** Always clone into `/workspace/repos/<nome-repo>`. Clone to `/tmp` then move to avoid 9P issues:

```bash
git clone https://x-access-token:$GITHUB_TOKEN@github.com/$GITHUB_ORG/<nome-repo>.git /tmp/<nome-repo> && mv /tmp/<nome-repo> /workspace/repos/<nome-repo>
```

**Link to user:** Use the organization URL: `https://github.com/$GITHUB_ORG/<nome-repo>`. Example: `https://github.com/clawdevs-ai/user-api`. Never use placeholders.

**After adding files:** Run `cd /workspace/repos/<nome-repo> && git add -A && git commit -m "..." && git push` and always report the result (success or error message) to the user.

**Org restriction error handling:** If output contains `organization has enabled OAuth App access restrictions` (HTTP 403), stop and report that exact error to the user. Ask to approve GitHub CLI in org settings (`Settings -> Third-party access -> GitHub CLI -> Grant access`) or remove restrictions. Do not proceed to clone/commit in this case. **Note (2026-03-04):** this restriction was removed by the org owner; the current policy is "No restrictions".

---

## Identification in history

When creating issues, PRs, or comments on GitHub, identify the agent in the body (e.g. at the end): `— Created by Sérgio, DevOps/SRE — ClawDevs`.
