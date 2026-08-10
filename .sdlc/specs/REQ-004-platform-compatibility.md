# REQ-004: Platform Compatibility

## Status

Implemented

## Parent

[AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069)

## Phase

[PHASE-001](../phases/PHASE-001-initial-collection.md)

---

## Requirement

Support AAP **2.6+** with both **RHEL 9** and **RHEL 10** execution/hop nodes.

## Rationale

- AAP 2.6 is current GA release
- AAP 2.7 is upcoming (first target for upstream migration)
- RHEL 9 is current production standard
- RHEL 10 is emerging for new deployments

Collection must work across this matrix.

## Acceptance Criteria

### AAP Versions
- [ ] AAP 2.6.x containerized — tested
- [ ] AAP 2.7.x containerized — tested
- [ ] AAP 2.5 — out of scope (documented)
- [ ] RPM installs — out of scope (documented)
- [ ] OpenShift — out of scope (documented)

### Node OS Versions
- [ ] RHEL 9.x execution nodes — tested
- [ ] RHEL 9.x hop nodes — tested
- [ ] RHEL 10.x execution nodes — tested
- [ ] RHEL 10.x hop nodes — tested
- [ ] Other Linux — not tested, may work

### Controller OS
- [ ] Controller on RHEL 9 — tested
- [ ] Controller on RHEL 10 — follows AAP support matrix

## Implementation

| Artifact | Description |
|----------|-------------|
| `meta/runtime.yml` | Ansible version requirements |
| `galaxy.yml` | Collection metadata |
| CHANGELOG.md | Tested versions documented |

## Test Matrix

| AAP | Controller OS | Node OS | Status |
|-----|---------------|---------|--------|
| 2.7.1 | RHEL 9.x | RHEL 9.x | Tested |
| 2.7.1 | RHEL 9.x | RHEL 10.0 | Tested |
| 2.6.x | RHEL 9.x | RHEL 9.x | Tested |

## Verification

See [TEST.md](../../TEST.md) — run against each matrix combination.

## Related

- INSTALLER_PLAN.md: Version targets for upstream
