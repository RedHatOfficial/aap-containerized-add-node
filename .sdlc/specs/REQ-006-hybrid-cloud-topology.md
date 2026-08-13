# REQ-006: Hybrid Cloud Topology Support

## Status

Approved

## Parent

[AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069)

## Phase

[PHASE-001](../phases/PHASE-001-outbound-dial.md)

---

## Requirement

Support hybrid cloud deployments where AAP controller runs in cloud (GCP/AWS/Azure) and execution nodes run on-premises, with firewall rules allowing only outbound connections from on-prem to cloud.

## Scenario

```
┌──────────────────────────────────────────────┐
│                    CLOUD                      │
│  Controller ◄── outbound dial ──┐            │
│  [listener]                     │            │
└─────────────────────────────────│────────────┘
                                  │
          ═══════ FIREWALL: on-prem → cloud ONLY ═══════
                                  │
┌─────────────────────────────────│────────────┐
│                  ON-PREM        │            │
│                          ┌─────┴─────┐      │
│               ┌─────────►│    Hop    │      │
│               │          │[dials out]│      │
│               │          └───────────┘      │
│        ┌──────┴──────┐                      │
│        │     EN      │                      │
│        └─────────────┘                      │
└─────────────────────────────────────────────┘
```

## Rationale

Common enterprise pattern:
- Cloud-first strategy with AAP centralized in cloud
- Legacy workloads and sensitive systems remain on-premises
- Security policy restricts inbound connections to on-prem networks
- Execution nodes must "pull" work from cloud controller

This topology is fully supported using Pattern 1 (outbound dial) — the default and recommended approach.

## Acceptance Criteria

- [x] On-prem ENs can peer to cloud controller via `receptor_peers`
- [x] Hop nodes can relay through DMZ/network boundaries
- [x] Controller requires no outbound connectivity to on-prem
- [x] Example inventory documented
- [x] Firewall requirements documented

## Constraints

1. **SSH access required at install time** — installer must reach all nodes
2. **DNS/routing required** — on-prem nodes must resolve cloud controller FQDN
3. **Port 27199** — must be open from on-prem to cloud controller

## Installation Options

| Method | SSH Requirement | Use Case |
|--------|-----------------|----------|
| Online (default) | Temporary SSH from installer to all nodes | Standard deployments, VPN/bastion available |
| Offline bundle (REQ-005) | SSH to controller only, manual transfer to ENs | No SSH to on-prem ENs allowed |

### No-SSH Path (Offline Bundle)

For environments where SSH from installer to on-prem ENs is not possible:

1. **Generate bundle** — run on control host (SSH to controller only)
2. **Transfer bundle** — via approved channel (USB, secure file transfer)
3. **Execute locally** — run on EN with `ansible-playbook -c local`

See [REQ-005](REQ-005-offline-bundle.md) and [PHASE-002](../phases/PHASE-002-offline-bundle.md) for offline bundle implementation.

## Documentation

| Artifact | Description |
|----------|-------------|
| `docs/TOPOLOGY.md` Example 7 | Hybrid cloud topology with diagram |
| `examples/inventory-hybrid-cloud.yml` | Copy-paste ready inventory |
| `README.md` topology picker | Quick reference entry |

## Related

- REQ-005: Offline Join Bundle (for no-SSH scenarios)
- REQ-003: Bidirectional Peering (inbound dial option)
- DR-001: Ansible Automation Only
