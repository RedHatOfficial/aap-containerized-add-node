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

## For AI Agent Contributors

**All AI agents MUST use the skills in `.agents/skills/` for SDLC tasks.**

| Task | Invoke |
|------|--------|
| Check status | `/sdlc-status` |
| What to do next | `/workflow` |
| New requirement | `/req-new` |
| Capture question | `/dr-new` |
| Resolve decision | `/dr-review` |
| Architecture decision | `/adr-new` |

Skills ensure consistency. Do not bypass them by guessing implementation.

## Coverage Matrix

| AAPRFE-3069 Requirement | Status | REQ | Phase |
|-------------------------|--------|-----|-------|
| Add EN to existing mesh post-install | Implemented | REQ-001 | PHASE-001 |
| No full installer re-run | Implemented | REQ-001 | PHASE-001 |
| Hop node support | Implemented | REQ-002 | PHASE-001 |
| Execution node support | Implemented | REQ-002 | PHASE-001 |
| Outbound-only mode (EN → Controller) | Implemented | REQ-003 | PHASE-001 |
| Inbound mode (Controller → EN) | Implemented | REQ-003 | PHASE-001 |
| AAP 2.6+ support | Implemented | REQ-004 | PHASE-001 |
| RHEL 9 nodes | Implemented | REQ-004 | PHASE-001 |
| RHEL 10 nodes | Implemented | REQ-004 | PHASE-001 |
| Self-contained "join bundle" | Open | REQ-005 | PHASE-002 |
| UI-driven workflow | Not Implementing | — | ADR-001 |
| CLI "add node" command | Not Implementing | — | ADR-001 |

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| [adrs/](adrs/) | Architecture Decision Records |
| [specs/](specs/) | Requirements specifications |
| [phases/](phases/) | Development phases |
| [decisions/](decisions/) | Open and closed decision requests |
| [testing/](testing/) | Test plans, scenarios, checklists |
| [research/](research/) | Background research |
| [context/](context/) | Supporting documentation references |
| [templates/](templates/) | Document templates |

## Phases

| Phase | Title | Status |
|-------|-------|--------|
| [PHASE-001](phases/PHASE-001-initial-collection.md) | Initial Collection | Complete |
| [PHASE-002](phases/PHASE-002-offline-bundle.md) | Offline Bundle | Planned |
| [PHASE-003](phases/PHASE-003-upstream-migration.md) | Upstream Migration | Future |

## Requirements

| REQ | Title | Status | Phase |
|-----|-------|--------|-------|
| [REQ-001](specs/REQ-001-additive-node-join.md) | Additive Node Join | Implemented | PHASE-001 |
| [REQ-002](specs/REQ-002-hop-and-execution-nodes.md) | Hop and Execution Node Support | Implemented | PHASE-001 |
| [REQ-003](specs/REQ-003-bidirectional-peering.md) | Bidirectional Peering | Implemented | PHASE-001 |
| [REQ-004](specs/REQ-004-platform-compatibility.md) | Platform Compatibility | Implemented | PHASE-001 |
| [REQ-005](specs/REQ-005-offline-bundle.md) | Offline Join Bundle | Open | PHASE-002 |

## ADRs (Architecture Decisions)

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](adrs/ADR-001-cli-first-approach.md) | Ansible Automation Only | Accepted |
| [ADR-002](adrs/ADR-002-serial-registration.md) | Serial Registration | Accepted |
| [ADR-003](adrs/ADR-003-outbound-first-topology.md) | Outbound-First Topology | Accepted |
| [ADR-004](adrs/ADR-004-installer-role-reuse.md) | Installer Role Reuse | Accepted |
| [ADR-005](adrs/ADR-005-preflight-opt-out.md) | Preflight as Opt-Out | Accepted |

## Open DRs (Need Input)

None

## Closed DRs

| DR | Title | Outcome |
|----|-------|---------|
| [DR-001](decisions/closed/DR-001-offline-join-bundle.md) | Offline Join Bundle | Implement (PHASE-002) |
| [DR-002](decisions/closed/DR-002-controller-ui-integration.md) | Controller UI Integration | Not Implementing |
| [DR-003](decisions/closed/DR-003-awx-cli-integration.md) | awx-cli Integration | Not Implementing |
