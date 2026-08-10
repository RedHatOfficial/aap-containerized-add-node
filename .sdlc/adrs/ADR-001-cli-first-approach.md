# ADR-001: CLI-First Approach

## Status

Accepted

## Date

2026-08-10

## Context

AAPRFE-3069 requests both UI-driven and CLI-driven workflows for adding execution nodes. The RFE consolidates customer pain points around manual, error-prone processes that don't scale.

- UI integration requires upstream Controller changes (new views, API endpoints)
- Customers need a solution now, not after a product release cycle
- The underlying operations (awx-manage, receptor install) are already CLI-based
- Ansible collections are the standard automation pattern for AAP operations

## Decision

**We will implement as an Ansible collection first, deferring UI integration to upstream product work.**

The collection:
1. Wraps existing awx-manage commands in idempotent roles
2. Uses the same `ansible.containerized_installer` roles as the official installer
3. Operates on the standard installer inventory format
4. Provides preflight validation to catch errors early
5. Supports parallel node addition with serialized DB registration

## Alternatives Considered

### Alternative 1: Wait for Upstream UI Support

**Description**: Do nothing until AAP product team implements native UI.

**Pros**:
- Fully integrated solution
- No separate tooling to maintain

**Cons**:
- Unknown timeline
- Customers blocked in the meantime

**Why not chosen**: Customer need is immediate; product roadmap uncertain.

### Alternative 2: Build Standalone CLI Tool

**Description**: Create a dedicated `aap-add-node` CLI binary.

**Pros**:
- Simple user experience
- No Ansible knowledge required

**Cons**:
- Duplicates installer infrastructure
- Separate maintenance burden
- Not aligned with AAP automation patterns

**Why not chosen**: Ansible collection is the standard pattern and reuses existing installer roles.

## Consequences

### Positive

- Immediately usable by customers with Ansible skills
- Scriptable for customers with many isolated environments
- Can be integrated into existing automation pipelines
- No upstream product dependencies for initial release

### Negative

- Not accessible to users who only use the UI
- Requires Ansible knowledge to operate
- No single-click "add node" experience

## Related Decisions

- DR-002: Controller UI Integration (gap)
- DR-003: awx-cli Integration (gap)

## References

- [AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069)
- [AAPRFE-1752](https://redhat.atlassian.net/browse/AAPRFE-1752) (consolidated)
- [AAPRFE-1967](https://redhat.atlassian.net/browse/AAPRFE-1967) (consolidated)

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-08-10 | pgriffit | Initial proposal and acceptance |
