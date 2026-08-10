# ADR-004: Installer Role Reuse

## Status

Accepted

## Date

2026-08-10

## Context

AAP containerized installer (`ansible.containerized_installer`) contains battle-tested roles for:
- Container image handling
- Receptor configuration
- TLS certificate generation
- Podman quadlet setup

Duplicating this logic means maintaining parallel implementations that drift.

## Decision

**Reuse installer roles via `aap_setup_dir` and `ANSIBLE_COLLECTIONS_PATH`.**

```yaml
environment:
  ANSIBLE_COLLECTIONS_PATH: "{{ aap_setup_dir }}/collections:{{ lookup('env', 'ANSIBLE_COLLECTIONS_PATH') }}"
```

Collection reads images from `bundle/` directory when `bundle_install: true`.

Roles used from installer:
- `common` — base container setup
- `receptor` — receptor configuration
- Image loading from bundle

## Alternatives Considered

### Alternative 1: Standalone Implementation

**Description**: Rewrite all logic in this collection.

**Pros**:
- No external dependency
- Full control

**Cons**:
- Duplicated maintenance
- Version drift risk
- Miss installer bug fixes

**Why not chosen**: Installer roles are well-tested, maintained, and version-matched.

### Alternative 2: Require Collection Install

**Description**: `ansible-galaxy collection install ansible.containerized_installer`.

**Pros**:
- Standard dependency mechanism

**Cons**:
- Collection not publicly available
- Version mismatch with `aap_setup_dir`
- Extra install step

**Why not chosen**: `aap_setup_dir` already contains version-matched collection.

## Consequences

### Positive

- Version parity with installer
- Benefit from upstream fixes
- Reduced maintenance burden
- Consistent behavior

### Negative

- Requires `aap_setup_dir` to be present
- Couples to installer structure

### Neutral

- Users already have `aap_setup_dir` from initial install

## Implementation

- `playbooks/add_node.yml:68,110` — sets `ANSIBLE_COLLECTIONS_PATH`
- `validate_setup_dir` role — verifies structure exists
- `bundle_dir` variable — points to image location

## References

- `ansible.containerized_installer` collection structure
- AAP installation documentation

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-08-10 | pgriffit | Initial — documenting existing implementation |
