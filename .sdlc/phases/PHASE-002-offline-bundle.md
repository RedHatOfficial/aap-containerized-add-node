# PHASE-002: Offline Bundle

## Status

Ready

## Timeline

- **Target Start**: TBD
- **Target Complete**: TBD

---

## Objective

Support air-gapped environments where control host cannot SSH to execution nodes.

## Requirements Addressed

| REQ | Title | Status |
|-----|-------|--------|
| [REQ-005](../specs/REQ-005-offline-bundle.md) | Offline Join Bundle | Approved |

## Decision

[DR-001: Offline Join Bundle](../decisions/closed/DR-001-offline-join-bundle.md) — **Decided: Implement**

Constraints:
- No API/UI/platform changes — collection only
- Same approach as online — reuse existing roles
- Self-contained — bundle includes everything needed
- Fully documented — clear offline prerequisites

## Proposed Deliverables

| Artifact | Description |
|----------|-------------|
| `playbooks/generate_bundle.yml` | Bundle generation playbook |
| `roles/generate_bundle/` | Bundle assembly role |
| `docs/OFFLINE.md` | Air-gapped installation guide |

## Workflow

```
Phase 1: Generate (control host)
┌─────────────────────────────────────────────┐
│ ansible-playbook generate_bundle.yml        │
│   - SSH to controller (fetch CA, keys)      │
│   - Pre-mint TLS certs for target node      │
│   - Create self-contained archive           │
└─────────────────────────────────────────────┘
                    │
                    ▼
            [Transfer bundle via approved channel]
                    │
                    ▼
Phase 2: Execute (on EN, locally)
┌─────────────────────────────────────────────┐
│ ansible-playbook -c local install.yml       │
│   - Install receptor from bundle            │
│   - Configure TLS from pre-minted certs     │
│   - Start receptor service                  │
└─────────────────────────────────────────────┘
```

## Dependencies

- PHASE-001 complete
- DR-001 decided

## Next Phase

[PHASE-003: Upstream Migration](PHASE-003-upstream-migration.md)
