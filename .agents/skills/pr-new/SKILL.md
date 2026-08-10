---
name: pr-new
description: >
  Prepare and submit a pull request. Runs quality gates (ansible-lint),
  commits with conventional commits, creates PR via gh. Use when the user
  asks to submit, create, or open a pull request.
argument-hint: "[branch-name] [--title 'PR title']"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---

# PR New

Prepare and submit a pull request for this collection.

## Workflow

### Step 1: Create feature branch

```bash
git checkout -b <branch-name> devel
```

Use descriptive branch name (e.g., `feat/offline-bundle`, `fix/preflight-ssh`).

### Step 2: Run quality gates

```bash
ansible-lint
```

Must pass cleanly on all files.

### Step 3: Self-review the diff

```bash
git diff devel...HEAD
```

Check:
1. Does every statement mean what it says?
2. Are there security issues (credentials, injection)?
3. Would a caller be surprised?
4. Is documentation still accurate?
5. Are there unused imports or dead code?
6. Is this consistent with existing patterns?

### Step 4: Commit with conventional commits

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]
```

Types for this project:

| Type | When to use |
|------|-------------|
| `feat` | New feature (role, playbook, variable) |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructuring |
| `test` | Adding or updating tests |
| `ci` | CI/CD configuration |
| `chore` | Maintenance tasks |

Scopes: `preflight`, `register`, `receptor`, `topology`, `sdlc`

Examples:
- `feat(preflight): add registry credential check`
- `fix(register): handle HA controller correctly`
- `docs: update TOPOLOGY.md with multi-hop example`

### Step 5: Push and create PR

```bash
git push -u origin HEAD

gh pr create --title "conventional commit style title" --body "$(cat <<'EOF'
## Summary
- Concise description of what changed and why

## Changes
- List of notable changes

## Test plan
- [ ] ansible-lint passes
- [ ] Tested against AAP 2.x (specify version)
- [ ] Docs updated (if applicable)
EOF
)"
```

PR targets `devel` branch. Return PR URL to user.

### Step 6: Address review feedback

After pushing, reviewers may leave comments. Address feedback:
1. Make requested changes
2. Push new commits
3. Reply to comments
4. Re-run quality gates

## Quick Reference

| Check | Command |
|-------|---------|
| Lint | `ansible-lint` |
| Syntax | `ansible-playbook --syntax-check playbooks/*.yml` |
| Diff | `git diff devel...HEAD` |
| PR | `gh pr create` |
