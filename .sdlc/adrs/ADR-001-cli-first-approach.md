# ADR-001: Ansible Automation Only

## Status

Accepted

## Date

2026-08-10

## Context

AAPRFE-3069 requests workflows for adding execution nodes post-install. The RFE consolidates customer pain points around manual, error-prone processes that don't scale.

Key observations:
- The underlying operations (awx-manage, receptor install) are already automation tasks
- Customers adding nodes at scale (28+ environments, 100K+ managed nodes) need scriptable solutions
- Manual CLI commands don't scale and are error-prone (AAPRFE-1752 required 7 manual steps)
- UI workflows add administrative overhead without enabling automation

## Decision

**We will provide Ansible automation only. No UI. No separate CLI tool.**

This is a deliberate design choice to:
1. Minimize administrative tasks through automation
2. Enable integration with existing automation pipelines
3. Avoid duplication between CLI and automation
4. Match how customers actually deploy at scale

The collection:
1. Wraps existing awx-manage commands in idempotent roles
2. Uses the same `ansible.containerized_installer` roles as the official installer
3. Operates on the standard installer inventory format
4. Provides preflight validation to catch errors early
5. Supports parallel node addition with serialized DB registration

## Alternatives Considered

### Alternative 1: Add UI Workflow

**Description**: Build or request "Add Node" wizard in Controller UI.

**Pros**:
- Accessible to non-automation users

**Cons**:
- Adds administrative overhead
- Not scriptable for scale deployments
- Duplicates automation capability

**Why not chosen**: UI doesn't solve the scale problem. Customers with 28+ environments need automation, not clicks.

### Alternative 2: Build Separate CLI Tool

**Description**: Create `aap-add-node` CLI binary alongside collection.

**Pros**:
- Simple one-off usage

**Cons**:
- Duplicates collection functionality
- Two tools to maintain
- CLI still not scriptable like Ansible

**Why not chosen**: Ansible automation already covers CLI use cases without duplication. Running a playbook is equivalent effort to running a CLI command.

### Alternative 3: Propose awx-manage Additions

**Description**: Add `awx-manage add_execution_node` upstream.

**Pros**:
- Native to AAP

**Cons**:
- Still requires SSH to controller
- Still manual (not automated)
- Upstream contribution overhead

**Why not chosen**: Doesn't improve on collection approach. Automation is the answer, not more CLI commands.

## Consequences

### Positive

- Single automation path — no confusion between UI/CLI/automation
- Scriptable for customers with many isolated environments
- Integrates with existing Ansible workflows and CI/CD
- No upstream dependencies
- No duplication to maintain

### Negative

- Requires Ansible knowledge (appropriate for AAP users)

### Neutral

- Users wanting "button-click" can wrap in AAP Job Template with Survey

## Implementation Notes

- Collection is the interface; no other interfaces planned
- Job Template + Survey provides UI-like experience if needed
- Documentation emphasizes automation-first approach

## Related Decisions

- DR-001: Offline Join Bundle (still requires decision — different concern)

## References

- [AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069)
- [AAPRFE-1752](https://redhat.atlassian.net/browse/AAPRFE-1752) (7 manual steps problem)
- [AAPRFE-1967](https://redhat.atlassian.net/browse/AAPRFE-1967) (outbound-only requirement)

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-08-10 | pgriffit | Initial proposal |
| 2026-08-10 | pgriffit | Revised: Automation-only is design choice, not gap |
