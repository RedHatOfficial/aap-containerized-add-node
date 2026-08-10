# PHASE-003: Upstream Migration

## Status

Future

## Timeline

Target: AAP 2.7 GA + 1

---

## Objective

Migrate collection functionality into upstream `ansible.containerized_installer`.

## Rationale

This collection is a **reference implementation**. Long-term home is the official installer:
- Single source of truth
- Product-supported
- Included in AAP releases

## Approach

See [INSTALLER_PLAN.md](../../INSTALLER_PLAN.md) for detailed migration plan.

Summary:
1. Add `add_execution_nodes.yml` playbook to installer
2. Extract `register_execution_nodes.yml` task file
3. Reuse existing installer roles (receptor, common)

## Targets

| AAP Version | Priority | Status |
|-------------|----------|--------|
| 2.7 | First | Planned |
| 2.6 | Backport | After 2.7 |
| 2.5 | Out of scope | — |

## Deliverables

| Artifact | Destination |
|----------|-------------|
| `add_execution_nodes.yml` | `ansible.containerized_installer/playbooks/` |
| `add_execution_nodes/` role | `ansible.containerized_installer/roles/` |
| `register_execution_nodes.yml` | `ansible.containerized_installer/roles/automationcontroller/tasks/` |

## Prerequisites

- PHASE-001 validated in production
- PHASE-002 complete (if approved)
- Upstream maintainer buy-in

## Working Tree

[installer-overlay/](../../installer-overlay/) contains drop-in files for testing migration.

## Dependencies

- PHASE-001 complete
- PHASE-002 complete or deferred
