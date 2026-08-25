# Branch Protection Settings

**Configure these settings IMMEDIATELY after making the repository public.**

Branch protection ensures all code changes go through pull requests from forks. Direct pushes to `main` and `devel` are blocked - contributors MUST fork and submit PRs.

## `main` Branch (Production)

Settings → Branches → Add rule → `main`

- [x] **Require a pull request before merging**
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Required checks: `changelog`, `lint`, `syntax-check`, `build`, `gitleaks`, `dco`
- [x] **Require linear history** (no merge commits - squash only)
- [x] **Restrict who can push to matching branches** (maintainers only)
- [x] **Do not allow bypassing the above settings**
- [x] **Block force pushes** (prevent history rewriting)
- [ ] Allow deletions (optional - typically disabled)

## `devel` Branch (Development)

Settings → Branches → Add rule → `devel`

- [x] **Require a pull request before merging**
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Required checks: `changelog`, `lint`, `syntax-check`, `build`, `gitleaks`, `dco`
- [x] **Require linear history** (squash merge only)
- [x] **Restrict who can push to matching branches** (maintainers only)
- [x] **Block force pushes**
- [ ] Allow deletions (optional - typically disabled)

## Repository Settings

Settings → General:

- [x] **Automatically delete head branches** after PR merge
- [ ] **Allow merge commits** (disabled - use squash only)
- [x] **Allow squash merging** (default)
- [ ] **Allow rebase merging** (disabled)

Settings → Code security and analysis:

- [x] **Dependabot alerts**
- [x] **Dependabot security updates**
- [x] **Secret scanning**
- [x] **Push protection** (blocks commits with secrets)

## Tag Protection

Settings → Tags → Add rule:

- Pattern: `v*`
- Restrict who can create: Maintainers only
- Allow **GitHub Actions** to create matching tags so `release_collection.yml` can publish `vX.Y.Z` with `GITHUB_TOKEN` (avoids a second run of `release.yml`). Optional `GH_WORKFLOW_KEY` is for `release/*` branch push and the devel PR only.

---

## How Branch Protection Works

### For External Contributors (Public)

1. **Fork** the repository to your GitHub account
2. **Clone** your fork locally
3. **Create** feature branch from `devel`
4. **Make changes** and commit (with DCO sign-off)
5. **Push** to your fork
6. **Open PR** from your fork to `RedHatOfficial/aap-containerized-add-node:devel`
7. CI checks run automatically
8. Maintainer reviews and approves
9. Maintainer squash-merges (or you squash before merge)

### For Maintainers (Internal)

- **Cannot push directly** to `main` or `devel`
- Must create feature branches
- Must submit PR
- Must get approval from another maintainer
- Cannot bypass status checks
- Cannot force push

### Why This Matters

- **Quality gate**: All changes reviewed before merge
- **Audit trail**: Every change traceable via PR
- **CI validation**: Lint, tests, security scans run on every PR
- **DCO enforcement**: All commits must be signed off
- **No accidents**: Cannot accidentally push to protected branches

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contributor workflow.
