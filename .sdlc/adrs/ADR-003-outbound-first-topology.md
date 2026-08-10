# ADR-003: Outbound-First Topology

## Status

Accepted

## Date

2026-08-10

## Context

Mesh nodes can connect in two directions:
1. **Outbound**: EN dials controller (`tcp-peer` on EN, `tcp-listener` on controller)
2. **Inbound**: Controller dials EN (`tcp-listener` on EN, `tcp-peer` on controller)

Inbound requires restarting controller receptor, causing 5-10 second mesh disruption per node. Running jobs may fail.

Most customer firewalls allow outbound from EN to controller (standard automation pattern).

## Decision

**Default to outbound dial (EN → Controller). Zero mesh disruption.**

Nodes define `receptor_peers` in inventory — list of hostnames they dial out to:

```yaml
execution_nodes:
  hosts:
    new-en-01:
      receptor_peers:
        - controller.example.com
```

Inbound dial available via `aap_add_node_enable_controller_peer: true` but explicitly warns about disruption.

## Alternatives Considered

### Alternative 1: Inbound-First (Controller → EN)

**Description**: Controller dials all nodes.

**Pros**:
- Simpler inventory (no `receptor_peers` needed)

**Cons**:
- Mesh disruption on every add
- Requires maintenance window
- Controller becomes single point of failure for dial-out

**Why not chosen**: Disruption unacceptable for day-2 operations.

### Alternative 2: Auto-Detect Based on Firewall

**Description**: Probe connectivity and choose direction automatically.

**Pros**:
- User doesn't need to understand topology

**Cons**:
- Complex probing logic
- May guess wrong
- Hard to debug when it fails

**Why not chosen**: Explicit is better than implicit for infrastructure decisions.

## Consequences

### Positive

- Zero disruption when adding nodes
- No maintenance window required
- Matches common firewall patterns (outbound allowed)
- Explicit topology in inventory

### Negative

- Users must understand `receptor_peers` concept
- Inbound-only environments need opt-in flag

### Neutral

- Both directions supported — user chooses

## Implementation

- `receptor_peers` variable on execution nodes
- `update_controller_peers` role (opt-in, warns about disruption)
- `playbooks/add_node.yml:114-123`

## References

- AAPRFE-1967: Outbound-only requirement
- `docs/TOPOLOGY.md`: Full topology documentation

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2026-08-10 | pgriffit | Initial — documenting existing implementation |
