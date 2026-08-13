# Context Documents

Supporting documentation for SDLC decisions. User-facing docs remain in `docs/`.

## Architecture References

| Document | Location | Purpose |
|----------|----------|---------|
| [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) | docs/ | System architecture, goals, non-goals |
| [TOPOLOGY.md](../../docs/TOPOLOGY.md) | docs/ | Mesh topology patterns |
| [CONVENTIONS.md](../../docs/CONVENTIONS.md) | docs/ | Variable naming, inventory format |
| [COLLECTION_MAP.md](../../docs/COLLECTION_MAP.md) | docs/ | Role and playbook flow |

## Installer context

| Document | Location | Purpose |
|----------|----------|---------|
| [INSTALLER_PLAN.md](../../INSTALLER_PLAN.md) | root | **Agent-maintained** porting spec for `ansible.containerized_installer.add_execution_nodes` |

Implementation reference: this collection (`playbooks/add_node.yml`, `roles/*`). Do not depend on
vendored installer snapshots in this repo.

## SDLC Cross-References

| Document | Purpose |
|----------|---------|
| [../specs/](../specs/) | Requirements specifications |
| [../research/](../research/) | Research and analysis |
| [../phases/](../phases/) | Development phases |
