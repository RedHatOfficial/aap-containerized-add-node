# REQ-001: Additive Node Join

## Status

Implemented

## Parent

[AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069): "Support adding/joining execution nodes to an existing mesh post-install"

## Phase

[PHASE-001](../phases/PHASE-001-initial-collection.md)

---

## Requirement

Add execution nodes and hop nodes to an existing containerized AAP cluster **without re-running the full installer**.

## Rationale

Full installer runs cause:
- Maintenance windows (controller/gateway/hub restart)
- Risk to existing workloads
- Unnecessary reconfiguration of unchanged nodes

Day-2 node addition should be additive, touching only new nodes.

## Acceptance Criteria

- [ ] Playbook adds nodes without touching existing platform components
- [ ] Controller, Gateway, Hub, EDA containers not restarted
- [ ] Existing mesh connections remain stable
- [ ] Only new nodes receive configuration changes
- [ ] `awx-manage list_instances` shows new nodes with heartbeat
- [ ] Playbook is idempotent (re-run safe)

## Implementation

| Artifact | Description |
|----------|-------------|
| `playbooks/add_node.yml` | Main playbook |
| `roles/discover_new_nodes/` | Diff inventory vs list_instances |
| `roles/register_instance/` | awx-manage provision_instance |
| `roles/install_receptor_node/` | Receptor install on new nodes only |

## Verification

See [TEST.md](../../TEST.md) scenarios T01-T06.

## Related

- ADR-004: Installer Role Reuse
- ADR-005: Preflight as Opt-Out
