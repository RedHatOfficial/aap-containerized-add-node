# AAP Containerized Add Node Collection

## Project Constitution

This document is the authoritative source of truth for AI agents. All development must align with these principles.

## Overview

Ansible collection for adding execution nodes and hop nodes to existing containerized AAP 2.6+ clusters without re-running the full installer.

**Collection:** `redhat_official.aap_containerized_add_node`

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Installer Host                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ansible-playbook playbooks/add_node.yml                 │   │
│  │    -i inventory -e aap_setup_dir=/path/to/setup          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │ SSH                              │ SSH
         ▼                                  ▼
┌─────────────────────┐          ┌─────────────────────┐
│  automationcontroller│          │  New Execution Node │
│  - awx-manage        │          │  - receptor install │
│  - mesh CA fetch     │          │  - TLS certs        │
│  - list_instances    │          │  - dial to mesh     │
└─────────────────────┘          └─────────────────────┘
```

## Key ADRs

| ADR | Decision |
|-----|----------|
| [ADR-001](.sdlc/adrs/ADR-001-cli-first-approach.md) | Ansible Automation Only — no UI, no separate CLI |
| [ADR-002](.sdlc/adrs/ADR-002-serial-registration.md) | Serial registration with `serial: 1` |
| [ADR-003](.sdlc/adrs/ADR-003-outbound-first-topology.md) | Outbound dial (EN → Controller) default |
| [ADR-004](.sdlc/adrs/ADR-004-installer-role-reuse.md) | Reuse installer roles via `aap_setup_dir` |
| [ADR-005](.sdlc/adrs/ADR-005-preflight-opt-out.md) | Preflight enabled by default |

Full list: `.sdlc/adrs/README.md`

## Spec-Driven Development

All features follow: **Spec First → DR for Questions → ADR for Decisions → Traceability**

| Skill | Purpose |
|-------|---------|
| `/sdlc-status` | Dashboard: REQ/DR/ADR status and blockers |
| `/req-new` | Create requirement spec |
| `/dr-new` | Capture blocking question |
| `/dr-review` | Resolve decision request |
| `/adr-new` | Document architectural decision |

Full workflow: `.agents/skills/workflow/SKILL.md`

## Agent Constraints

- **Follow ADRs** — no deviation without a new ADR
- **ansible-lint must pass** — run before committing
- **Non-root execution** — collection rejects root user
- **Installer inventory format** — match `ansible.containerized_installer`
- **receptor_peers is a list** — never a bare string
- **Outbound dial default** — inbound dial requires explicit opt-in
- Do NOT modify files outside task scope
- Do NOT add features not in requirements
- Ask for clarification if specs are ambiguous

## Quality Gates

Before completing any task:
- [ ] `ansible-lint` passes
- [ ] `ansible-playbook --syntax-check` passes
- [ ] Documentation updated (if applicable)
- [ ] ADR added (if architectural decision)

## Supported Platforms

| Platform | Status |
|----------|--------|
| Containerized AAP 2.6+ | Supported |
| Containerized AAP 2.7+ | Supported |
| RHEL 9.x nodes | Tested |
| RHEL 10.x nodes | Tested |

## Not Supported

- RPM installs (different installer mechanics)
- OpenShift / Operator (out of scope)
- AAP 2.4 and earlier (pre-gateway architecture)

## References

- [README.md](README.md) — Quick start and usage
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System architecture
- [docs/TOPOLOGY.md](docs/TOPOLOGY.md) — Mesh topology patterns
- [.sdlc/README.md](.sdlc/README.md) — SDLC framework
- [CONTRIBUTING.md](CONTRIBUTING.md) — Development workflow
