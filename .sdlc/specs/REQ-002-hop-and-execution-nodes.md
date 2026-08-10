# REQ-002: Hop and Execution Node Support

## Status

Implemented

## Parent

[AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069)

## Phase

[PHASE-001](../phases/PHASE-001-initial-collection.md)

---

## Requirement

Support both **execution nodes** and **hop nodes** in the same collection and playbook.

## Rationale

Enterprise deployments use:
- **Execution nodes**: Run jobs, need capacity
- **Hop nodes**: Relay traffic, enable DMZ traversal

Both share receptor install mechanics but differ in registration (`node_type`).

## Acceptance Criteria

- [ ] `receptor_type=execution` registers as execution node with capacity
- [ ] `receptor_type=hop` registers as hop node (relay only)
- [ ] Both types use same playbook entry point
- [ ] Hop nodes show `capacity=0` in list_instances
- [ ] Mixed inventory (hops + execution) works in single run

## Implementation

| Artifact | Description |
|----------|-------------|
| `receptor_type` inventory var | `execution` (default) or `hop` |
| `roles/register_instance/` | Passes `--node-type` to provision_instance |
| `roles/install_receptor_node/` | Same install for both types |

## Verification

See [TEST.md](../../TEST.md) scenarios T04 (hop), T06 (mixed).

## Related

- docs/TOPOLOGY.md: Multi-hop patterns
