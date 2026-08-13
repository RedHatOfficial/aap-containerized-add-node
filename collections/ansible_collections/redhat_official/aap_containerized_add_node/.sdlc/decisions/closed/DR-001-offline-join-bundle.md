# DR-001: Offline Join Bundle

## Status

Decided

## Raised By

pgriffit — 2026-08-10

## Category

Architecture

## Priority

High

---

## Question

Should this collection support generating self-contained "join bundles" for air-gapped execution node provisioning?

## Context

ADR-001 establishes that Ansible automation is the only interface. This DR addresses a specific gap: environments where the control host cannot SSH to execution nodes.

AAPRFE-3069 describes customers who cannot allow inbound SSH to execution nodes due to security/compliance policy:

> "Allow the controller to generate a self-contained 'join bundle'... which can be executed directly on the target RHEL host to join the mesh with minimal manual steps — useful for environments where the control plane cannot reach the node directly at all."

Current state:
- Collection requires SSH from control host to execution nodes
- Some environments have strict egress-only policies on EN networks
- No documented workaround for air-gapped scenarios

This is an automation question, not a UI question — bundle generation would be another playbook, consistent with ADR-001.

## Impact of Not Deciding

- Air-gapped customers cannot use this collection
- Partial coverage of AAPRFE-3069 requirements
- Customers must create bundles manually (error-prone)

---

## Options Considered

### Option A: Implement Bundle Generation Playbook

**Description**: Add `playbooks/generate_bundle.yml` that creates self-contained archive for offline execution.

Bundle contents:
- Pre-minted TLS certificates (signed by mesh CA)
- receptor.conf template
- Install playbook for local execution
- Optional: receptor container image

Workflow:
1. Run `generate_bundle.yml` on control host (SSH to controller only)
2. Transfer bundle to EN via approved channel (USB, SFTP, etc.)
3. Run `install.yml` locally on EN

**Pros**:
- Supports air-gapped environments
- Consistent with automation-only approach (ADR-001)
- Bundle can be audited before execution
- Pre-registers instance so heartbeat appears after local install

**Cons**:
- Two-phase process (generate + execute)
- TLS private keys in bundle require secure handling
- Bundle size ~50MB minimum, ~600MB with images

**Effort**: Medium

### Option B: Document Manual Process

**Description**: Provide step-by-step documentation for manually creating bundles.

**Pros**:
- No code changes
- Users can customize

**Cons**:
- Error-prone (7+ manual steps)
- Not automatable
- Contradicts ADR-001 philosophy

**Effort**: Low

### Option C: Out of Scope

**Description**: Air-gapped scenarios are not supported. Document limitation.

**Pros**:
- No additional work
- Clear boundary

**Cons**:
- Blocks air-gapped customers
- AAPRFE-3069 gap remains

**Effort**: None

---

## Recommendation

Option A aligns with ADR-001 (automation-only). Bundle generation is just another playbook.

---

## Related Artifacts

- AAPRFE-3069: Parent RFE
- ADR-001: Ansible Automation Only
- REQ-005: Offline Join Bundle
- PHASE-002: Offline Bundle

---

## Decision

**Status**: Decided
**Date**: 2026-08-10
**Decided By**: pgriffit

**Decision**: Option A — Implement bundle generation playbook

**Rationale**: 

Must implement with these constraints:
1. **No API/UI/platform changes** — collection only, no upstream dependencies
2. **Same approach as online** — reuse existing roles, same registration mechanics
3. **Self-contained** — bundle includes everything needed for offline execution
4. **Fully documented** — clear docs for offline prerequisites and workflow

The bundle generation is just another playbook that:
- Runs `generate_bundle.yml` with SSH to controller only (fetch CA, pre-register instance)
- Produces archive containing: TLS certs, receptor.conf, install playbook, optionally images
- User transfers bundle via approved channel
- User runs `install.yml` locally on EN (no SSH required)

Same `awx-manage` registration, same receptor install — just split into two phases.

**Constraints**:
- Bundle must work without internet access on EN
- TLS keys in bundle — document secure handling
- Images optional (user can pre-pull or include in bundle)
- No changes to Controller, Gateway, or any AAP component

**Action Items**:
- [ ] Create `playbooks/generate_bundle.yml`
- [ ] Create `roles/generate_bundle/`
- [ ] Create `playbooks/install_from_bundle.yml` (runs locally on EN)
- [ ] Document offline prerequisites in `docs/OFFLINE.md`
- [ ] Document secure bundle handling
- [ ] Test in air-gapped lab environment
