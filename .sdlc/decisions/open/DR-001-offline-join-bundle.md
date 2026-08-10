# DR-001: Offline Join Bundle

## Status

Open

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

ADR-001 establishes that Ansible automation is the only interface. This DR addresses a specific gap: environments where the installer host cannot SSH to execution nodes.

AAPRFE-3069 describes customers who cannot allow inbound SSH to execution nodes due to security/compliance policy:

> "Allow the controller to generate a self-contained 'join bundle'... which can be executed directly on the target RHEL host to join the mesh with minimal manual steps — useful for environments where the control plane cannot reach the node directly at all."

Current state:
- Collection requires SSH from installer host to execution nodes
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
1. Run `generate_bundle.yml` on installer host (SSH to controller only)
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

Pending:
- Security review of credential handling in bundles
- Customer validation of two-phase workflow

---

## Related Artifacts

- AAPRFE-3069: Parent RFE
- ADR-001: Ansible Automation Only

---

## Decision

**Status**: Open
**Date**: 
**Decided By**: 

**Decision**: [TBD]

**Rationale**: 

**Action Items**:
- [ ] Security review of TLS key handling in bundles
- [ ] Customer feedback on two-phase workflow acceptability
- [ ] Prototype if approved
