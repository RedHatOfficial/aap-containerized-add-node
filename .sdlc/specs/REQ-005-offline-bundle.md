# REQ-005: Offline Join Bundle

## Status

Approved

## Parent

[AAPRFE-3069](https://redhat.atlassian.net/browse/AAPRFE-3069)

## Phase

[PHASE-002](../phases/PHASE-002-offline-bundle.md)

---

## Requirement

Generate self-contained "join bundle" for air-gapped execution node provisioning.

## Rationale

Some environments cannot allow SSH from installer host to execution nodes due to:
- Security policy (egress-only networks)
- Compliance requirements
- Network segmentation

Bundle enables two-phase join:
1. Generate bundle on installer host (SSH to controller only)
2. Transfer and execute on EN (no inbound SSH required)

## Acceptance Criteria

- [ ] `playbooks/generate_bundle.yml` creates self-contained archive
- [ ] Bundle contains pre-minted TLS certificates
- [ ] Bundle contains receptor.conf template
- [ ] Bundle contains install playbook for local execution
- [ ] Optional: Bundle includes receptor container image
- [ ] Bundle can be audited before execution
- [ ] Documentation covers secure handling of credentials in bundle

## Constraints (from DR-001)

Per DR-001 decision:
1. **No API/UI/platform changes** — collection only
2. **Same approach as online** — reuse existing roles
3. **Self-contained** — bundle includes everything needed
4. **Fully documented** — clear offline prerequisites

## Implementation

| Artifact | Description |
|----------|-------------|
| `playbooks/generate_bundle.yml` | Generate bundle (SSH to controller only) |
| `playbooks/install_from_bundle.yml` | Install locally on EN (no SSH) |
| `roles/generate_bundle/` | Bundle assembly role |
| `docs/OFFLINE.md` | Air-gapped installation guide |

## Related

- DR-001: Offline Join Bundle
- ADR-001: Ansible Automation Only (bundle generation = another playbook)
