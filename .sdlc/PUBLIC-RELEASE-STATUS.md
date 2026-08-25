# Public Release Status

**Last Updated**: 2026-08-25 09:38 AM

**Current Repo State**: Private

---

## ✅ COMPLETED (Ready for Public)

### Documentation
- [x] **SUPPORT.md created** — SE requirement, request process, coverage scope documented
- [x] **README.md SE banner added** — Support notice at top after badges
- [x] **Installation docs updated**:
  - [x] docs/INSTALL.md — GitHub Release install methods
  - [x] docs/QUICKSTART.md — GitHub Release install methods
  - [x] Both methods documented (direct URL + download/install)

### Security
- [x] **Gitleaks scan passed** — No secrets detected (scanned 481 KB in 73ms)
- [x] **Secrets template verified** — examples/add_node.secrets.yml is template only
- [x] **.gitignore verified** — Covers *.vault, secrets.yml, .env, .ignore/

### CI/CD
- [x] **All workflows passing**:
  - [x] CI (lint, syntax-check, build, changelog, gitleaks)
  - [x] CodeQL security scanning (now explicitly configured)
  - [x] Dependency Review (now explicitly configured)
  - [x] DCO Check
  - [x] Documentation build (now deploys to GitHub Pages)
- [x] **Release workflow exists** — `.github/workflows/release.yml` configured
- [x] **Dependabot configured** — Auto-updates and security alerts enabled
- [x] **GitHub Pages configured** — mkdocs site deploys on main branch push

### Repository Files
- [x] **LICENSE** — GPL-3.0-or-later
- [x] **CODE_OF_CONDUCT.md** — Community standards
- [x] **SECURITY.md** — Vulnerability reporting (secalert@redhat.com)
- [x] **CONTRIBUTING.md** — DCO requirement, PR process
- [x] **Issue templates** — Bug report, feature request (YAML + MD)
- [x] **PR template** — Checklist for contributors
- [x] **CODEOWNERS** — Review requirements
- [x] **Branch protection docs** — `.github/BRANCH_PROTECTION.md`

### Collection Quality
- [x] **11 inventory examples** — Cover all topology patterns
- [x] **13 roles implemented** — All PHASE-001 requirements complete
- [x] **Comprehensive documentation**:
  - [x] INSTALL.md, QUICKSTART.md, TROUBLESHOOTING.md
  - [x] ARCHITECTURE.md, TOPOLOGY.md, CONVENTIONS.md
  - [x] COLLECTION_MAP.md, FINDINGS.md
- [x] **SDLC artifacts** — ADRs, REQs, test plan, phase tracking
- [x] **Lab validated** — AAP 2.6 AIO, 2.7 AIO, 2.7 HA cluster

---

## ❌ CRITICAL BLOCKERS (Must Complete Before Public)

### Legal & Approval
- [x] **Product management approval** — ✅ General agreement from delivery PMs (2026-08-25)
- [x] **Legal team approval** — ✅ GPL-3.0-or-later acceptable (coordinated 2026-08-25)
- [x] **DCO verification** — ✅ Contributors signed Developer Certificate of Origin
  - Contributors: Phil Griffiths (@pgriffit), Lenny Shirley (@lennysh)
  - Verified: 2026-08-25

### Testing
- [x] **Release workflow test** — ✅ Workflow tested successfully (2026-08-25 08:42 AM)
  - [x] RC tag created and pushed → workflow triggered
  - [x] GitHub Release created with tarball (362 KB)
  - [x] Tarball downloaded via gh CLI
  - [x] Collection installed successfully from local tarball
  - [x] Verified: `redhat_official.aap_containerized_add_node 1.0.0`
  - [x] RC tag and release deleted (cleanup complete)
  
  **Note**: Direct URL install from private repo returns 404 (expected). Once repo is public, URL install will work:
  ```bash
  ansible-galaxy collection install \
    https://github.com/RedHatOfficial/aap-containerized-add-node/releases/download/v1.0.0/redhat_official-aap_containerized_add_node-1.0.0.tar.gz
  ```

### Minor Documentation Review
- [ ] **CONTRIBUTING.md** — Add note about SE requirement for supported usage
- [ ] **CODE_OF_CONDUCT.md** — Verify contact info for violations
- [ ] **SECURITY.md** — Verify secalert@redhat.com contact + PGP key link current

---

## ⏳ POST-PUBLIC TASKS (Do Immediately After Public)

**These require public repo** (free tier GitHub limitations):

### Immediate (Within 1 Hour)
1. [ ] **Enable Branch Protection** — Settings → Branches
   - [ ] `main` branch: 1 approval, status checks, linear history, CODEOWNERS, no force push
   - [ ] `devel` branch: 1 approval, status checks, linear history
   - See `.github/BRANCH_PROTECTION.md` for exact configuration

2. [ ] **Enable Secret Scanning** — Settings → Security
   - [ ] Secret scanning: enable
   - [ ] Push protection: enable

3. [ ] **Verify Repository Settings** — Settings → General
   - [ ] Issues: enabled
   - [ ] Squash merge: enabled (only)
   - [ ] Merge commits: disabled
   - [ ] Rebase merge: disabled
   - [ ] Auto-delete head branches: enabled

### Same Day
4. [ ] **Tag v1.0.0 Release**
   ```bash
   git tag -a v1.0.0 -m "Initial public release"
   git push origin v1.0.0
   gh release view v1.0.0  # Verify created
   ```

5. [ ] **Update CHANGELOG.rst** — Document v1.0.0 features
   - Summarize PHASE-001 deliverables
   - Document supported platforms (AAP 2.6+, RHEL 9/10)
   - Document limitations

6. [ ] **Enable GitHub Pages** — Settings → Pages
   - [ ] Source: GitHub Actions
   - [ ] Verify mkdocs site deployed to https://redhatofficial.github.io/aap-containerized-add-node/

### Same Week
7. [ ] **Internal Announcements**
   - [ ] Notify TAM/account teams (SE requirement + how to request)
   - [ ] Notify Support team (SE coverage model)
   - [ ] Notify PM team (AAPRFE-3069 stakeholders)
   - [ ] Update AAPRFE-3069 JIRA with public repo link
   - [ ] Share GitHub Pages documentation site URL

---

## 🎯 RECOMMENDED (Nice-to-Have)

### Documentation Enhancements
- [ ] Video tutorial (basic EN addition walkthrough)
- [ ] Architecture diagrams (outbound/inbound/multi-hop topologies)
- [ ] FAQ section (vs full installer, Operator support, job impact, failure recovery)

### Quality Enhancements
- [ ] Integration tests (Molecule)
- [ ] Performance testing (10+ nodes, 100+ nodes)
- [ ] IPv6 examples
- [ ] BYO TLS examples (REQ-007)

---

## 📊 PROGRESS SUMMARY

| Category | Status |
|----------|--------|
| **Documentation** | ✅ 100% (3/3 critical items) |
| **Security** | ✅ 100% (3/3 items) |
| **CI/CD** | ✅ 100% (6/6 items) |
| **Legal & Approval** | ✅ 100% (3/3 items) |
| **Testing** | ✅ 100% (1/1 items) |
| **Minor Reviews** | ⚠️ 0% (0/3 — non-blocking) |
| **Overall Pre-Public** | ✅ **100%** (15/15 critical items) |

---

## 🚦 GO/NO-GO DECISION

### Current State: **GO** ✅

**All Blocking Issues Resolved**:
1. ✅ Legal/product approval obtained (2026-08-25)
2. ✅ Release workflow tested successfully (2026-08-25 08:42 AM)
3. ✅ DCO signatures verified

**All Critical Requirements Met**:
1. ✅ Legal/PM approval received
2. ✅ Release workflow tested successfully with RC tag
3. ✅ DCO signatures verified for all contributors
4. ⚠️ Minor doc reviews pending (recommended but not blocking)

**Ready to Make Public**: Yes — all critical blockers cleared

---

## 📝 NEXT ACTIONS (Priority Order)

1. **Get approvals** — Contact PM and legal for formal OK
2. **Test release workflow** — Create RC tag, verify tarball, install test
3. **Verify DCO signatures** — Check git log for sign-offs
4. **Minor doc review** — Update CONTRIBUTING, verify CODE_OF_CONDUCT/SECURITY contacts
5. **Stage commit** — Commit SUPPORT.md, README.md, docs updates
6. **Wait for approvals** — Do not proceed until legal/PM OK received
7. **Make public** — Change repo visibility to public
8. **Immediate post-public** — Branch protection, secret scanning, v1.0.0 tag
9. **Same-day announcements** — Notify internal teams

---

## 🔗 RESOURCES

- **Full Checklist**: `.sdlc/PRE-PUBLIC-CHECKLIST.md`
- **Branch Protection Config**: `.github/BRANCH_PROTECTION.md`
- **Phase 3 Plan**: `.sdlc/phases/PHASE-003-public-release.md`
- **Support Model**: `SUPPORT.md`
- **AAPRFE**: https://redhat.atlassian.net/browse/AAPRFE-3069

---

**Decision Point**: Obtain legal/PM approval before proceeding. Release workflow test can run in parallel while waiting.
