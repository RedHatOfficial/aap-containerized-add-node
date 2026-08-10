# Test Scenarios

Lab test scenarios for validating the collection.

## Scenario Index

| ID | Name | Topology | Priority | Status |
|----|------|----------|----------|--------|
| [S-001](S-001-single-en.md) | Single Execution Node | AIO + EN | P1 | Tested |
| [S-002](S-002-single-hop.md) | Single Hop Node | AIO + HN | P1 | Tested |
| [S-003](S-003-multi-hop.md) | Multi-Hop Topology | AIO + HN + EN | P1 | Tested |
| [S-010](S-010-inbound-dial.md) | Inbound Dial | AIO + EN (inbound) | P2 | Untested |
| [S-020](S-020-preflight-validation.md) | Preflight Validation | Any | P1 | Tested |
| [S-030](S-030-parallel-nodes.md) | Parallel Node Addition | AIO + 2 EN | P1 | Tested |
| [S-040](S-040-failure-recovery.md) | Failure and Recovery | Any | P1 | Tested |
| [S-041](S-041-deprovision-rejoin.md) | Deprovision and Rejoin | Any | P1 | Tested |
| [S-050](S-050-upgrade-after-join.md) | Full Upgrade After Join | Any | P2 | Tested |

## Creating a New Scenario

1. Copy `../.sdlc/templates/test-scenario.md`
2. Number sequentially: `S-NNN-name.md`
3. Fill in all sections
4. Update this index

## Running Scenarios

1. Set up lab environment per scenario prerequisites
2. Follow "Steps" section exactly
3. Verify against "Pass Criteria"
4. Record result in scenario's "Results Log"
5. Update this index status

## Priority Definitions

| Priority | Meaning | When to Test |
|----------|---------|--------------|
| P1 | Core functionality | Every release |
| P2 | Important features | Major releases |
| P3 | Edge cases | As needed |
