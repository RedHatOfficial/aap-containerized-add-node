# Branch Protection Settings

Configure these settings when the repository is made public.

## `main` Branch (Production)

Settings → Branches → Add rule → `main`

- [x] **Require a pull request before merging**
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Required checks: `lint`, `syntax-check`, `build`
- [x] **Require linear history** (no merge commits)
- [x] **Do not allow bypassing the above settings**
- [ ] Do not allow force pushes
- [ ] Do not allow deletions

## `devel` Branch (Development)

Settings → Branches → Add rule → `devel`

- [x] **Require a pull request before merging**
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Required checks: `lint`, `syntax-check`, `build`
- [x] **Require linear history**
- [ ] Do not allow force pushes
- [ ] Do not allow deletions

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
