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
- [x] AAP 2.6.x containerized — tested
- [x] AAP 2.7.x containerized — tested
- [x] AAP 2.5 and earlier — out of scope (documented)
- [x] RPM installs — out of scope (documented)
- [x] OpenShift — out of scope (documented)

### Node OS Versions
- [x] RHEL 9.x execution nodes — tested
- [x] RHEL 9.x hop nodes — tested
- [x] RHEL 10.x execution nodes — tested (S-001; EN-via-HN on aap27)
- [x] RHEL 10.x hop nodes — tested (T-27-AIO-EN-VIA-HN, aap27-hn-02, 2026-08-10)
- [ ] Other Linux — not tested, may work

### Controller OS
- [x] Controller on RHEL 9 — tested (aap26 lab)
- [x] Controller on RHEL 10 — tested (aap27 lab, RHEL 10.2)

## Implementation

| Artifact | Description |
|----------|-------------|
| `meta/runtime.yml` | Ansible version requirements |
| `galaxy.yml` | Collection metadata |
| CHANGELOG.rst | Tested versions documented |

## Test Matrix

| AAP | Controller OS | Node OS | Status |
|-----|---------------|---------|--------|
| 2.6.x | RHEL 9.x | RHEL 9.x | Tested (aap26) |
| 2.7.x | RHEL 10.x | RHEL 9.x | Tested (aap27 EN-VIA-HN, 2026-08-10) |
| 2.7.1 | (lab) | RHEL 10.x EN | Tested (S-001 single EN) |
| 2.7.x | RHEL 10.x | RHEL 10.x HN+EN | Tested (aap27 EN-VIA-HN, hn-02/en-02, 2026-08-10) |

## Verification

See [TEST.md](../../TEST.md) — run against each matrix combination.

## Related

- INSTALLER_PLAN.md: Version targets for upstream
