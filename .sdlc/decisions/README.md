# Decision Requests

Questions and decisions requiring input before implementation.

## Open Decisions

| DR | Title | Priority | Category |
|----|-------|----------|----------|
| [DR-001](open/DR-001-offline-join-bundle.md) | Offline Join Bundle | High | Architecture |
| [DR-002](open/DR-002-controller-ui-integration.md) | Controller UI Integration | Medium | Product |
| [DR-003](open/DR-003-awx-cli-integration.md) | awx-cli Integration | Medium | Architecture |

## Closed Decisions

None yet.

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
