# SDLC Framework

Spec-Driven Development artifacts for AAP Containerized Add Node collection.

## RFE Alignment

This collection addresses [AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069): "Support adding/joining execution nodes to an existing mesh post-install"

## Design Philosophy

**Ansible automation is the interface.** No UI. No separate CLI.

This is a deliberate design choice (ADR-001):
- Minimizes administrative tasks through automation
- Enables integration with existing pipelines
- Avoids duplication between UI/CLI/automation
- Matches how customers deploy at scale

## Coverage Matrix

| AAPRFE-3069 Requirement | Status | Notes |
|-------------------------|--------|-------|
| Add EN to existing mesh post-install | Implemented | Core functionality |
| No full installer re-run | Implemented | Only new nodes touched |
| Outbound-only mode (EN → Controller) | Implemented | Default, zero disruption |
| Inbound mode (Controller → EN) | Implemented | Optional |
| Node-initiated peering | Implemented | `receptor_peers` |
| Wrap awx-manage provision_instance | Implemented | `register_instance` role |
| Correct status reporting | Implemented | `verify_mesh` role |
| Scriptable/automatable | Implemented | Ansible collection |
| Self-contained "join bundle" | Open | DR-001 |
| UI-driven workflow | Not Implementing | ADR-001 |
| CLI "add node" command | Not Implementing | ADR-001 |

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| `adrs/` | Architecture Decision Records |
| `decisions/open/` | Open decision requests |
| `decisions/closed/` | Resolved decisions |
| `templates/` | Document templates |

## Decisions Summary

### ADRs (Architecture Decisions)

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](adrs/ADR-001-cli-first-approach.md) | Ansible Automation Only | Accepted |
| [ADR-002](adrs/ADR-002-serial-registration.md) | Serial Registration | Accepted |
| [ADR-003](adrs/ADR-003-outbound-first-topology.md) | Outbound-First Topology | Accepted |
| [ADR-004](adrs/ADR-004-installer-role-reuse.md) | Installer Role Reuse | Accepted |
| [ADR-005](adrs/ADR-005-preflight-opt-out.md) | Preflight as Opt-Out | Accepted |

### Open DRs (Need Input)

| DR | Title | Priority |
|----|-------|----------|
| [DR-001](decisions/open/DR-001-offline-join-bundle.md) | Offline Join Bundle | High |

### Closed DRs

| DR | Title | Outcome |
|----|-------|---------|
| [DR-002](decisions/closed/DR-002-controller-ui-integration.md) | Controller UI Integration | Not Implementing |
| [DR-003](decisions/closed/DR-003-awx-cli-integration.md) | awx-cli Integration | Not Implementing |
