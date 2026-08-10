# DR-002: Controller UI Integration

## Status

Decided — Not Implementing

**Decision:** UI integration is out of scope. Ansible automation is the interface. See ADR-001.

## Raised By

pgriffit — 2026-08-10

## Category

Product

## Priority

Medium

---

## Question

How should UI-driven node addition be provided to customers who don't use CLI/Ansible?

## Context

AAPRFE-3069 explicitly requests:

> "Add a first-class 'add execution node' workflow (UI + CLI)"

And for air-gapped environments:

> "Allow the controller to generate a self-contained 'join bundle'... from data entered in the controller UI"

Current UI limitations:
- No "Add Node" button in Topology or Instances view
- No workflow to guide users through node addition
- No bundle generation capability
- Status reporting issues when nodes join (AAPRFE-1752)

This collection (ADR-001) addresses CLI/automation but not UI.

## Impact of Not Deciding

- Non-Ansible users have no solution
- AAPRFE-3069 only partially addressed
- Continued customer friction

---

## Options Considered

### Option A: Upstream Product Implementation

**Description**: Request AAP product team implement "Add Node" wizard in Controller UI.

**Pros**:
- Proper UX design and integration
- Product-supported feature
- Consistent with rest of AAP UI

**Cons**:
- Requires product roadmap prioritization
- Unknown timeline
- Collection team has no control

**Effort**: None (collection scope) / High (product scope)

### Option B: AAP Job Template with Survey

**Description**: Wrap collection in Job Template with survey prompts for "button-click" experience.

**Pros**:
- Works with existing AAP capabilities
- No upstream changes needed
- Users get UI-like experience

**Cons**:
- Not native UI
- Requires Job Template setup
- Limited UX customization

**Effort**: Low

### Option C: Gateway Plugin

**Description**: Build UI plugin for AAP Gateway that calls collection.

**Pros**:
- Custom UI possible
- Could integrate with existing views

**Cons**:
- Complex to build and maintain
- Gateway plugin architecture overhead
- Separate from Controller UI

**Effort**: High

### Option D: Document Status Quo

**Description**: Accept CLI-only and document for users.

**Pros**:
- No additional work

**Cons**:
- UI users blocked
- Incomplete AAPRFE-3069 coverage

**Effort**: Low

---

## Recommendation

TBD — depends on:
- Product team appetite for upstream implementation
- Customer tolerance for Job Template workaround
- Resource availability for plugin development

---

## Related Artifacts

- AAPRFE-3069: Parent RFE
- AAPRFE-1752: UI status reporting issues
- ADR-001: CLI-First Approach
- DR-001: Offline Join Bundle (bundle generation in UI)

---

## Decision

**Status**: Open
**Date**: 
**Decided By**: 

**Decision**: [TBD]

**Rationale**: 

**Action Items**:
- [ ] Engage with AAP product team on upstream prioritization
- [ ] Document Job Template workaround as interim
- [ ] Gather customer feedback on acceptable solutions
