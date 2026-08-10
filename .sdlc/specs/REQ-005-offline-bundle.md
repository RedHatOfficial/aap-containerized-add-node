# REQ-005: Offline Join Bundle

## Status

Open

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

## Open Questions

See [DR-001](../decisions/open/DR-001-offline-join-bundle.md):
- Security review of TLS key handling
- Customer validation of two-phase workflow
- Bundle size with/without images

## Implementation

TBD — awaiting DR-001 decision.

## Related

- DR-001: Offline Join Bundle
- ADR-001: Ansible Automation Only (bundle generation = another playbook)
