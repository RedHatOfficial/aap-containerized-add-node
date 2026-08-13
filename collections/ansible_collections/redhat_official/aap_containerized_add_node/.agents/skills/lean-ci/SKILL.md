---
name: lean-ci
description: >
  Guide for GitHub Actions workflows in this repository. Use when creating
  CI/CD pipelines, modifying build steps, or debugging CI failures.
argument-hint: "[workflow-name]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.2.0
---

# Lean CI

This collection follows a "CI as thin wrapper" philosophy. GitHub Actions
workflows call ansible-lint and syntax checks — no inline shell logic.

Distribution is **manual** (customer handoff of the collection tarball). Do
**not** add Ansible Galaxy or Automation Hub publish steps.

## Principles

1. **Every CI step must be reproducible locally.** Developers run same commands.

2. **Minimal setup actions.** Prefer `actions/checkout` plus `actions/setup-python`
   only when pip install is required.

3. **Pin actions to commit SHAs.** Mutable tags (`@v4`) allow upstream changes
   without review. Pin to full SHA with tag comment.

4. **Use ubuntu-24.04 explicitly** rather than `ubuntu-latest`.

## Workflow Structure

CI has two workflows in `.github/workflows/`:

### ci.yml

Runs on push/PR to `main` and `devel`:

| Job | Command |
|-----|---------|
| changelog | PR only: `.github/scripts/validate_changelog.py` (skip with `skip-changelog` label) |
| lint | `yamllint .` then `ansible-lint` |
| syntax-check | install collection, then `ansible-playbook --syntax-check` on `playbooks/*.yml` |
| build | `ansible-galaxy collection build` and upload `.tar.gz` artifact |

Required status checks (see `.github/BRANCH_PROTECTION.md`): `changelog`, `lint`, `syntax-check`, `build`.

### release.yml

Runs on tags matching `v*`:

- Builds collection with `ansible-galaxy collection build`
- Creates a **GitHub Release** and attaches the `.tar.gz` for manual customer distribution
- Does **not** publish to Ansible Galaxy or Automation Hub

## Changelog fragments

- Source of truth: `changelogs/fragments/*.yml` → generated `CHANGELOG.rst`
- `CHANGELOG.md` is a pointer only — do not duplicate release notes there
- PRs that modify `roles/` or `playbooks/` must add a fragment (or use `skip-changelog`)

## Rules for Modifications

When adding or modifying CI:

- **DO** use SHA-pinned actions with tag comment
  ```yaml
  uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
  ```

- **DO** set `FORCE_COLOR: 1` for readable logs

- **DO** use `ubuntu-24.04` explicitly

- **DO NOT** put multi-line shell scripts in `run:` blocks

- **DO NOT** hardcode tool versions in YAML beyond what setup-python needs

- **DO NOT** add Galaxy or Automation Hub publish jobs

## Local Testing

Run CI checks locally before pushing:

```bash
# Lint
yamllint .
ansible-lint

# Changelog (against devel; requires fetch of origin/devel)
python3 .github/scripts/validate_changelog.py --ref devel

# Syntax check (install collection first)
ansible-galaxy collection install -r requirements.yml
ansible-galaxy collection install . --force
for playbook in playbooks/*.yml; do
  ansible-playbook "$playbook" --syntax-check
done

# Build collection
ansible-galaxy collection build
```

## Debugging Failures

1. **Changelog failure**: Add `changelogs/fragments/<name>.yml`, or label `skip-changelog` when appropriate
2. **Lint failure**: Run `ansible-lint` / `yamllint` locally, fix violations
3. **Syntax failure**: Check YAML formatting, variable references, FQCNs
4. **Build failure**: Check `galaxy.yml` and `build_ignore`
5. **Action failure**: Check action version compatibility

## Adding New Checks

1. Test command locally first
2. Add as simple `run:` step (one line)
3. Update this skill with new check
