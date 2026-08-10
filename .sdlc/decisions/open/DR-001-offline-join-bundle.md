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

AAPRFE-3069 describes customers who cannot allow inbound SSH to execution nodes due to security/compliance policy:

> "Allow the controller to generate a self-contained 'join bundle' (inventory + credentials + ansible-navigator + EE) from data entered in the controller UI, which can be executed directly on the target RHEL host to join the mesh with minimal manual steps — useful for environments where the control plane cannot reach the node directly at all."

Current state:
- Collection requires SSH from installer host to execution nodes
- Some environments have strict egress-only policies on EN networks
- Manual bundle creation is error-prone and undocumented

## Impact of Not Deciding

- Air-gapped customers cannot use this collection
- Manual workarounds remain error-prone
- Partial coverage of AAPRFE-3069 requirements

---

## Options Considered

### Option A: Implement Bundle Generation in Collection

**Description**: Add `playbooks/generate_bundle.yml` that creates self-contained archive.

**Pros**:
- Supports air-gapped environments
- No SSH to EN required
- Bundle can be audited before execution

**Cons**:
- Two-phase process (generate + execute)
- Credentials in bundle require careful handling
- Bundle may be large if images included (~600MB)

**Effort**: Medium

### Option B: Document Manual Bundle Creation

**Description**: Provide documentation for manually creating bundles.

**Pros**:
- No code changes
- Users can customize for their environment

**Cons**:
- Error-prone
- Not automatable at scale
- Poor UX

**Effort**: Low

### Option C: Defer to Upstream

**Description**: Request product team implement bundle generation in Controller.

**Pros**:
- Proper UI integration
- Product-supported feature

**Cons**:
- Unknown timeline
- Customers blocked

**Effort**: None (collection scope)

---

## Recommendation

TBD — awaiting input on:
- Customer priority for this capability
- Security review of bundle credential handling
- Alignment with upstream product direction

---

## Related Artifacts

- AAPRFE-3069: Parent RFE
- ADR-001: CLI-First Approach
- DR-002: Controller UI Integration (would include bundle generation)

---

## Decision

**Status**: Open
**Date**: 
**Decided By**: 

**Decision**: [TBD]

**Rationale**: 

**Action Items**:
- [ ] Gather customer input on priority
- [ ] Security review of credential handling in bundles
- [ ] Prototype implementation if approved
