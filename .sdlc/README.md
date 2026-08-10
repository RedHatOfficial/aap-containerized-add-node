# SDLC Framework

Spec-Driven Development artifacts for AAP Containerized Add Node collection.

## RFE Alignment

This collection addresses [AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069): "Support adding/joining execution nodes to an existing mesh post-install"

## Coverage Matrix

| AAPRFE-3069 Requirement | Status | Artifact |
|-------------------------|--------|----------|
| Add EN to existing mesh post-install | Implemented | - |
| No full installer re-run | Implemented | - |
| Outbound-only mode (EN → Controller) | Implemented | - |
| Inbound mode (Controller → EN) | Implemented | - |
| Node-initiated peering | Implemented | - |
| Wrap awx-manage provision_instance | Implemented | - |
| Correct status reporting | Implemented | - |
| Scriptable/automatable | Implemented | - |
| Self-contained "join bundle" | Gap | DR-001 |
| UI-driven workflow | Gap | DR-002 |
| CLI "add node" command | Gap | DR-003 |
| Controller generates bundle from UI | Gap | DR-002 |

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| `adrs/` | Architecture Decision Records |
| `decisions/open/` | Open decision requests (gaps, questions) |
| `decisions/closed/` | Resolved decisions |
| `context/` | Project knowledge (architecture, conventions) |
| `research/` | Investigation documents |
| `templates/` | Document templates |

## Open Decisions

| DR | Title | Priority | Category |
|----|-------|----------|----------|
| DR-001 | Offline Join Bundle | High | Architecture |
| DR-002 | Controller UI Integration | Medium | Product |
| DR-003 | awx-cli Integration | Medium | Architecture |

## ADRs

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | CLI-First Approach | Accepted |

## Quick Reference

- `/sdlc-status` — View current state
- `/dr-new` — Raise a new question
- `/adr-new` — Document a decision
