# Branch Protection Setup

Configure these settings in GitHub repository Settings → Branches → Branch protection rules.

## Main Branch (`main`)

Create rule for `main`:

### Protect matching branches

- [x] **Require a pull request before merging**
  - [x] Require approvals: 1
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners

- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - Required checks:
    - `gitleaks`
    - `lint`
    - `syntax-check`
    - `build`
    - `changelog`

- [x] **Require conversation resolution before merging**

- [x] **Require signed commits**

- [x] **Do not allow bypassing the above settings**

- [x] **Restrict who can push to matching branches**
  - Add: `RedHatOfficial/aap-containerized-add-node-maintainers`

### Rules applied to everyone including administrators

- [x] **Block force pushes**
- [x] **Block deletions**

## Devel Branch (`devel`)

Same as main, but:
- Require approvals: 1 (can be self-approved by maintainers)
- Allow bypassing for maintainers (for urgent fixes)

## Setup Commands (gh CLI)

```bash
# Main branch protection
gh api repos/RedHatOfficial/aap-containerized-add-node/branches/main/protection \
  -X PUT \
  -H "Accept: application/vnd.github+json" \
  -f required_status_checks='{"strict":true,"contexts":["gitleaks","lint","syntax-check","build","changelog"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
  -f restrictions=null \
  -f required_signatures=true \
  -f allow_force_pushes=false \
  -f allow_deletions=false
```
