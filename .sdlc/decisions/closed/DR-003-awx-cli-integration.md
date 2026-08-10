# DR-003: awx-cli Integration

## Status

Decided — Not Implementing

**Decision:** Separate CLI tool would duplicate automation. Ansible collection covers CLI use case. See ADR-001.

## Raised By

pgriffit — 2026-08-10

## Category

Architecture

## Priority

Medium

---

## Question

Should we propose upstream additions to `awx-manage` or the AWX API to enable native CLI-driven node addition?

## Context

AAPRFE-3069 requests a CLI-native "add node" command. Currently:

- `awx` CLI has no `add-node` or `provision-instance` command
- Users must use `awx-manage` via SSH/podman exec (4+ sequential commands)
- No API endpoint exposes the provision_instance workflow

The collection wraps these commands but requires Ansible. Some users want simpler CLI access.

## Impact of Not Deciding

- Collection remains the only automation option
- Non-Ansible users must run multiple awx-manage commands manually
- No standard API for third-party tooling

---

## Options Considered

### Option A: Propose awx-manage Wrapper Command

**Description**: Contribute `awx-manage add_execution_node` to ansible/awx that wraps the 4+ command sequence.

**Pros**:
- Single command UX
- No API changes needed
- Backward compatible

**Cons**:
- Still requires SSH to controller
- Contribution process overhead

**Effort**: Medium

### Option B: Propose API Endpoint

**Description**: Contribute `/api/v2/instances/provision/` endpoint to AWX.

**Pros**:
- Standard REST API access
- Token auth (no SSH)
- Enables `awx` CLI integration

**Cons**:
- Larger upstream change
- API design considerations
- Longer review cycle

**Effort**: High

### Option C: Both (Phased)

**Description**: Start with awx-manage command (Option A), then propose API (Option B).

**Pros**:
- Incremental value delivery
- awx-manage is lower friction to merge
- API can follow proven awx-manage design

**Cons**:
- Two upstream contributions
- More total effort

**Effort**: Medium + High

### Option D: Accept Collection-Only

**Description**: Document that Ansible collection is the supported path.

**Pros**:
- No upstream work
- Clear ownership boundary

**Cons**:
- Non-Ansible users unsatisfied
- AAPRFE-3069 gap remains

**Effort**: None

---

## Recommendation

TBD — depends on:
- Upstream AWX maintainer appetite for these additions
- Community interest in contributing
- Customer priority for non-Ansible CLI

---

## Related Artifacts

- AAPRFE-3069: Parent RFE
- ADR-001: CLI-First Approach
- ansible/awx: Upstream repository

---

## Decision

**Status**: Open
**Date**: 
**Decided By**: 

**Decision**: [TBD]

**Rationale**: 

**Action Items**:
- [ ] Review AWX contribution guidelines
- [ ] Draft awx-manage command proposal
- [ ] Engage with AWX maintainers on feasibility
