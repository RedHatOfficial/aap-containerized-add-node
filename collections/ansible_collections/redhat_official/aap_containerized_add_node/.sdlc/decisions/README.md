# Decision Requests

Questions and decisions requiring input before implementation.

## Open Decisions

None

## Closed Decisions

| DR | Title | Outcome |
|----|-------|---------|
| [DR-001](closed/DR-001-offline-join-bundle.md) | Offline Join Bundle | Implement (PHASE-002) |
| [DR-002](closed/DR-002-controller-ui-integration.md) | Controller UI Integration | Not Implementing (ADR-001) |
| [DR-003](closed/DR-003-awx-cli-integration.md) | awx-cli Integration | Not Implementing (ADR-001) |

## Creating a New DR

1. Copy `../templates/decision-request.md`
2. Number sequentially: `DR-004-title.md`
3. Place in `open/` directory
4. Fill in question, context, options
5. When decided, move to `closed/` and update status

## DR Lifecycle

```
Open → Under Review → Decided | Deferred
                   ↓
              (may create ADR)
```
