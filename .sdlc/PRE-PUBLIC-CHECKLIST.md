# Pre-Public Release Checklist

**Target**: Make aap-containerized-add-node repository public

**Phase**: PHASE-003 preparation

**Date Started**: 2026-08-25

---

## Critical Blockers (Must Complete Before Public)

### Documentation

- [ ] **Create SUPPORT.md** — Document Support Exception (SE) requirement
  - [ ] Explain SE process (contact TAM/account team)
  - [ ] State collection is not officially supported without SE
  - [ ] Link to internal SE request process or TAM contact info
  - [ ] Document what SE covers and doesn't cover
  - [ ] Document SE number requirement for support cases

- [ ] **Add Support Notice Banner to README.md** — Top of file after badges
  ```markdown
  > **Support Notice:** This collection is not part of the official AAP product.
  > For supported usage, customers must have an approved Red Hat Support Exception.
  > Contact your TAM or account team to request an SE.
  > Without an SE, this collection is provided as-is without Red Hat Support coverage.
  ```

- [ ] **Update Installation Docs** — Add GitHub Release download method
  - [ ] Update docs/INSTALL.md with GitHub Release URL installation
  - [ ] Update docs/QUICKSTART.md with GitHub Release method
  - [ ] Add both installation methods:
    - Direct URL: `ansible-galaxy collection install https://github.com/...`
    - Download then install: `curl -LO ... && ansible-galaxy collection install`

### Testing & Validation

- [ ] **Test GitHub Release Workflow** — Verify tarball build
  - [ ] Create test tag (e.g., `v1.0.0-rc1`)
  - [ ] Verify `.github/workflows/release.yml` triggers
  - [ ] Verify tarball is built and attached to release
  - [ ] Verify tarball installs correctly: `ansible-galaxy collection install <tarball-url>`
  - [ ] Delete test tag after validation

- [ ] **Final Security Scan** — No secrets/credentials
  - [ ] Run gitleaks: `git secrets --scan` or equivalent
  - [ ] Manual review of examples/ for any leftover tokens/passwords
  - [ ] Verify add_node.secrets.yml is template only (no real credentials)
  - [ ] Check .gitignore covers .ignore/, *.vault, *.secret

- [ ] **Final CI/CD Check** — All workflows passing
  - [x] ~~CI workflow (lint, syntax-check, build, changelog, gitleaks)~~
  - [x] ~~CodeQL security scanning~~
  - [x] ~~Dependency Review~~
  - [x] ~~DCO Check~~
  - [x] ~~Documentation build~~
  - [ ] Release workflow tested (see above)

### Legal & Compliance

- [ ] **Legal Review** — Approval to open-source
  - [ ] Product management approval
  - [ ] Legal team approval for public release
  - [ ] Confirm GPL-3.0-or-later license is appropriate
  - [ ] Verify all contributors have signed DCO (Developer Certificate of Origin)

- [ ] **License Headers** — Check source files
  - [ ] Verify LICENSE file is present (already exists: GPL-3.0-or-later)
  - [ ] Check if role files need license headers (consult legal)

### Contribution Hygiene

- [ ] **Review CONTRIBUTING.md** — External contributor guidance
  - [x] ~~DCO requirement documented~~
  - [x] ~~PR process documented~~
  - [ ] Verify contribution workflow is clear for external users
  - [ ] Add note about SE requirement for supported usage

- [ ] **Review CODE_OF_CONDUCT.md** — Community standards
  - [x] ~~Already exists~~
  - [ ] Verify contact info is correct for violations

- [ ] **Review SECURITY.md** — Vulnerability reporting
  - [x] ~~Already exists~~
  - [ ] Verify secalert@redhat.com is correct contact
  - [ ] Verify PGP key link is current

---

## Post-Public Tasks (Do After Repository is Public)

These tasks **require** the repository to be public (free tier GitHub limitations).

### GitHub Settings

- [ ] **Enable Branch Protection Rules**
  - [ ] `main` branch protection (see `.github/BRANCH_PROTECTION.md`)
    - [ ] Require PR reviews (1 approval)
    - [ ] Require status checks: changelog, lint, syntax-check, build
    - [ ] Require linear history (squash merge only)
    - [ ] Require Code Owners review
    - [ ] Block force pushes
  - [ ] `devel` branch protection
    - [ ] Require PR reviews (1 approval)
    - [ ] Require status checks: changelog, lint, syntax-check, build
    - [ ] Require linear history

- [ ] **Enable GitHub Advanced Security Features**
  - [x] ~~Dependabot alerts (already enabled)~~
  - [x] ~~Dependabot security updates (already enabled)~~
  - [ ] Secret scanning (enable after public)
  - [ ] Push protection for secrets (enable after public)
  - [x] ~~CodeQL code scanning (already configured)~~

- [ ] **Repository Settings Verification**
  - [ ] Settings → General → Features:
    - [ ] Issues enabled
    - [ ] Discussions disabled (or enabled if desired)
    - [ ] Projects disabled (or enabled if desired)
  - [ ] Settings → General → Pull Requests:
    - [ ] Allow squash merging: **enabled**
    - [ ] Allow merge commits: **disabled**
    - [ ] Allow rebase merging: **disabled**
    - [ ] Automatically delete head branches: **enabled**
  - [ ] Settings → Code security and analysis:
    - [ ] Review all security features enabled

### Community Files

- [ ] **Create CHANGELOG for v1.0.0** — First public release
  - [ ] Summarize all features from PHASE-001
  - [ ] Document supported platforms (AAP 2.6+, RHEL 9/10)
  - [ ] Document limitations (SSH access, air-gap bundle pending)

- [ ] **Tag v1.0.0 Release**
  - [ ] Ensure CHANGELOG.rst is up to date
  - [ ] Tag: `git tag -a v1.0.0 -m "Initial public release"`
  - [ ] Push tag: `git push origin v1.0.0`
  - [ ] Verify GitHub Release created with tarball
  - [ ] Edit GitHub Release notes if needed

### Announcement & Communication

- [ ] **Internal Announcement** — Notify Red Hat teams
  - [ ] Notify TAM/account teams about SE requirement
  - [ ] Notify Support team about SE coverage model
  - [ ] Notify PM team (AAPRFE-3069 stakeholders)
  - [ ] Update AAPRFE-3069 JIRA with public repo link

- [ ] **External Announcement** (Optional)
  - [ ] Blog post or community announcement
  - [ ] Link in AAP community forums
  - [ ] Link in relevant documentation

---

## Recommended (Nice-to-Have)

### Documentation Enhancements

- [ ] **Add Video Tutorial** — YouTube or Red Hat portal
  - [ ] Screen recording: basic EN addition walkthrough
  - [ ] Link from README.md and docs/QUICKSTART.md

- [ ] **Add Architecture Diagrams** — Visual topology examples
  - [ ] Outbound dial topology diagram
  - [ ] Inbound dial topology diagram
  - [ ] Multi-hop chain diagram
  - [ ] Embed in docs/TOPOLOGY.md or docs/ARCHITECTURE.md

- [ ] **Add FAQ Section** — Common customer questions
  - [ ] When to use this vs full installer?
  - [ ] Does this work with AAP Operator?
  - [ ] Can I add nodes while jobs are running?
  - [ ] What happens if playbook fails mid-join?

### Quality Enhancements

- [ ] **Add Integration Tests** — Molecule or similar
  - [ ] Test basic EN addition (AAP 2.6)
  - [ ] Test basic EN addition (AAP 2.7)
  - [ ] Test hop node addition
  - [ ] Test EN via hop
  - [ ] Test failure/retry scenarios

- [ ] **Performance Testing** — Large-scale validation
  - [ ] Test adding 10+ nodes simultaneously
  - [ ] Test adding 100+ nodes sequentially
  - [ ] Document performance characteristics in docs/

- [ ] **Add More Examples** — Cover edge cases
  - [ ] IPv6-only mesh
  - [ ] BYO TLS certificates (REQ-007)
  - [ ] Custom firewall configurations
  - [ ] Air-gapped/offline bundle (PHASE-002)

### Observability

- [ ] **Add Metrics/Telemetry** (if permitted)
  - [ ] Anonymous usage stats (opt-in)
  - [ ] Failure rate tracking
  - [ ] Platform version distribution

---

## Current Status Summary

### ✅ Already Complete

- CI/CD workflows (lint, syntax-check, build, changelog, gitleaks, CodeQL)
- Dependabot alerts and auto-updates
- Issue templates (bug report, feature request)
- Pull request template
- CODE_OF_CONDUCT.md
- SECURITY.md
- CONTRIBUTING.md (with DCO requirement)
- LICENSE (GPL-3.0-or-later)
- README.md (comprehensive but missing SE banner)
- Release workflow (.github/workflows/release.yml)
- Comprehensive examples/ (11 inventory patterns)
- Documentation (INSTALL.md, QUICKSTART.md, TROUBLESHOOTING.md, etc.)
- SDLC artifacts (.sdlc/ with ADRs, REQs, phases)
- Test plan (TEST.md)
- All PHASE-001 requirements implemented

### ❌ Missing (Blockers)

1. **SUPPORT.md** — Critical: Document SE requirement and process
2. **README.md SE banner** — Critical: Support notice at top
3. **Installation docs update** — Add GitHub Release download method
4. **Release workflow testing** — Verify tarball build works
5. **Legal/product approval** — Confirm OK to open-source
6. **Final security review** — Ensure no secrets committed

### ⏳ Post-Public Only

- Branch protection rules (requires public repo on free tier)
- Secret scanning / push protection (requires public repo)

---

## Next Steps

1. **Create SUPPORT.md** (blocking)
2. **Add SE banner to README.md** (blocking)
3. **Update installation docs** with GitHub Release method (blocking)
4. **Test release workflow** with RC tag (blocking)
5. **Get legal/product approval** (blocking)
6. **Final security scan** (blocking)
7. **Make repository public** (after all blockers cleared)
8. **Configure branch protection** (immediately after public)
9. **Tag v1.0.0 release** (after public + branch protection)
10. **Announce internally** (after v1.0.0 tagged)

---

## Notes

- PHASE-002 (offline bundle) is optional for initial public release
- PHASE-003 upstream migration is separate long-term goal
- Galaxy/Automation Hub publish is out of scope (manual GitHub Release distribution)
- SE requirement is non-negotiable for Red Hat Support coverage
