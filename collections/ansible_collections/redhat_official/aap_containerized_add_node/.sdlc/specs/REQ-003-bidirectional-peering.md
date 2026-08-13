# REQ-003: Bidirectional Peering

## Status

Implemented

## Parent

[AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069), [AAPRFE-1967](https://redhat.atlassian.net/browse/AAPRFE-1967)

## Phase

[PHASE-001](../phases/PHASE-001-initial-collection.md)

---

## Requirement

Support both peering directions:
1. **Outbound dial** (EN → Controller): Node initiates connection
2. **Inbound dial** (Controller → EN): Controller initiates connection

## Rationale

Different firewall policies require different directions:
- **Outbound**: Common, works through most firewalls, zero disruption
- **Inbound**: Required when EN has no outbound access, causes mesh disruption

## Acceptance Criteria

### Outbound Dial (Default)
- [ ] EN dials controller via `receptor_peers`
- [ ] No changes to controller receptor.conf
- [ ] Zero mesh disruption
- [ ] Works through NAT/firewalls that allow outbound

### Inbound Dial (Optional)
- [ ] Controller dials EN when `aap_add_node_enable_controller_peer=true`
- [ ] Controller receptor.conf updated with new tcp-peer
- [ ] Warning displayed about mesh disruption
- [ ] 5-10 second disruption per node documented

## Implementation

| Artifact | Description |
|----------|-------------|
| `receptor_peers` inventory var | List of peers EN dials |
| `roles/update_controller_peers/` | Updates controller receptor.conf |
| `aap_add_node_enable_controller_peer` | Opt-in flag for inbound |
| `docs/TOPOLOGY.md` | Disruption warning |

## Verification

See [TEST.md](../../TEST.md) scenarios T01 (outbound), T05 (inbound).

## Related

- ADR-003: Outbound-First Topology
