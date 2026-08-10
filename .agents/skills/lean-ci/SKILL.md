---
name: lean-ci
description: >
  Guide for GitHub Actions workflows in this repository. Use when creating
  CI/CD pipelines, modifying build steps, or debugging CI failures.
argument-hint: "[workflow-name]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---

# Lean CI

This collection follows a "CI as thin wrapper" philosophy. GitHub Actions
workflows call ansible-lint and syntax checks — no inline shell logic.

## Principles

1. **Every CI step must be reproducible locally.** Developers run same commands.

2. **Minimal setup actions.** Only `actions/checkout`.

3. **Pin actions to commit SHAs.** Mutable tags (`@v4`) allow upstream changes
   without review. Pin to full SHA with tag comment.

4. **Use ubuntu-24.04 explicitly** rather than `ubuntu-latest`.

## Workflow Structure

CI has two workflows in `.github/workflows/`:

### ci.yml

Runs on pull requests to `devel`:

| Job | Command |
|-----|---------|
| lint | `ansible-lint` |
| syntax-check | `ansible-playbook --syntax-check playbooks/*.yml` |

### release.yml

Runs on tags:
- Builds collection with `ansible-galaxy collection build`
- Creates GitHub release

## Rules for Modifications

When adding or modifying CI:

- **DO** use SHA-pinned actions with tag comment
  ```yaml
  uses: actions/checkout@11bd719...  # v4.2.2
  ```

- **DO** set `FORCE_COLOR: 1` for readable logs

- **DO** use `ubuntu-24.04` explicitly

- **DO NOT** put multi-line shell scripts in `run:` blocks

- **DO NOT** add setup actions beyond checkout

- **DO NOT** hardcode tool versions in YAML

## Local Testing

Run CI checks locally before pushing:

```bash
# Lint
ansible-lint

# Syntax check
ansible-playbook --syntax-check playbooks/*.yml

# Build collection
ansible-galaxy collection build
```

## Debugging Failures

1. **Lint failure**: Run `ansible-lint` locally, fix violations
2. **Syntax failure**: Check YAML formatting, variable references
3. **Action failure**: Check action version compatibility

## Adding New Checks

1. Test command locally first
2. Add as simple `run:` step (one line)
3. Update this skill with new check
