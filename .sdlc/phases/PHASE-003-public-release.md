# PHASE-003: Public Release

## Status

Future

## Timeline

- **Target Start**: TBD
- **Target Complete**: TBD

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
- Must have an approved **Red Hat Support Exception**
- Exception covers use of this collection alongside supported AAP installation
- Without exception, collection is provided as-is (community support only)

Documentation must clearly state:
1. Collection is not officially supported by Red Hat
2. Supported usage requires Red Hat Support Exception
3. How to request a Support Exception
4. What the exception covers/doesn't cover

## Deliverables

| Artifact | Description |
|----------|-------------|
| Public repo | Change visibility to public |
| SUPPORT.md | Support model documentation |
| README update | Add support disclaimer prominently |
| GitHub Release tarball | Tag builds attach `.tar.gz` for manual handoff (`release.yml`) |
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

- PHASE-001 complete ✓
- PHASE-002 complete (or deferred)
- Legal/product approval for public release
- Support Exception template approved

## Success Criteria

- [ ] Repository publicly accessible
- [ ] Support model clearly documented
- [ ] README includes support disclaimer
- [ ] Contribution process documented for external contributors
- [ ] Branch protection enabled on main and devel
- [ ] CodeQL code scanning enabled
- [ ] Dependabot alerts enabled

## Notes

Upstream migration to `ansible.containerized_installer` (original PHASE-003 scope) is a separate track — that would make this capability officially supported without exception. This phase covers the interim public release.

Galaxy/Automation Hub publishing remains deferred/out of scope while distribution is manual customer handoff of the GitHub Release artifact.
