# PHASE-003: Public Release

## Status

Ready (PR #63 merged 2026-08-25)

## Timeline

- **Started**: 2026-08-25
- **PR Merged**: 2026-08-25
- **Target Public**: 2026-08-25 (pending final approval)

---

## Objective

Open the repository to public access and establish support model.

## Goals

1. Make repository publicly accessible on GitHub
2. Document support model and Red Hat Support Exception requirement
3. Establish contribution guidelines for external contributors
4. Ship releases via GitHub Release tarball for **manual** customer distribution (Galaxy/Automation Hub out of scope)

## Support Model

**IMPORTANT:** This collection is not part of the official AAP product.

For customers to use this in a **fully supported** fashion:
- Must have an approved **Red Hat Support Exception (SE)**
- Exception covers use of this collection alongside supported AAP installation
- Without exception, collection is provided as-is (community support only)

### Red Hat Support Exception Process

1. **Customer requests SE** via their TAM or account team
2. **SE references this collection** and specific use case (adding execution nodes without full installer re-run)
3. **Red Hat Support reviews** and approves/denies based on customer environment
4. **If approved**: Customer can open support cases referencing the SE number
5. **If denied**: Customer can still use collection but without Red Hat Support coverage

### SE Documentation Required

- SE number must be referenced in any support cases
- Customer must document which nodes were added via this collection
- Customer must maintain inventory of collection-managed vs installer-managed nodes

### Repository Documentation

Documentation must clearly state:
1. Collection is **not officially supported** by Red Hat
2. Supported usage **requires Red Hat Support Exception**
3. Link to SE request process (internal Red Hat portal or TAM contact)
4. What the exception covers (collection usage) and doesn't cover (bugs in collection code)

### README Banner (Required)

Add prominent banner at top of README:

```markdown
> **Support Notice:** This collection is not part of the official AAP product.
> For supported usage, customers must have an approved Red Hat Support Exception.
> Contact your TAM or account team to request an SE.
> Without an SE, this collection is provided as-is without Red Hat Support coverage.
```

## Distribution Model

**Decision: GitHub Releases only** — Keep it simple.

### How It Works

1. Tag a release (e.g., `git tag v1.0.0 && git push --tags`)
2. `release.yml` workflow builds collection tarball
3. Tarball attached to GitHub Release page
4. Customer downloads and installs

### Installation Methods

```bash
# Option 1: Direct from GitHub Release URL
ansible-galaxy collection install \
  https://github.com/RedHatOfficial/aap-containerized-add-node/releases/download/v1.0.0/redhat_official-aap_containerized_add_node-1.0.0.tar.gz

# Option 2: Download then install
curl -LO https://github.com/RedHatOfficial/aap-containerized-add-node/releases/download/v1.0.0/redhat_official-aap_containerized_add_node-1.0.0.tar.gz
ansible-galaxy collection install ./redhat_official-aap_containerized_add_node-1.0.0.tar.gz
```

## Deliverables

| Artifact | Description |
|----------|-------------|
| Public repo | Change visibility to public |
| SUPPORT.md | Support model documentation |
| README update | Add support disclaimer prominently |
| GitHub Release workflow | `release.yml` builds and attaches collection tarball on tag |
| Installation docs | Document download + install steps |
| CONTRIBUTING.md update | External contributor guidelines |
| Branch protection | Enable for main and devel branches |
| CodeQL | Enable GitHub Advanced Security code scanning |

### Post-Public Tasks

These require public repo (free tier doesn't support on private):

1. **Branch Protection** (Settings → Branches)
   - Require PR reviews before merge
   - Require status checks (gitleaks, lint, syntax-check, build, changelog)
   - Block force pushes
   - See `docs/BRANCH_PROTECTION.md` for full config

2. **CodeQL / GHAS** (Settings → Security)
   - Re-enable `.github/workflows/codeql.yml`
   - Enable Dependabot alerts
   - Enable secret scanning

**Out of scope:** Ansible Galaxy and Automation Hub publish — this collection is distributed manually under the Support Exception model.

## Prerequisites

- [x] PHASE-001 complete ✓
- [x] PHASE-002 complete ✓
- [x] Legal/product approval for public release ✓ (2026-08-25)
- [x] Support Exception template approved ✓

## Success Criteria (Pre-Public)

- [x] Support model clearly documented in SUPPORT.md
- [x] README includes SE banner at top
- [x] SE request process documented (TAM/account team contact)
- [x] Installation docs updated (GitHub Release download + install)
- [x] GitHub Release workflow tested (v1.0.0-rc1 validated)
- [x] Contribution process documented for external contributors
- [x] Branch protection docs prepared (.github/BRANCH_PROTECTION.md)
- [x] CodeQL workflow configured (.github/workflows/codeql.yml)
- [x] Dependency Review workflow configured
- [x] Documentation Pages workflow configured (mkdocs → GitHub Pages)
- [x] Dependabot alerts enabled
- [x] Gitleaks security scan passed
- [x] DCO sign-off verified
- [x] PR #63 merged to devel

## Success Criteria (Post-Public)

- [x] Repository visibility changed to public (2026-08-25)
- [x] Branch protection rules enabled (devel; main doesn't exist)
- [x] GitHub Pages enabled (workflow build_type)
- [x] Secret scanning enabled
- [x] Push protection enabled
- [ ] v1.0.0 release tagged and published
- [ ] Internal announcements sent (TAM/Support/PM teams)
- [ ] AAPRFE-3069 updated with public repo link

## Notes

Upstream migration to `ansible.containerized_installer` (original PHASE-003 scope) is a separate track — that would make this capability officially supported without exception. This phase covers the interim public release.

Galaxy/Automation Hub publishing remains deferred/out of scope while distribution is manual customer handoff of the GitHub Release artifact.
